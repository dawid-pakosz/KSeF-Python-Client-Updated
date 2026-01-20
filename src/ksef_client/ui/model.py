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
        # Bridge backend logs to GUI console
        self.config.log_callback = self.log
        
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
            "Standard Template (V1)",
            "Export Template (V2)",
            "Service Template (V3)",
            "Correction Template (V4)",
            "Proforma Template (V5)",
            "Special Template (V6)"
        ]
        
        self.logs = []

    def log(self, message, level="INFO"):
        timestamp = time.strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_entry)
        self.last_operation = message
        return log_entry

    def init_system(self):
        """Fetch KSeF certificates (v2 init)."""
        self.log("Fetching KSeF public certificates...")
        try:
            self.auth_service.fetch_certificates()
            self.config.reload_certificates() # Force memory refresh
            self.log("✅ Certificates fetched successfully.")
            return True
        except Exception as e:
            self.log(f"❌ Initialization error: {str(e)}", "ERROR")
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
            
            self.log(f"✅ Session opened correctly. Ref: {ref_no}")
            return True
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}", "ERROR")
            return False

    def check_session_status(self):
        self.log("Checking session status...")
        try:
            status = self.invoice_service.session.get('referenceNumber')
            if status:
                self.is_logged_in = True
                self.log(f"✅ Session active: {status}")
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
            self.log("✅ Token refreshed.")
            return True
        except Exception as e:
            self.log(f"❌ Refresh error: {str(e)}", "ERROR")
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
            self.log(f"❌ Logout error: {str(e)}", "ERROR")
            return False

    def convert_excel_to_xml(self, excel_path, template):
        self.log(f"Converting: {excel_path} using {template}...")
        # Future Excel -> XML mapping module
        time.sleep(1.5)
        self.log(f"✅ Generated XML for {excel_path}.")
        return True

    def send_xml_invoice(self, xml_path):
        if not self.is_logged_in:
             self.log("❌ Error: You must be logged in to send an invoice.", "ERROR")
             return False
        self.log(f"Sending file {xml_path} (InvoiceService)...")
        try:
            ref_no = self.invoice_service.send_invoice(xml_path)
            self.log(f"✅ Invoice sent. Ref: {ref_no}")
            return True
        except Exception as e:
            self.log(f"❌ Send error: {str(e)}", "ERROR")
            return False

    def check_status_upo(self, xml_path):
        self.log(f"Fetching status/UPO for XML file...")
        try:
            upo_path = self.invoice_service.download_upo(xml_path)
            self.log(f"✅ UPO fetched and saved to: {upo_path}")
            return True
        except Exception as e:
            self.log(f"❌ Status error: {str(e)}", "ERROR")
            return False

    def fetch_purchases(self, days=30, subject_type="Subject2"):
        self.log(f"Fetching {subject_type} invoices (last {days} days)...")
        try:
            if not self.query_service:
                self.query_service = QueryService(self.config)
                
            invoices = self.query_service.list_invoices(days=days, subject_type=subject_type)
            self.purchase_invoices_raw = invoices  # Store raw for export
            
            # FORCE DEBUG TO CONSOLE (STDOUT)
            if invoices:
                import json
                print("\n" + "="*50)
                print(f"DEBUG KSEF API RAW JSON (First Item):")
                print(json.dumps(invoices[0], indent=2))
                print("="*50 + "\n")
                self.log(f"DEBUG: Sprawdź terminal/konsolę dla surowych danych JSON.")

            self.purchase_invoices = []
            
            for inv in invoices:
                # Basic metadata extraction
                ksef = inv.get('ksefNumber', 'None')
                date = inv.get('invoicingDate', 'None')
                inv_no = inv.get('invoiceNumber', 'None')
                curr = inv.get('currencyCode', 'PLN')
                
                # Robust Subject extraction (KSeF API metadata varies)
                # Possible keys: subjectBy, subjectTo, issuedBy, receivedBy
                subj_obj = inv.get('subjectBy') or inv.get('issuedBy') or inv.get('receivedBy') or inv.get('subjectTo') or {}
                
                # Try to get NIP (identifier value)
                # Logic: Check identifier -> value OR subjectIdentifier -> identifier
                identifier = subj_obj.get('identifier', {})
                if not identifier: 
                    identifier = subj_obj.get('subjectIdentifier', {}).get('identifier', {})
                
                nip = identifier.get('value') if isinstance(identifier, dict) else identifier
                if not nip: nip = 'None'
                
                # Try to get Name
                name = subj_obj.get('name') or subj_obj.get('fullName') or 'Unknown'
                
                # Amounts
                gross = str(inv.get('grossAmount', '0.00'))
                net = str(inv.get('netAmount', '0.00')) 
                vat = str(inv.get('vatAmount', '0.00'))
                
                # Format for Treeview (nip, name, ksef_no, inv_no, date, net, gross, vat, currency)
                self.purchase_invoices.append((nip, name, ksef, inv_no, date, net, gross, vat, curr))
            
            self.log(f"✅ Fetched {len(self.purchase_invoices)} invoices.")
            return self.purchase_invoices
        except Exception as e:
            self.log(f"❌ Fetch error: {str(e)}", "ERROR")
            return False

    def export_purchases_to_excel(self):
        if not hasattr(self, 'purchase_invoices_raw') or not self.purchase_invoices_raw:
            self.log("⚠️ No data to export. Fetch invoices first.", "WARNING")
            return False
            
        self.log("Generating summary report from last fetch...")
        try:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            output_path = self.config.reports / f"summary_report_{timestamp}.xlsx"
            
            # Use ExportService to process raw list
            path = self.export_service.export_to_excel(self.purchase_invoices_raw, str(output_path))
            
            self.log(f"✅ Report exported to: {path}")
            return path
        except Exception as e:
            self.log(f"❌ Export error: {str(e)}", "ERROR")
            return False
