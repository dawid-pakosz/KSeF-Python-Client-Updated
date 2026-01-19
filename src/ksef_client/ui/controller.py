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
                messagebox.showinfo("Inicjalizacja", "Certyfikaty KSeF zostały pobrane. Możesz teraz otworzyć sesję.")
            self.refresh_ui()
        threading.Thread(target=task).start()

    def handle_login(self):
        # Pobieramy login systemowy (UID)
        username = os.environ.get('USERNAME') or os.getlogin() or "Użytkownik"
        
        def on_proxy_confirm(password=None):
            if password:
                # Tymczasowe działanie: print do terminala (do testów) zgodnie z prośbą
                print(f">>> [TEST] Przechwycono hasło proxy dla {username}: {password}")
                self.model.log(f"Hasło proxy zostało podane (tryb testowy).")
            
            # Tu nastąpi faktyczne wywołanie skryptów
            def task():
                # Krok 1: Inicjalizacja (pobranie certyfikatów)
                if not self.model.init_system():
                    self.refresh_ui()
                    messagebox.showerror("Błąd", "Nie udało się pobrać certyfikatów.")
                    return

                # Krok 2: Logowanie i otwarcie sesji
                if self.model.open_session():
                    self.refresh_ui()
                    messagebox.showinfo("KSeF", "Pomyślnie zalogowano i otwarto sesję.")
                else:
                    self.refresh_ui()
                    messagebox.showerror("Błąd", "Nie udało się zalogować. Sprawdź logi w konsoli.")
            
            threading.Thread(target=task).start()

        # Sprawdzamy w configu czy proxy jest aktywne
        if self.model.config.proxy_enabled:
            # Wyświetlamy okienko pop-up
            ProxyPasswordDialog(self.view, username, on_proxy_confirm)
        else:
            # Pomijamy okienko i idziemy dalej
            self.model.log("Proxy wyłączone w konfiguracji. Przechodzę do bezpośredniego logowania.")
            on_proxy_confirm()

    def handle_check_status(self):
        self.model.check_session_status()
        self.refresh_ui()

    def handle_refresh_token(self, silent=False):
        def task():
            if self.model.refresh_session_token():
                self.refresh_ui()
                if not silent:
                    messagebox.showinfo("KSeF", "Token został odświeżony.")
            self.refresh_ui()
        threading.Thread(target=task).start()

    def handle_logout(self):
        def task():
            if self.model.logout():
                self.refresh_ui()
                messagebox.showinfo("KSeF", "Sesja została zamknięta.")
            self.refresh_ui()
        threading.Thread(target=task).start()

    # --- AKCJE SPRZEDAŻY ---
    def handle_convert_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            template = self.view.views['sales'].combo_mapping.get()
            def task():
                self.model.convert_excel_to_xml(file_path, template)
                self.refresh_ui()
                messagebox.showinfo("Sukces", f"Przekonwertowano plik za pomocą {template}\n(Funkcja mapowania w przygotowaniu)")
            threading.Thread(target=task).start()

    def handle_send_xml(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if file_path:
            def task():
                if self.model.send_xml_invoice(file_path):
                    self.refresh_ui()
                    messagebox.showinfo("Sukces", "Faktura wysłana do KSeF.")
                self.refresh_ui()
            threading.Thread(target=task).start()

    def handle_check_upo(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")], title="Wybierz wysłany plik XML, aby pobrać UPO")
        if file_path:
            def task():
                self.model.check_status_upo(file_path)
                self.refresh_ui()
            threading.Thread(target=task).start()

    def handle_preview(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")], title="Wybierz plik XML do wizualizacji")
        if file_path:
            self.model.log(f"Generowanie wizualizacji dla {file_path}...")
            try:
                from ksef_client.views.ksef_viz import run_visualization
                # Wizualizacja zapisuje HTML i może go otworzyć
                if run_visualization(file_path, theme="corporate"):
                    self.model.log("✅ Wizualizacja wygenerowana.")
                    # Tu można dodać automatyczne otwarcie w przeglądarce
            except Exception as e:
                self.model.log(f"❌ Bląd wizualizacji: {e}", "ERROR")
            self.refresh_ui()

    # --- AKCJE ZAKUPÓW ---
    def handle_sync_purchases(self):
        def task():
            if self.model.fetch_purchases():
                self.refresh_ui()
                messagebox.showinfo("KSeF", "Pobrano listę faktur zakupowych.")
            self.refresh_ui()
        threading.Thread(target=task).start()

    def handle_download_xml(self):
        # W modelu można dodać metodę pobierania konkretnych XMLi
        self.model.log("Pobieranie plików XML (funkcja w przygotowaniu)...")
        self.refresh_ui()

    def handle_export_excel(self):
        def task():
            if self.model.export_purchases_to_excel():
                self.refresh_ui()
                messagebox.showinfo("Sukces", "Zestawienie Excel zostało wygenerowane w folderze reports.")
            self.refresh_ui()
        threading.Thread(target=task).start()
