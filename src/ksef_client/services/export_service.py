import pandas as pd
import datetime
import os
from typing import List, Dict
from ..utils.ksefconfig import Config

class ExportService:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def export_to_excel(self, invoices: List[Dict], output_path: str, subject_type: str = "Subject2") -> str:
        """
        Converts list of invoice metadata to an Excel file.
        Matches the logic used in UI for consistency.
        """
        if not invoices:
            return None

        flat_data = []
        for inv in invoices:
            # 1. Date cleaning
            date = inv.get('invoicingDate', 'None')
            if 'T' in date: date = date.split('T')[0]
            
            # 2. Contractor selection (robust mapping)
            if subject_type == "Subject2":
                subj_obj = inv.get('seller') or {}
            else:
                subj_obj = inv.get('buyer') or {}
            
            # 3. NIP
            nip = 'None'
            identifier = subj_obj.get('identifier')
            if isinstance(identifier, dict):
                nip = identifier.get('value', 'None')
            else:
                nip = subj_obj.get('nip', 'None')
            
            # 4. Name
            name = subj_obj.get('name') or subj_obj.get('fullName') or 'Unknown'
            
            # 5. Amounts & Currency
            curr = inv.get('currency', 'PLN')
            gross = inv.get('grossAmount', 0.0)
            net = inv.get('netAmount', 0.0)
            vat = inv.get('vatAmount', 0.0)

            row = {
                "NIP": nip,
                "Nazwa": name,
                "Numer KSeF": inv.get('ksefNumber'),
                "Nr faktury": inv.get('invoiceNumber'),
                "Data wystawienia": date,
                "Netto": net,
                "Brutto": gross,
                "VAT": vat,
                "Waluta": curr
            }
            flat_data.append(row)

        df = pd.DataFrame(flat_data)
        
        # Save with Excel engine
        df.to_excel(output_path, index=False, engine='openpyxl')
        
        return output_path
