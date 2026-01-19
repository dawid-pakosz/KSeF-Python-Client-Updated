import time

class KSeFModel:
    def __init__(self):
        self.is_logged_in = False
        self.session_token = None
        self.user_name = "Dawid"
        self.last_operation = "System gotowy"
        
        # Sales (Sprzedaż)
        self.sales_invoices = [
            ("FV/2024/S001", "2024-03-20", "Klient A", "Wysłana"),
            ("FV/2024/S002", "2024-03-21", "Klient B", "Błąd"),
        ]
        
        # Purchases (Zakupy)
        self.purchase_invoices = [
            ("FV/2024/P100", "2024-03-15", "Dostawca X", "Pobrana"),
            ("FV/2024/P101", "2024-03-16", "Dostawca Y", "Pobrana"),
        ]
        
        self.available_themes = ["darkly", "flatly", "cosmo", "superhero", "journal", "pulse", "sandstone", "united"]
        self.mapping_templates = [
            "Szablon Standardowy (V1)",
            "Szablon Eksportowy (V2)",
            "Szablon Usługowy (V3)",
            "Szablon Korekta (V4)",
            "Szablon Proforma (V5)",
            "Szablon Specjalny (V6)"
        ]
        
        self.logs = []

    def log(self, message, level="INFO"):
        timestamp = time.strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_entry)
        self.last_operation = message
        return log_entry

    # Placeholder for AuthService
    def open_session(self):
        self.log("Łączenie z KSeF API (AuthService)...")
        time.sleep(1)
        self.is_logged_in = True
        self.session_token = "MOCK_TOKEN_12345"
        self.log("✅ Sesja otwarta poprawnie. Token pobrany.")
        return True

    def check_session_status(self):
        self.log("Sprawdzanie statusu sesji...")
        time.sleep(0.5)
        status = "AKTYWNA" if self.is_logged_in else "BRAK"
        self.log(f"Status sesji: {status}")
        return self.is_logged_in

    def refresh_session_token(self):
        if not self.is_logged_in:
            self.log("❌ Nie można odświeżyć - brak aktywnej sesji.", "ERROR")
            return False
        self.log("Odświeżanie tokena sesyjnego...")
        time.sleep(0.8)
        self.session_token = "MOCK_TOKEN_REFRESHED"
        self.log("✅ Token odświeżony.")
        return True

    def logout(self):
        self.log("Zamykanie sesji (AuthService)...")
        time.sleep(0.5)
        self.is_logged_in = False
        self.session_token = None
        self.log("Wylogowano bezpiecznie.")
        return True

    # Placeholder for InvoiceService
    def convert_excel_to_xml(self, excel_path, template):
        self.log(f"Konwersja: {excel_path} przy użyciu {template}...")
        time.sleep(1.5)
        self.log(f"✅ Wygenerowano XML dla {excel_path}.")
        return True

    def send_xml_invoice(self, xml_path):
        if not self.is_logged_in:
             self.log("❌ Błąd: Musisz być zalogowany, aby wysłać fakturę.", "ERROR")
             return False
        self.log(f"Wysyłanie pliku {xml_path} (InvoiceService)...")
        time.sleep(1.2)
        nr = f"FV/2024/S{len(self.sales_invoices)+1:03d}"
        self.sales_invoices.insert(0, (nr, time.strftime('%Y-%m-%d'), "Nowy Klient", "Wysłana"))
        self.log(f"✅ Faktura {nr} zarejestrowana w KSeF.")
        return True

    def check_status_upo(self, invoice_nr):
        self.log(f"Pobieranie statusu/UPO dla {invoice_nr} (QueryService)...")
        time.sleep(0.8)
        self.log(f"✅ UPO dla {invoice_nr} pobrane i zapisane.")
        return True

    # Placeholder for QueryService
    def fetch_purchases(self):
        self.log("Pobieranie faktur zakupowych z ostatnich 30 dni (QueryService)...")
        time.sleep(1.5)
        self.log(f"✅ Pobrano {len(self.purchase_invoices)} faktur.")
        return True

    def export_purchases_to_excel(self):
        self.log("Generowanie raportu zbiorczego do Excela...")
        time.sleep(1.0)
        self.log("✅ Raport wyeksportowany do 'ksef_purchases_report.xlsx'.")
        return True
