import json
import os
import datetime
import hashlib
import base64
import requests
import dateutil.parser
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

from ..utils.ksefconfig import Config

class KSeFError(Exception):
    def __init__(self, msg, text=None):
        self.msg = msg
        self.text = text
        super().__init__(self.msg)

class InvoiceService:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.auth_file = f"{cfg.prefix_full}-auth.json"
        self.session_file = f"{cfg.prefix_full}-session.json"
        
        if not os.path.exists(self.auth_file):
            raise KSeFError(f"Missing auth file: {self.auth_file}")

        with open(self.auth_file, "rt") as fp:
            self.auth = json.loads(fp.read())

        self.access_token = self.auth["accessToken"]["token"]
        self.session = self._load_or_init_session()

    def _load_or_init_session(self):
        if os.path.exists(self.session_file):
            with open(self.session_file, "rt") as fp:
                session = json.loads(fp.read())
            
            dtnow = datetime.datetime.now(datetime.timezone.utc)
            dtdiff = datetime.timedelta(minutes=15)
            dt = dateutil.parser.isoparse(session['validUntil'])
            if dt < dtnow - dtdiff:
                session = None
        else:
            session = None

        if session is None:
            session = {
                'symmetric_key': base64.b64encode(os.urandom(32)).decode(),
                'iv': base64.b64encode(os.urandom(16)).decode(),
                'referenceNumber': None,
                'validUntil': None,
                'refs': {},
            }
        return session

    def session_save(self):
        with open(self.session_file, "wt", encoding="utf-8") as fp:
            fp.write(json.dumps(self.session))

    def session_open(self):
        _, public_key = self.cfg.getcertificte(False)
        assert isinstance(public_key, rsa.RSAPublicKey)

        encrypted_symmetric_key = public_key.encrypt(
            base64.b64decode(self.session['symmetric_key']),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        request_data = {
            "formCode": {
                "systemCode": "FA (3)",
                "schemaVersion": "1-0E",
                "value": "FA",
            },
            "encryption": {
                "encryptedSymmetricKey": base64.b64encode(encrypted_symmetric_key).decode(),
                "initializationVector": self.session['iv'],
            },
        }

        response = requests.post(
            f"{self.cfg.url}/api/v2/sessions/online",
            json=request_data,
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=30,
        )

        if response.status_code != 201:
            raise KSeFError('Error opening session.', response.text)

        data = response.json()
        self.session["referenceNumber"] = data["referenceNumber"]
        self.session["validUntil"] = data["validUntil"]
        self.session_save()
        return data["referenceNumber"]

    def session_close(self):
        ref = self.session.get("referenceNumber")
        if not ref:
            return

        requests.post(
            f'{self.cfg.url}/api/v2/sessions/online/{ref}/close',
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=15,
        )
        
        if os.path.exists(self.session_file):
            os.unlink(self.session_file)

    def _encrypt_invoice(self, invoice_bytes):
        cipher = Cipher(
            algorithms.AES(base64.b64decode(self.session['symmetric_key'])),
            modes.CBC(base64.b64decode(self.session['iv'])),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        pad = len(invoice_bytes) % 16
        if pad:
            padding_length = 16 - pad
            invoice_bytes += bytes([padding_length] * padding_length)

        return encryptor.update(invoice_bytes) + encryptor.finalize()

    def send_invoice(self, xml_path):
        if not self.session.get("referenceNumber"):
            raise KSeFError("Session not open")

        with open(xml_path, "rb") as f:
            invoice_xml = f.read()

        encrypted_invoice = self._encrypt_invoice(invoice_xml)
        invoice_hash = base64.b64encode(hashlib.sha256(invoice_xml).digest()).decode()
        enc_hash = base64.b64encode(hashlib.sha256(encrypted_invoice).digest()).decode()

        request_data = {
            "invoiceHash": invoice_hash,
            "invoiceSize": len(invoice_xml),
            "encryptedInvoiceHash": enc_hash,
            "encryptedInvoiceSize": len(encrypted_invoice),
            "encryptedInvoiceContent": base64.b64encode(encrypted_invoice).decode(),
            "offlineMode": False,
        }

        response = requests.post(
            f'{self.cfg.url}/api/v2/sessions/online/{self.session["referenceNumber"]}/invoices',
            json=request_data,
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=30,
        )

        if response.status_code != 202:
            raise KSeFError("Upload error", response.text)

        result = response.json()
        self.session['refs'][xml_path] = result["referenceNumber"]
        self.session_save()
        return result["referenceNumber"]

    def check_invoice_status(self, xml_path):
        invoice_ref = self.session['refs'].get(xml_path)
        if not invoice_ref: return None

        response = requests.get(
            f'{self.cfg.url}/api/v2/sessions/{self.session["referenceNumber"]}/invoices/{invoice_ref}',
            headers={"Authorization": f"Bearer {self.access_token}"},
            timeout=15,
        )

        if response.status_code == 200:
            data = response.json()
            if data['status']['code'] == 200:
                del self.session['refs'][xml_path]
                # Save reference info to sent/xml folder
                ref_file = self.cfg.sent_xml / f"{os.path.basename(xml_path)}.ref"
                with open(ref_file, 'wt', encoding="utf-8") as fp:
                    fp.write(json.dumps(data))
                self.session_save()
            return data
        return None

    def download_upo(self, xml_path):
        ref_file = self.cfg.sent_xml / f"{os.path.basename(xml_path)}.ref"
        if not os.path.exists(ref_file):
            # Try to get status first?
            data = self.check_invoice_status(xml_path)
            if not data or data['status']['code'] != 200:
                raise KSeFError("Invoice not accepted yet or missing reference.")
        else:
            with open(ref_file, 'rt', encoding="utf-8") as fp:
                data = json.loads(fp.read())

        upo_url = data.get('upoDownloadUrl')
        if not upo_url:
             response = requests.get(
                f'{self.cfg.url}/api/v2/sessions/{self.session["referenceNumber"]}/invoices/{data["ksefNumber"]}/upo',
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=15,
            )
        else:
            response = requests.get(upo_url)

        if response.status_code == 200:
            upo_path = self.cfg.sent_upo / f"{os.path.basename(xml_path)}.upo.xml"
            with open(upo_path, 'wt', encoding="utf-8") as fp:
                fp.write(response.text)
            return str(upo_path)
        return None
