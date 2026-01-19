import requests
import json
import os
import datetime
from typing import Optional, List, Dict
from ..utils.ksefconfig import Config
from .invoice_service import KSeFError

class QueryService:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.auth_file = f"{cfg.prefix_full}-auth.json"
        
        if not os.path.exists(self.auth_file):
            raise KSeFError(f"Missing auth file: {self.auth_file}")

        with open(self.auth_file, "rt", encoding="utf-8") as fp:
            self.auth = json.loads(fp.read())

        self.access_token = self.auth["accessToken"]["token"]

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def list_invoices(self, days: int = 30, subject_type: str = "Subject2") -> List[Dict]:
        """
        Lists invoices metadata from the last X days.
        subjectType: Subject1 (Seller), Subject2 (Buyer)
        """
        dtnow = datetime.datetime.now(datetime.timezone.utc)
        dtdiff = datetime.timedelta(days=days)
        
        page_size = 100
        page_offset = 0
        all_invoices = []

        data = {
            "subjectType": subject_type,
            "dateRange": {
                "dateType": "Issue",
                "from": (dtnow - dtdiff).isoformat(),
                "to": dtnow.isoformat(),
            }
        }

        while True:
            url = f"{self.cfg.url}/invoices/query/metadata?pageOffset={page_offset}&pageSize={page_size}"
            resp = requests.post(url, json=data, headers=self._get_headers(), timeout=15)
            
            if resp.status_code != 200:
                error_text = resp.text
                if resp.status_code == 429:
                    try:
                        details = resp.json().get('status', {}).get('details', [])
                        wait_msg = details[0] if details else "Zbyt wiele żądań."
                        raise KSeFError(f"Limit API przekroczony (429): {wait_msg}", error_text)
                    except:
                        raise KSeFError("Przekroczono limit zapytań KSeF (429). Spróbuj ponownie za ok. 20-30 minut.", error_text)
                
                if "narrow your filters" in error_text.lower():
                    raise KSeFError("Zbyt szerokie zapytanie. Wybrany zakres dat i typ podmiotu zwraca ponad 10 000 wyników. Spróbuj zawęzić zakres (np. --days 1).", error_text)
                raise KSeFError(f"Error querying invoices: {resp.status_code}", error_text)
            
            result = resp.json()
            # Try both possible keys for compatibility
            invoices = result.get("invoices") or result.get("invoiceMetadataList") or []
            all_invoices.extend(invoices)
            
            if result.get("hasMore", False):
                page_offset += page_size
            else:
                break
                
        return all_invoices

    def download_invoice(self, ksef_number: str) -> str:
        """
        Downloads the full XML of an invoice by KSeF number.
        Saves it to storage/inbox.
        """
        url = f"{self.cfg.url}/invoices/ksef/{ksef_number}"
        resp = requests.get(url, headers=self._get_headers(), timeout=15)
        
        if resp.status_code != 200:
            raise KSeFError(f"Error downloading invoice {ksef_number}: {resp.status_code}", resp.text)
        
        output_path = self.cfg.received_xml / f"{ksef_number}.xml"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(resp.text)
            
        return str(output_path)
