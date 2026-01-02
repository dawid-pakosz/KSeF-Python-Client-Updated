import json
import requests
import os
from ..utils.ksefconfig import Config

class AuthService:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.auth_file = f"{cfg.prefix_full}-auth.json"

    def refresh_token(self):
        if not os.path.exists(self.auth_file):
            raise FileNotFoundError(f"Authentication file not found: {self.auth_file}")

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
            raise Exception(f"Failed to refresh token: {resp.status_code} - {resp.text}")

    def get_access_token(self):
        if not os.path.exists(self.auth_file):
            return None
        with open(self.auth_file, 'rt') as fp:
            auth = json.loads(fp.read())
            return auth.get("accessToken", {}).get("token")
