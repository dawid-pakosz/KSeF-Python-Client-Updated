import os
import time
import datetime
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from ksef_client.utils.ksefconfig import Config
from ksef_client.services.auth_service import AuthService
from ksef_client.services.invoice_service import InvoiceService
from ksef_client.services.query_service import QueryService
from ksef_client.services.export_service import ExportService
try:
    from standalone_mapper.template_mapper import TemplateMapper
except ImportError:
    TemplateMapper = None
    print("Warning: Could not import standalone_mapper. Excel loading will fail.")

class LogStream:
    """Pośrednik przekierowujący dane z terminala (stdout/stderr) do loggera."""
    def __init__(self, logger, log_level):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

class KSeFModel:
    def __init__(self):
        # Inicjalizacja konfiguracji (domyślnie firma 1, osoba fizyczna = False)
        # W przyszłości można dodać ekran wyboru profilu w GUI
        self.config = Config(1, initialize=True)
        
        # --- KONFIGURACJA LOGOWANIA ---
        self.logs = []
        self._setup_logging()
        
        # Bridge backend logs to GUI console (via config)
        self.config.log_callback = self.log
        
        self.auth_service = AuthService(self.config)
        self.invoice_service = None # Opóźniona inicjalizacja po zalogowaniu
        self.export_service = ExportService(self.config)
        
        self.is_logged_in = False
        self.session_token = None
        self.token_expiry = 0 # Timestamp wygaśnięcia
        self.user_name = f"Dawid ({self.config.nip})"
        self.app_version = self.config.app_version
        self.env = self.config.version.upper()
        self.last_operation = "System gotowy"
        
        # Dane faktur (początkowo puste, pobierane z serwisu)
        self.sales_invoices = []
        self.purchase_invoices = []
        
        self.available_themes = ["darkly", "flatly", "cosmo", "superhero", "journal", "pulse", "sandstone", "united"]
        self.mapping_templates = [
            "ACC_PLN_PROSTA",
            "ACC_MULTI",
            "ACC_EUR"
        ]

    def _setup_logging(self):
        """Konfiguracja logowania z datą w nazwie i ręcznym czyszczeniem starych logów."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        log_file = self.config.logs / f"app_{today}.log"
        
        # 1. RĘCZNE CZYSZCZENIE STARYCH LOGÓW (starszych niż 30 dni)
        try:
            now = time.time()
            retention_days = 90
            for f in os.listdir(self.config.logs):
                f_path = os.path.join(self.config.logs, f)
                if os.path.isfile(f_path) and f.startswith("app_") and f.endswith(".log"):
                    # Jeśli plik jest starszy niż 30 dni
                    if os.stat(f_path).st_mtime < now - (retention_days * 86400):
                        os.remove(f_path)
        except Exception as e:
            print(f"Błąd podczas czyszczenia logów: {e}")

        # 2. KONFIGURACJA LOGGERA
        self.logger = logging.getLogger("KSeFApp")
        self.logger.setLevel(logging.DEBUG)
        
        file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] %(message)s')
        
        # Używamy standardowego FileHandler, bo data jest już w nazwie
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        
        # Unikaj duplikowania handlerów
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            
            # --- PRZECHWYTYWANIE TERMINALA ---
            sys.stdout = LogStream(self.logger, logging.INFO)
            sys.stderr = LogStream(self.logger, logging.ERROR)
            
            self.logger.info(f"--- Logowanie zainicjowane (Plik: {log_file.name}) ---")

    def log(self, message, level="INFO"):
        """
        Loguje komunikat do pliku i (jeśli poziom >= INFO) do konsoli GUI.
        """
        # 1. Zapis do systemowego loggera (do pliku)
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        
        # Jeśli logujemy błąd, automatycznie dołączamy informacje o wyjątku (traceback)
        if numeric_level >= logging.ERROR:
            self.logger.log(numeric_level, message, exc_info=True)
        else:
            self.logger.log(numeric_level, message)
        
        # 2. Przekazanie do konsoli GUI (tylko INFO, WARNING, ERROR, CRITICAL)
        if numeric_level >= logging.INFO:
            timestamp = time.strftime('%H:%M:%S')
            log_entry = f"[{timestamp}] [{level}] {message}"
            self.logs.append(log_entry)
            self.last_operation = message
            return log_entry
        return None

    def init_system(self):
        """Fetch KSeF certificates (v2 init)."""
        self.log("Fetching KSeF public certificates...")
        try:
            self.auth_service.fetch_certificates()
            self.config.reload_certificates() # Force memory refresh
            self.log("Certificates fetched successfully.")
            return True
        except Exception as e:
            self.log(f"Initialization error: {str(e)}", "ERROR")
            return False

    def open_session(self):
        self.log("Connecting to KSeF API (AuthService)...")
        try:
            # Login in AuthService saves token to file and sets it in config
            self.auth_service.login()
            # Open invoice session
            if not self.invoice_service:
                self.invoice_service = InvoiceService(self.config)
            ref_no = self.invoice_service.session_open()
            
            # Initialize QueryService after login as it needs the token
            self.query_service = QueryService(self.config)
            
            self.is_logged_in = True
            self.session_token = ref_no
            
            # KSeF session lasts usually 1 hour (3600s)
            self.token_expiry = time.time() + 3500 
            
            self.log(f"Session opened correctly. Ref: {ref_no}")
            return True
        except Exception as e:
            self.log(f"Login error: {str(e)}", "ERROR")
            return False

    def check_session_status(self):
        self.log("Checking session status...")
        try:
            status = self.invoice_service.session.get('referenceNumber')
            if status:
                self.is_logged_in = True
                self.log(f"Session active: {status}")
            else:
                self.is_logged_in = False
                self.log("No active session.")
            return self.is_logged_in
        except:
            self.is_logged_in = False
            return False

    def refresh_session_token(self):
        self.log("Refreshing session token...")
        try:
            self.auth_service.refresh_token()
            self.log("Token refreshed.")
            return True
        except Exception as e:
            self.log(f"Refresh error: {str(e)}", "ERROR")
            return False

    def logout(self):
        self.log("Closing session (AuthService)...")
        try:
            self.invoice_service.session_close()
            self.is_logged_in = False
            self.session_token = None
            self.log("Logged out safely.")
            return True
        except Exception as e:
            self.log(f"Logout error: {str(e)}", "ERROR")
            return False

    def load_excel_preview(self, excel_path, template):
        self.log(f"Loading Excel preview: {excel_path} ({template})...")
        
        if not TemplateMapper:
            self.log("Error: TemplateMapper module not available.", "ERROR")
            return None
            
        try:
            # Use path from config which handles frozen state
            rules_path = os.path.join(self.config.resources_dir, "technical_rules.json")
            
            if not os.path.exists(rules_path):
                self.log(f"Error: Rules file not found at {rules_path}", "ERROR")
                return None
                
            mapper = TemplateMapper(rules_path)
            data = mapper.extract_data(excel_path, template)
            
            if data['status'] == "BŁĄD":
                self.log(f"Extraction failed for {excel_path}", "ERROR")
            else:
                self.log(f"Loaded data for {excel_path}")
                
            return data
            
        except Exception as e:
            self.log(f"Load error: {str(e)}", "ERROR")
            return None

    def generate_xml_from_file(self, excel_path, template):
        self.log(f"Generating XML for: {os.path.basename(excel_path)}...")
        
        if not TemplateMapper:
            return None
            
        try:
            # Re-init mapper (could be optimized to single instance if rules don't change)
            rules_path = os.path.join(self.config.resources_dir, "technical_rules.json")
            mapper = TemplateMapper(rules_path)
            
            output_xml = excel_path.replace('.xlsx', '_mapped.xml')
            generated_path = mapper.create_xml(excel_path, output_xml, mapping_type=template)
            
            self.log(f"Generated: {os.path.basename(generated_path)}")
            return generated_path
            
        except Exception as e:
            self.log(f"Generation error: {str(e)}", "ERROR")
            return None

    def send_xml_invoice(self, xml_path):
        if not self.is_logged_in:
             self.log("Error: You must be logged in to send an invoice.", "ERROR")
             return False
        self.log(f"Sending file {xml_path} (InvoiceService)...")
        try:
            ref_no = self.invoice_service.send_invoice(xml_path)
            self.log(f"Invoice sent. Ref: {ref_no}")
            return True
        except Exception as e:
            self.log(f"Send error: {str(e)}", "ERROR")
            return False

    def check_status_upo(self, xml_path):
        self.log(f"Fetching status/UPO for XML file...")
        try:
            upo_path = self.invoice_service.download_upo(xml_path)
            self.log(f"UPO fetched and saved to: {upo_path}")
            return True
        except Exception as e:
            self.log(f"Status error: {str(e)}", "ERROR")
            return False

    def fetch_purchases(self, days=30, subject_type="Subject2"):
        self.log(f"Fetching {subject_type} invoices (last {days} days)...")
        try:
            if not self.query_service:
                self.query_service = QueryService(self.config)
                
            invoices = self.query_service.list_invoices(days=days, subject_type=subject_type)
            self.purchase_invoices_raw = invoices  # Store raw for export
            self.last_subject_type = subject_type   # Store for export consistency
            
            self.purchase_invoices = []
            
            for inv in invoices:
                # Basic metadata extraction
                ksef = inv.get('ksefNumber', 'None')
                date = inv.get('invoicingDate', 'None')
                if 'T' in date: date = date.split('T')[0] # Clean date format
                
                inv_no = inv.get('invoiceNumber', 'None')
                curr = inv.get('currency', 'PLN') # JSON shows 'currency' not 'currencyCode'
                
                # Robust Subject extraction based on subject_type
                # If we query as Buyer (Subject2), result counterparty is Seller
                # If we query as Seller (Subject1), result counterparty is Buyer
                if subject_type == "Subject2":
                    subj_obj = inv.get('seller') or {}
                else:
                    subj_obj = inv.get('buyer') or {}
                
                # Check NIP
                # Logic: Check identifier -> value OR direct 'nip' key
                nip = 'None'
                identifier = subj_obj.get('identifier')
                if isinstance(identifier, dict):
                    nip = identifier.get('value', 'None')
                else:
                    nip = subj_obj.get('nip', 'None')
                
                # Check Name
                name = subj_obj.get('name') or subj_obj.get('fullName') or 'Unknown'
                
                # Amounts directly from root
                gross = f"{inv.get('grossAmount', 0):.2f}"
                net = f"{inv.get('netAmount', 0):.2f}"
                vat = f"{inv.get('vatAmount', 0):.2f}"
                
                # Format for Treeview (nip, name, ksef_no, inv_no, date, net, gross, vat, currency)
                self.purchase_invoices.append((nip, name, ksef, inv_no, date, net, gross, vat, curr))
            
            self.log(f"Fetched {len(self.purchase_invoices)} invoices.")
            return self.purchase_invoices
        except Exception as e:
            self.log(f"Fetch error: {str(e)}", "ERROR")
            return False

    def export_purchases_to_excel(self):
        if not hasattr(self, 'purchase_invoices_raw') or not self.purchase_invoices_raw:
            self.log("No data to export. Fetch invoices first.", "WARNING")
            return False
            
        self.log("Generating summary report from last fetch...")
        try:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            output_path = self.config.reports / f"summary_report_{timestamp}.xlsx"
            
            # Use ExportService with stored subject_type for mapping consistency
            subj_type = getattr(self, 'last_subject_type', 'Subject2')
            path = self.export_service.export_to_excel(self.purchase_invoices_raw, str(output_path), subject_type=subj_type)
            
            self.log(f"Report exported to: {path}")
            return path
        except Exception as e:
            self.log(f"Export error: {str(e)}", "ERROR")
            return False
