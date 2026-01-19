import time
from ksef_client.utils.ksefconfig import Config
from ksef_client.services.auth_service import AuthService
from ksef_client.services.invoice_service import InvoiceService
from ksef_client.services.query_service import QueryService
from ksef_client.services.export_service import ExportService

class KSeFModel:
    def __init__(self):
        # Inicjalizacja konfiguracji (domyślnie firma 1, osoba fizyczna = False)
        # W przyszłości można dodać ekran wyboru profilu w GUI
        self.config = Config(1, initialize=True)
        self.auth_service = AuthService(self.config)
        self.auth_service = AuthService(self.config)
        self.invoice_service = None # Opóźniona inicjalizacja po zalogowaniu
        self.export_service = ExportService(self.config)
        
        self.is_logged_in = False
        self.session_token = None
        self.token_expiry = 0 # Timestamp wygaśnięcia
        self.user_name = f"Dawid ({self.config.nip})"
        self.last_operation = "System gotowy"
        
        # Dane faktur (początkowo puste, pobierane z serwisu)
        self.sales_invoices = []
        self.purchase_invoices = []
        
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

    def init_system(self):
        """Pobieranie certyfikatów KSeF (v2 init)."""
        self.log("Pobieranie certyfikatów publicznych KSeF...")
        try:
            self.auth_service.fetch_certificates()
            self.log("✅ Certyfikaty pobrane pomyślnie.")
            return True
        except Exception as e:
            self.log(f"❌ Błąd inicjalizacji: {str(e)}", "ERROR")
            return False

    def open_session(self):
        self.log("Łączenie z KSeF API (AuthService)...")
        try:
            # Login w AuthService zapisuje token do pliku i ustawia go w config
            self.auth_service.login()
            self.auth_service.login()
            # Otwarcie sesji faktur
            if not self.invoice_service:
                self.invoice_service = InvoiceService(self.config)
            ref_no = self.invoice_service.session_open()
            self.is_logged_in = True
            self.session_token = ref_no
            
            # KSeF session lasts usually 1 hour (3600s)
            self.token_expiry = time.time() + 3500 
            
            self.log(f"✅ Sesja otwarta poprawnie. Ref: {ref_no}")
            return True
        except Exception as e:
            self.log(f"❌ Błąd logowania: {str(e)}", "ERROR")
            return False

    def check_session_status(self):
        self.log("Sprawdzanie statusu sesji...")
        try:
            status = self.invoice_service.session.get('referenceNumber')
            if status:
                self.is_logged_in = True
                self.log(f"✅ Sesja aktywna: {status}")
            else:
                self.is_logged_in = False
                self.log("Brak aktywnej sesji.")
            return self.is_logged_in
        except:
            self.is_logged_in = False
            return False

    def refresh_session_token(self):
        self.log("Odświeżanie tokena sesyjnego...")
        try:
            self.auth_service.refresh_token()
            self.log("✅ Token odświeżony.")
            return True
        except Exception as e:
            self.log(f"❌ Błąd odświeżania: {str(e)}", "ERROR")
            return False

    def logout(self):
        self.log("Zamykanie sesji (AuthService)...")
        try:
            self.invoice_service.session_close()
            self.is_logged_in = False
            self.session_token = None
            self.log("Wylogowano bezpiecznie.")
            return True
        except Exception as e:
            self.log(f"❌ Błąd wylogowania: {str(e)}", "ERROR")
            return False

    def convert_excel_to_xml(self, excel_path, template):
        self.log(f"Konwersja: {excel_path} przy użyciu {template}...")
        # Tutaj w przyszłości wepniemy moduł mapowania Excel -> XML
        time.sleep(1.5)
        self.log(f"✅ Wygenerowano XML dla {excel_path}.")
        return True

    def send_xml_invoice(self, xml_path):
        if not self.is_logged_in:
             self.log("❌ Błąd: Musisz być zalogowany, aby wysłać fakturę.", "ERROR")
             return False
        self.log(f"Wysyłanie pliku {xml_path} (InvoiceService)...")
        try:
            ref_no = self.invoice_service.send_invoice(xml_path)
            self.log(f"✅ Faktura wysłana. Ref: {ref_no}")
            return True
        except Exception as e:
            self.log(f"❌ Błąd wysyłki: {str(e)}", "ERROR")
            return False

    def check_status_upo(self, xml_path):
        self.log(f"Pobieranie statusu/UPO dla pliku XML...")
        try:
            # download_upo automatycznie sprawdza status i pobiera jeśli gotowe
            upo_path = self.invoice_service.download_upo(xml_path)
            self.log(f"✅ UPO pobrane i zapisane w: {upo_path}")
            return True
        except Exception as e:
            self.log(f"❌ Błąd statusu: {str(e)}", "ERROR")
            return False

    def fetch_purchases(self):
        self.log("Pobieranie faktur zakupowych (QueryService)...")
        try:
            # Domyślnie 30 dni wstecz, zakup (Subject2)
            invoices = self.query_service.list_invoices(days=30, subject_type="Subject2")
            self.purchase_invoices = []
            for inv in invoices:
                ksef = inv.get('ksefNumber', 'Brak')
                date = inv.get('invoicingDate', 'Brak')
                seller = inv.get('subjectBy', {}).get('name', 'Nieznany')
                amount = f"{inv.get('grossAmount', '0.00')} PLN"
                self.purchase_invoices.append((ksef, date, seller, amount))
            
            self.log(f"✅ Pobrano {len(self.purchase_invoices)} faktur.")
            return True
        except Exception as e:
            self.log(f"❌ Błąd pobierania: {str(e)}", "ERROR")
            return False

    def export_purchases_to_excel(self):
        if not self.purchase_invoices:
            self.log("⚠️ Brak danych do eksportu. Pobierz faktury najpierw.", "WARNING")
            return False
            
        self.log("Generowanie raportu zbiorczego do Excela...")
        try:
            # Ponowne pobranie pełnych danych dla eksportu
            invoices = self.query_service.list_invoices(days=30, subject_type="Subject2")
            output_path = self.config.reports / f"raport_zakupow_{time.strftime('%Y%m%d')}.xlsx"
            path = self.export_service.export_to_excel(invoices, str(output_path))
            self.log(f"✅ Raport wyeksportowany do: {path}")
            return True
        except Exception as e:
            self.log(f"❌ Błąd eksportu: {str(e)}", "ERROR")
            return False
