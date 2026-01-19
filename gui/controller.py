import threading
from tkinter import filedialog, messagebox
from model import KSeFModel
from view import KSeFViewV4

class KSeFController:
    def __init__(self):
        self.model = KSeFModel()
        
        # Nested callback structure for organized View
        callbacks = {
            "menu": self.handle_view_switch,
            
            "session_actions": {
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

    # --- SESSION ACTIONS ---
    def handle_login(self):
        def task():
            self.model.open_session()
            self.refresh_ui()
        threading.Thread(target=task).start()

    def handle_check_status(self):
        self.model.check_session_status()
        self.refresh_ui()

    def handle_refresh_token(self):
        self.model.refresh_session_token()
        self.refresh_ui()

    def handle_logout(self):
        self.model.logout()
        self.refresh_ui()

    # --- SALES ACTIONS ---
    def handle_convert_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            template = self.view.views['sales'].combo_mapping.get()
            def task():
                self.model.convert_excel_to_xml(file_path, template)
                self.refresh_ui()
                messagebox.showinfo("Sukces", f"Przekonwertowano plik za pomocą {template}")
            threading.Thread(target=task).start()

    def handle_send_xml(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if file_path:
            def task():
                self.model.send_xml_invoice(file_path)
                self.refresh_ui()
            threading.Thread(target=task).start()

    def handle_check_upo(self):
        # Simulation: pick the first one from sales for mock
        if self.model.sales_invoices:
            inv_nr = self.model.sales_invoices[0][0]
            self.model.check_status_upo(inv_nr)
        else:
            self.model.log("Brak faktur na liście do sprawdzenia statusu.", "WARNING")
        self.refresh_ui()

    def handle_preview(self):
        self.model.log("Generowanie wizualizacji HTML...")
        # In a real app, this would open webbrowser.open("path_to.html")
        self.refresh_ui()

    # --- PURCHASE ACTIONS ---
    def handle_sync_purchases(self):
        def task():
            self.model.fetch_purchases()
            self.refresh_ui()
        threading.Thread(target=task).start()

    def handle_download_xml(self):
        self.model.log("Pobieranie wybranych plików XML do folderu lokalnego...")
        self.refresh_ui()

    def handle_export_excel(self):
        self.model.export_purchases_to_excel()
        self.refresh_ui()

if __name__ == "__main__":
    c = KSeFController()
    c.run()
