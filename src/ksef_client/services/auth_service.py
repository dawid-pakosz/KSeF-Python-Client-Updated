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

        # 2. Pobierz Challenge (API v2)
        # UWAGA: Moja diagnostyka wykazała, że Demo wymaga pustego obiektu JSON {} 
        # Brak body lub pełne body z NIP-em zwraca błąd 400.
        challenge_url = f"{self.cfg.url}/auth/challenge"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "KSeF-Python-Client/1.0"
        }
        
        resp = requests.post(challenge_url, json={}, headers=headers, timeout=15)
        
        if resp.status_code not in [200, 201]:
            raise Exception(f"Błąd Challenge ({resp.status_code}): {resp.text}")
        
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

        # 4. Uwierzytelnienie (InitToken - v2)
        body = {
            "challenge": challenge,
            "contextIdentifier": {
                "type": "Nip",
                "value": self.cfg.nip
            },
            "encryptedToken": base64.b64encode(encrypted_token).decode()
        }

        # W API v2: /auth/ksef-token
        resp = requests.post(f"{self.cfg.url}/auth/ksef-token", json=body, headers=headers, timeout=15)
        if resp.status_code not in [201, 202]:
            raise Exception(f"Błąd InitToken ({resp.status_code}): {resp.text}")
        
        login_data = resp.json()
        ref_no = login_data['referenceNumber']
        auth_token = login_data['authenticationToken']['token']

        # 5. Oczekiwanie na potwierdzenie (Polling)
        headers = {"Authorization": f"Bearer {auth_token}"}
        status = 100
        while status < 200:
            time.sleep(1)
            # Poprawny URL pollingu dla v2: /auth/{referenceNumber}
            resp = requests.get(f"{self.cfg.url}/auth/{ref_no}", headers=headers, timeout=10)
            if resp.status_code != 200:
                raise Exception(f"Błąd sprawdzania statusu logowania ({resp.status_code}): {resp.text}")
            status_data = resp.json()
            status = status_data['status']['code']
            if status >= 300:
                raise Exception(f"Logowanie odrzucone: {status_data['status']['description']}")

        # 6. Redeem (odebranie finalnego tokena sesji)
        resp = requests.post(f"{self.cfg.url}/auth/token/redeem", headers=headers, timeout=15)
        if resp.status_code != 200:
            raise Exception(f"Błąd Redeem ({resp.status_code}): {resp.text}")
        
        final_auth = resp.json()
        with open(self.auth_file, 'wt', encoding="utf-8") as fp:
            fp.write(json.dumps(final_auth))
        
        return final_auth

    def refresh_token(self):
        if not os.path.exists(self.auth_file):
            raise FileNotFoundError(f"Plik uwierzytelnienia nie istnieje: {self.auth_file}. Użyj najpierw 'login'.")

        with open(self.auth_file, 'rt') as fp:
            auth = json.loads(fp.read())

        resp = requests.post(
            f"{self.cfg.url}/auth/token/refresh",
            headers={
                "Authorization": f"Bearer {auth['refreshToken']['token']}",
            },
            timeout=10
        )

        if resp.status_code == 200:
            data = resp.json()
            # In API v2, refresh usually returns a new accessToken object
            if "accessToken" in data:
                auth["accessToken"] = data["accessToken"]
            else:
                # Fallback if the whole response is the token object
                auth["accessToken"] = data
            
            with open(self.auth_file, 'wt', encoding="utf-8") as fp:
                fp.write(json.dumps(auth))
            return auth
        else:
            raise Exception(f"Nie udało się odświeżyć tokena: {resp.status_code} - {resp.text}")

    def get_access_token(self):
        if not os.path.exists(self.auth_file):
            return None
        with open(self.auth_file, 'rt', encoding="utf-8") as fp:
            auth = json.loads(fp.read())
            return auth.get("accessToken", {}).get("token")

    def fetch_certificates(self):
        """Pobiera oficjalne certyfikaty publiczne z serwerów Ministerstwa Finansów (API)."""
        print(f">>> Pobieranie oficjalnych certyfikatów dla środowiska: {self.cfg.version}...")
        
        # Używamy endpointu API, który jest bardziej stabilny niż pliki webowe
        # self.cfg.url zawiera już '/v2', więc doklejamy tylko resztę ścieżki
        cert_url = f"{self.cfg.url}/security/public-key-certificates"

        try:
            resp = requests.get(cert_url, timeout=15)
            if resp.status_code != 200:
                raise Exception(f"Serwer MF zwrócił status {resp.status_code}")
            
            # Zapisujemy odpowiedź JSON w folderze config/
            cert_file = os.path.join(self.cfg.config_dir, f'certificates-{self.cfg.version}.json')
            with open(cert_file, 'wt', encoding="utf-8") as fp:
                fp.write(json.dumps(resp.json(), indent=2))
            
            print(f"[OK] Certyfikaty pobrane i zapisane w: {cert_file}")
            return True
        except Exception as e:
            print(f"[!] Nie udało się pobrać certyfikatów z {cert_url}: {e}")
            return False
