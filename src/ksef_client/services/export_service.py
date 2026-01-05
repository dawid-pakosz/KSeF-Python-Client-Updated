import pandas as pd
import datetime
import os
from typing import List, Dict
from ..utils.ksefconfig import Config

class ExportService:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def export_to_excel(self, invoices: List[Dict], output_path: str) -> str:
        """
        Converts list of invoice metadata to an Excel file.
        """
        if not invoices:
            return None

        flat_data = []
        for inv in invoices:
            # Safely extract subject info
            subject = inv.get('subjectBy') or inv.get('issuedBy') or inv.get('receivedBy') or {}
            
            row = {
                "Numer KSeF": inv.get('ksefNumber'),
                "Data Wystawienia": inv.get('invoicingDate'),
                "Data Odebrania": inv.get('acquisitionTimestamp'),
                "NIP Kontrahenta": subject.get('identifier', {}).get('value'),
                "Nazwa Kontrahenta": subject.get('name') or subject.get('fullName'),
                "Kwota Brutto": inv.get('grossAmount'),
                "Waluta": inv.get('currencyCode', 'PLN'),
                "Numer Faktury": inv.get('invoiceNumber'),
            }
            flat_data.append(row)

        df = pd.DataFrame(flat_data)
        
        # Adjust column widths and formatting could be done here with openpyxl if needed,
        # but for now a simple pandas export is a great start.
        df.to_excel(output_path, index=False, engine='openpyxl')
        
        return output_path
