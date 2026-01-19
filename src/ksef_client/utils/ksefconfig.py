#
# http://generatory.it/
#
import os
import sys
import json
import base64
import configparser

from cryptography import x509
from pathlib import Path

class Config(configparser.ConfigParser):
    def __init__(self, firma:int=1, osoba:bool=False, initialize:bool=False):
        super().__init__()
        
        # Get project root (2 levels up from src/ksef_client/utils)
        self.project_root = Path(__file__).parent.parent.parent.parent.absolute()
        self.config_dir = self.project_root / 'config'
        self.storage_dir = self.project_root / 'storage'
        self.resources_dir = self.project_root / 'resources'
        
        # New structured storage paths
        self.sent_dir = self.storage_dir / 'sent'
        self.received_dir = self.storage_dir / 'received'
        self.reports_dir = self.storage_dir / 'reports'
        
        # Ensure directories exist
        dirs_to_create = [
            self.config_dir, self.storage_dir, self.resources_dir,
            self.sent_dir / 'xml', self.sent_dir / 'upo', self.sent_dir / 'viz',
            self.received_dir / 'xml', self.received_dir / 'viz',
            self.reports_dir
        ]
        for d in dirs_to_create:
            d.mkdir(parents=True, exist_ok=True)
            # Create .gitkeep in each leaf directory
            if not any(item for item in d.iterdir() if item.name != '.gitkeep'):
                (d / '.gitkeep').touch()
                
        ini_path = self.config_dir / 'ksef.ini'
        self.read(ini_path)

        self.firma = firma
        self.osoba = osoba
        self.version = self.get('ksef', 'version', fallback='test')
        self.proxy_enabled = self.getboolean('ksef', 'proxy_enabled', fallback=False)
        self.url = self.get(self.version, 'url')
        self.kseftoken = self.get(f'firma{firma}', 'token', fallback=None)

        self.nip = self.get(f'firma{firma}', 'nip')
        self.nazwa = self.get(f'firma{firma}', 'nazwa')
        self.adres = self.get(f'firma{firma}', 'adres')

        self.pesel = self.get(f'firma{firma}', 'pesel')
        self.imie = self.get(f'firma{firma}', 'imie')
        self.nazwisko = self.get(f'firma{firma}', 'nazwisko')

        self.prefix = self.pesel if self.osoba else self.nip
        self.prefix_full = os.path.join(self.config_dir, self.prefix)

        self.reload_certificates()

        if not initialize:
            assert self.nip and self.pesel

    def reload_certificates(self):
        """Wymusza ponowne wczytanie certyfikatów z dysku do pamięci."""
        cert_file = os.path.join(self.config_dir, f'certificates-{self.version}.json')
        if os.path.exists(cert_file):
            with open(cert_file, 'rt', encoding="utf-8") as fp:
                try:
                    data = json.loads(fp.read())
                    if isinstance(data, dict) and 'keys' in data:
                        self.certificates = data['keys']
                    elif isinstance(data, list):
                        self.certificates = data
                    else: 
                        self.certificates = []
                except json.JSONDecodeError:
                    self.certificates = []
        else:
            self.certificates = []

    @property
    def sent_xml(self): return self.sent_dir / 'xml'
    @property
    def sent_upo(self): return self.sent_dir / 'upo'
    @property
    def sent_viz(self): return self.sent_dir / 'viz'
    @property
    def received_xml(self): return self.received_dir / 'xml'
    @property
    def received_viz(self): return self.received_dir / 'viz'
    @property
    def reports(self): return self.reports_dir

    def loadcertificate(self, cert_data):
        from cryptography.hazmat.primitives import serialization
        cert_bytes = base64.b64decode(cert_data)
        try:
            # Try loading as X.509 Certificate (DER)
            certificate = x509.load_der_x509_certificate(cert_bytes)
            public_key = certificate.public_key()
            return certificate, public_key
        except Exception:
            try:
                # Try loading as PEM Public Key
                 from cryptography.hazmat.primitives.serialization import load_pem_public_key
                 public_key = load_pem_public_key(cert_bytes)
                 return None, public_key
            except Exception as e:
                # If both fail, re-raise
                raise ValueError(f"Failed to load certificate/key: {str(e)}")

    def getcertificte(self, token=True):
        for cert in self.certificates:
            if token:
                if 'KsefTokenEncryption' in cert['usage']:
                    return self.loadcertificate(cert['certificate'])
            elif 'SymmetricKeyEncryption' in cert['usage']:
                return self.loadcertificate(cert['certificate'])
        return None, None
