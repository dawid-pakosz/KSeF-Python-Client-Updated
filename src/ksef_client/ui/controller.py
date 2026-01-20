import threading
from tkinter import filedialog, messagebox
from .model import KSeFModel
from .view import KSeFViewV4
from .proxy_dialog import ProxyPasswordDialog
import os

class KSeFController:
    def __init__(self):
        self.model = KSeFModel()
        
        # Struktura callbacków dla zorganizowanego Widoku
        callbacks = {
            "menu": self.handle_view_switch,
            
            "session_actions": {
                "init": self.handle_init,
                "login": self.handle_login,
                "check_status": self.handle_check_status,
                "refresh": self.handle_refresh_token,
                "logout": self.handle_logout
            },
            
            "sales_actions": {
                "convert": self.handle_convert_excel,
                "send_xml": self.handle_send_xml,
                "check_upo": self.handle_check_upo,
                "preview": self.handle_preview
            },
            
            "purchase_actions": {
                "sync": self.handle_sync_purchases,
                "download": self.handle_download_xml,
                "export": self.handle_export_excel,
                "preview": self.handle_preview
            }
        }
        
        self.view = KSeFViewV4(callbacks, self.model)
        self.refresh_ui()
        
        self.refresh_ui()

    def run(self):
        self.view.mainloop()

    def refresh_ui(self):
        self.view.update_ui(self.model)
        # Przekazywanie logów do konsoli widoku
        if self.model.logs:
            self.view.log(self.model.logs[-1])

    def handle_view_switch(self, view_name):
        self.view.show_view(view_name)
        self.model.log(f"Przełączono widok na: {view_name}")
        self.refresh_ui()

        self.refresh_ui()

    # --- AKCJE SESJI ---
    def handle_init(self):
        def task():
            if self.model.init_system():
                messagebox.showinfo("Initialization", "KSeF certificates have been downloaded. You can now open a session.")
            self.refresh_ui()
        threading.Thread(target=task).start()

    def handle_login(self):
        # System login (UID)
        username = os.environ.get('USERNAME') or os.getlogin() or "User"
        
        def on_proxy_confirm(password=None):
            if password:
                # Set proxy environment variables
                proxy_url = f"http://{username}:{password}@ncproxy1:8080"
                os.environ["HTTP_PROXY"] = proxy_url
                os.environ["HTTPS_PROXY"] = proxy_url
                # Debug print
                print(f">>> [TEST] Proxy env set for {username}: {proxy_url}")
                self.model.log("Proxy password provided and environment variables set.")
            else:
                # No password entered – keep existing env or clear
                os.environ.pop("HTTP_PROXY", None)
                os.environ.pop("HTTPS_PROXY", None)
                self.model.log("Proxy password not provided; proxy disabled.")
            
            # Action
            def task():
                # Step 1: Init (fetching certificates)
                if not self.model.init_system():
                    self.refresh_ui()
                    messagebox.showerror("Error", "Failed to fetch certificates.")
                    return

                # Step 2: Login and open session
                if self.model.open_session():
                    self.refresh_ui()
                    messagebox.showinfo("KSeF", "Successfully logged in and session started.")
                else:
                    self.refresh_ui()
                    messagebox.showerror("Error", "Login failed. Check logs for details.")
            
            threading.Thread(target=task).start()

        # Check if proxy is enabled in config
        if self.model.config.proxy_enabled:
            # Show pop-up
            ProxyPasswordDialog(self.view, username, on_proxy_confirm)
        else:
            # Skip dialog
            self.model.log("Proxy disabled in config. Proceeding to direct login.")
            on_proxy_confirm()

    def handle_check_status(self):
        self.model.check_session_status()
        self.refresh_ui()

    def handle_refresh_token(self, silent=False):
        def task():
            if self.model.refresh_session_token():
                self.refresh_ui()
                if not silent:
                    messagebox.showinfo("KSeF", "Token has been refreshed.")
            self.refresh_ui()
        threading.Thread(target=task).start()

    def handle_logout(self):
        def task():
            if self.model.logout():
                self.refresh_ui()
                messagebox.showinfo("KSeF", "Session has been closed.")
            self.refresh_ui()
        threading.Thread(target=task).start()

    # --- SALES ACTIONS ---
    def handle_convert_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")], title="Select Excel file to convert")
        if file_path:
            template = self.view.views['sales'].combo_mapping.get()
            def task():
                self.model.convert_excel_to_xml(file_path, template)
                self.refresh_ui()
                messagebox.showinfo("Success", f"Converted using {template}\n(Mapping engine in progress)")
            threading.Thread(target=task).start()

    def handle_send_xml(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")], title="Select XML invoice to send")
        if file_path:
            def task():
                if self.model.send_xml_invoice(file_path):
                    self.refresh_ui()
                    messagebox.showinfo("Success", "Invoice sent to KSeF.")
                self.refresh_ui()
            threading.Thread(target=task).start()

    def handle_check_upo(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")], title="Select XML file to check UPO")
        if file_path:
            def task():
                self.model.check_status_upo(file_path)
                self.refresh_ui()
            threading.Thread(target=task).start()

    def handle_preview(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")], title="Select XML file for visualization")
        if file_path:
            self.model.log(f"Generating visualization for {file_path}...")
            try:
                from ksef_client.views.ksef_viz import run_visualization
                if run_visualization(file_path, theme="corporate"):
                    self.model.log("✅ Visualization generated.")
            except Exception as e:
                self.model.log(f"❌ Visualization error: {e}", "ERROR")
            self.refresh_ui()

    def handle_sync_purchases(self):
        if not self.model.is_logged_in:
            messagebox.showwarning("Brak sesji", "Musisz najpierw otworzyć sesję (Login), aby pobrać dane z KSeF.")
            return

        # Pobierz widok, aby wyciągnąć parametry
        p_view = self.view.views['purchases']
        
        # Pobierz wartości z UI
        ui_type = p_view.var_invoice_type.get()
        days = p_view.var_days.get()
        
        # Mapowanie typu (UI -> API)
        # "Sales invoices (Subject1)" -> "Subject1"
        # "Purchase invoices (Subject2)" -> "Subject2"
        subject_type = "Subject1" if "Subject1" in ui_type else "Subject2"
        
        def task():
            self.model.log(f"Inicjowanie pobierania: {ui_type} za ostatnie {days} dni...")
            data = self.model.fetch_purchases(days=days, subject_type=subject_type)
            
            def update_ui():
                if data is not False:
                    p_view.update_table(data)
                    self.refresh_ui()
                    messagebox.showinfo("KSeF", f"Pobrano {len(data)} faktur.")
                else:
                    self.refresh_ui()
                    messagebox.showerror("Błąd", "Nie udało się pobrać faktur. Sprawdź logi (Action Summary).")
            
            self.view.after(0, update_ui)
            
        threading.Thread(target=task).start()

    def handle_download_xml(self):
        self.model.log("Downloading XML files (feature in progress)...")
        self.refresh_ui()

    def handle_export_excel(self):
        def task():
            path = self.model.export_purchases_to_excel()
            if path:
                self.refresh_ui()
                messagebox.showinfo("Sukces", f"Raport Excel został wygenerowany:\n{path}")
            self.refresh_ui()
        threading.Thread(target=task).start()
