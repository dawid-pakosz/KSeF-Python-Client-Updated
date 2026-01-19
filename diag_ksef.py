import requests
import json

url = "https://api-demo.ksef.mf.gov.pl/v2/auth/challenge"
nip = "1070002909"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

variants = [
    ("v2 Empty JSON (No UA)", "https://api-demo.ksef.mf.gov.pl/v2/auth/challenge", {}, {"Content-Type": "application/json", "Accept": "application/json"}),
    ("v2 Empty JSON (With UA)", "https://api-demo.ksef.mf.gov.pl/v2/auth/challenge", {}, {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "KSeF-Python-Client/1.0"}),
]

for name, url_variant, body, h in variants:
    print(f"Testing {name}...")
    try:
        resp = requests.post(url_variant, json=body, headers=h, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)
