import json
import requests
import os
import base64
import time
import dateutil.parser
from cryptography.hazmat.primitives.asymmetric import rsa, padding as apadding
from cryptography.hazmat.primitives import hashes
from ..utils.ksefconfig import Config

class AuthService:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.auth_file = f"{cfg.prefix_full}-auth.json"

    def login(self):
        """Pełny proces logowania (uwierzytelnienie tokenem)."""
        if not self.cfg.kseftoken:
            raise Exception("Błąd: Brak tokena KSeF w ksef.ini dla tej firmy.")

        # 1. Pobierz certyfikat publiczny KSeF
        _, public_key = self.cfg.getcertificte(True)
        if not public_key:
             raise Exception("Błąd: Nie znaleziono certyfikatu publicznego KSeF w config/.")

        # 2. Pobierz Challenge
        resp = requests.post(f"{self.cfg.url}/api/v2/auth/challenge", timeout=10)
        
        if resp.status_code not in [200, 201]:
            raise Exception(f"Błąd Challenge: {resp.text}")
        
        challenge_data = resp.json()
        challenge = challenge_data['challenge']
        timestamp = challenge_data['timestamp']

        # 3. Przygotuj zaszyfrowany token
        dt = dateutil.parser.isoparse(timestamp)
        t = int(dt.timestamp() * 1000)
        token_str = f"{self.cfg.kseftoken}|{t}".encode('utf-8')

        encrypted_token = public_key.encrypt(
            token_str,
            apadding.OAEP(
                mgf=apadding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # 4. Uwierzytelnienie (InitToken)
        # Dla tokena KSeF zawsze używamy typu 'Nip' taxpayer-a
        body = {
            "challenge": challenge,
            "contextIdentifier": {
                "type": "Nip",
                "value": self.cfg.nip
            },
            "encryptedToken": base64.b64encode(encrypted_token).decode()
        }

        # W v2 endpoint to /api/v2/auth/ksef-token
        resp = requests.post(f"{self.cfg.url}/api/v2/auth/ksef-token", json=body, timeout=10)
        if resp.status_code not in [201, 202]:
            raise Exception(f"Błąd InitToken: {resp.text}")
        
        login_data = resp.json()
        ref_no = login_data['referenceNumber']
        auth_token = login_data['authenticationToken']['token']

        # 5. Oczekiwanie na potwierdzenie (Polling)
        headers = {"Authorization": f"Bearer {auth_token}"}
        status = 100
        while status < 200:
            time.sleep(1)
            # Poprawny URL pollingu to /api/v2/auth/{referenceNumber}
            resp = requests.get(f"{self.cfg.url}/api/v2/auth/{ref_no}", headers=headers, timeout=10)
            if resp.status_code != 200:
                raise Exception(f"Błąd sprawdzania statusu logowania ({resp.status_code}): {resp.text}")
            status_data = resp.json()
            status = status_data['status']['code']
            if status >= 300:
                raise Exception(f"Logowanie odrzucone: {status_data['status']['description']}")

        # 6. Redeem (odebranie finalnego tokena sesji)
        resp = requests.post(f"{self.cfg.url}/api/v2/auth/token/redeem", headers=headers, timeout=10)
        if resp.status_code != 200:
            raise Exception(f"Błąd Redeem: {resp.text}")
        
        final_auth = resp.json()
        with open(self.auth_file, 'wt') as fp:
            fp.write(json.dumps(final_auth))
        
        return final_auth

    def refresh_token(self):
        if not os.path.exists(self.auth_file):
            raise FileNotFoundError(f"Plik uwierzytelnienia nie istnieje: {self.auth_file}. Użyj najpierw 'login'.")

        with open(self.auth_file, 'rt') as fp:
            auth = json.loads(fp.read())

        resp = requests.post(
            f"{self.cfg.url}/api/v2/auth/token/refresh",
            headers={
                "Authorization": f"Bearer {auth['refreshToken']['token']}",
            },
            timeout=10
        )

        if resp.status_code == 200:
            data = resp.json()
            auth.update(data)
            with open(self.auth_file, 'wt') as fp:
                fp.write(json.dumps(auth))
            return auth
        else:
            raise Exception(f"Nie udało się odświeżyć tokena: {resp.status_code} - {resp.text}")

    def get_access_token(self):
        if not os.path.exists(self.auth_file):
            return None
        with open(self.auth_file, 'rt') as fp:
            auth = json.loads(fp.read())
            return auth.get("accessToken", {}).get("token")
