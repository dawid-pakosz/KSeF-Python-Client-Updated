#
# http://generatory.it/
#
import os
import sys
import json
import base64
import configparser

from cryptography import x509

class Config(configparser.ConfigParser):
    def __init__(self, firma:int=1, osoba:bool=False, initialize:bool=False):
        super().__init__()
        
        # Get project root (2 levels up from src/ksef_client/utils)
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        self.config_dir = os.path.join(self.project_root, 'config')
        self.storage_dir = os.path.join(self.project_root, 'storage')
        self.resources_dir = os.path.join(self.project_root, 'resources')
        
        ini_path = os.path.join(self.config_dir, 'ksef.ini')
        self.read(ini_path)

        self.firma = firma
        self.osoba = osoba
        self.version = self.get('ksef', 'version', fallback='test')
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

        cert_file = os.path.join(self.config_dir, f'certificates-{self.version}.json')
        if os.path.exists(cert_file):
            with open(cert_file, 'rt') as fp:
                self.certificates = json.loads(fp.read())
        else:
            self.certificates = []

        if not initialize:
            assert self.nip and self.pesel

    def loadcertificate(self, cert_data):
        cert_bytes = base64.b64decode(cert_data)
        certificate = x509.load_der_x509_certificate(cert_bytes)
        public_key = certificate.public_key()
        return certificate, public_key

    def getcertificte(self, token=True):
        for cert in self.certificates:
            if token:
                if 'KsefTokenEncryption' in cert['usage']:
                    return self.loadcertificate(cert['certificate'])
            elif 'SymmetricKeyEncryption' in cert['usage']:
                return self.loadcertificate(cert['certificate'])
        return None, None
