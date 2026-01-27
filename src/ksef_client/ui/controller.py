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
                "import": self.handle_import_excel,
                "remove": self.handle_remove_selected,
                "generate": self.handle_generate_xml,
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
        self.model.log(f"View switched to: {view_name}", level="DEBUG")
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
    def handle_import_excel(self, template):
        file_paths = filedialog.askopenfilenames(filetypes=[("Excel files", "*.xlsx")], title="Wybierz faktury Excel")
        if not file_paths:
            return

        sales_view = self.view.views['sales']

        def task():
            new_items_count = 0
            for file_path in file_paths:
                # Load data using Model -> TemplateMapper
                data = self.model.load_excel_preview(file_path, template)
                
                if data and data['status'] != "BŁĄD":
                    self.model.sales_invoices.append(data)
                    new_items_count += 1
                else:
                    self.model.log(f"Skipped file (error): {os.path.basename(file_path)}", "ERROR")
            
            if new_items_count > 0:
                view_data = self._prepare_sales_view_data()
                sales_view.update_table(view_data)
                self.model.log(f"Imported files: {new_items_count}")
            else:
                messagebox.showwarning("No data", "Failed to import any files.")

        threading.Thread(target=task).start()

    def handle_remove_selected(self):
        sales_view = self.view.views['sales']
        selected_items = sales_view.tree.selection()
        
        if not selected_items:
            return
            
        # Confirm
        if not messagebox.askyesno("Potwierdzenie", f"Czy na pewno usunąć zaznaczone faktury ({len(selected_items)})?"):
            return

        # Treeview returns IIDs. In our case (check update_table), we insert with default IIDs.
        # However, update_table recreates items, so IIDs might change. 
        # But `tree.index(item)` gives the position match. 
        # If we assume Table visual order == Model order (no sorting active), we can use indices.
        
        indices_to_remove = []
        for item in selected_items:
            idx = sales_view.tree.index(item)
            indices_to_remove.append(idx)
            
        # Sort descending to remove without shifting
        indices_to_remove.sort(reverse=True)
        
        removed_count = 0
        for idx in indices_to_remove:
            if 0 <= idx < len(self.model.sales_invoices):
                del self.model.sales_invoices[idx]
                removed_count += 1
                
        # Refresh
        sales_view.update_table(self._prepare_sales_view_data())
        self.model.log(f"Removed invoices: {removed_count}")

    def handle_generate_xml(self):
        # 1. Check if there are items
        if not self.model.sales_invoices:
            messagebox.showwarning("Brak danych", "Najpierw zaimportuj pliki Excel.")
            return
            
        # 2. Iterate and generate
        def task():
            count = 0
            for item in self.model.sales_invoices:
                if item['status'] not in ["NOWA", "ZAŁADOWANY"]:
                    continue # Skip already generated or sent
                    
                path = item['file']
                template = item['template']
                
                # Generate XML
                xml_path = self.model.generate_xml_from_file(path, template)
                
                if xml_path:
                    item['status'] = "XML_GOTOWY"
                    item['xml_path'] = xml_path
                    count += 1
            
            if count > 0:
                self.view.views['sales'].update_table(self._prepare_sales_view_data())
                self.model.log(f"Generated XML for {count} invoices.")
                messagebox.showinfo("Success", f"XML files generated: {count}")
            else:
                self.model.log("No new invoices to process.")

        threading.Thread(target=task).start()

    def _prepare_sales_view_data(self):
        """Helper to format model data for view"""
        view_data = []
        for item in self.model.sales_invoices:
            try:
                row = (
                    item['status'],
                    os.path.basename(item['file']),
                    item['template'],
                    item['p1'].get('nip', ''), item['p1'].get('country', ''), item['p1'].get('name', ''), item['p1'].get('addr', ''),
                    item['p2'].get('nip', ''), item['p2'].get('country', ''), item['p2'].get('name', ''), item['p2'].get('jst', ''), item['p2'].get('gv', ''),
                    item['inv'].get('no', ''), item['inv'].get('date_issued', ''), item['inv'].get('date_service', ''), item['inv'].get('curr', ''),
                    item['inv'].get('net', ''), item['inv'].get('vat', ''), item['inv'].get('gross', ''),
                    item['payment'], item['footer']
                )
                view_data.append(row)
            except Exception as e:
                print(f"Error mapping item to row: {e}")
        return view_data
            # file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")], title="Select Excel file to convert")
            # if file_path:
            #     template = self.view.views['sales'].combo_mapping.get()
            #     def task():
            #         self.model.convert_excel_to_xml(file_path, template)
            #         self.refresh_ui()
            #         messagebox.showinfo("Success", f"Converted using {template}\n(Mapping engine in progress)")
            #     threading.Thread(target=task).start()

    def handle_send_xml(self):
        # 1. Check session
        if not self.model.is_logged_in:
            messagebox.showwarning("Brak sesji", "Musisz być zalogowany do KSeF (Step 0: Login), aby wysłać faktury.")
            return

        # 2. Check for sendable items
        sendable_items = [i for i in self.model.sales_invoices if i.get('status') == 'XML_GOTOWY']
        if not sendable_items:
            messagebox.showinfo("Info", "Brak faktur gotowych do wysyłki (Status: XML_GOTOWY).")
            return

        # 3. Batch send task
        def task():
            success_count = 0
            fail_count = 0
            
            for item in sendable_items:
                xml_path = item.get('xml_path')
                if not xml_path or not os.path.exists(xml_path):
                    item['status'] = "BŁĄD PLIKU"
                    fail_count += 1
                    continue
                
                # Send
                if self.model.send_xml_invoice(xml_path):
                    item['status'] = "WYSŁANA"
                    # Capture ref number if model stores it (currently send_xml_invoice logs it, 
                    # ideally it should return it. Let's assume boolean return for now).
                    # TODO: Enhance model to return ref_no to store in item['ksef_ref']
                    success_count += 1
                else:
                    item['status'] = "BŁĄD WYSYŁKI"
                    fail_count += 1
            
            # Refresh UI
            self.view.views['sales'].update_table(self._prepare_sales_view_data())
            
            # Summary
            if fail_count == 0:
                self.model.log(f"Successfully sent: {success_count} invoices.")
                messagebox.showinfo("Success", f"Sent {success_count} invoices to KSeF.")
            else:
                self.model.log(f"Sent: {success_count}, Errors: {fail_count}.", "WARNING")
                messagebox.showwarning("Send report", f"Success: {success_count}\nErrors: {fail_count}\nCheck logs.")

        threading.Thread(target=task).start()

    def handle_check_upo(self):
        sales_view = self.view.views['sales']
        selected_items = sales_view.tree.selection()
        
        if not selected_items:
            # If nothing selected, maybe fallback to file dialog? Or just warn.
            # Let's fallback to file dialog for flexibility, or warn. 
            # User workflow: Select sent invoice -> Check UPO.
            file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")], title="Wybierz plik XML do sprawdzenia UPO")
            if not file_path:
                return
            xml_path = file_path
        else:
            # Get first selected
            item_idx = sales_view.tree.index(selected_items[0])
            if item_idx < len(self.model.sales_invoices):
                item = self.model.sales_invoices[item_idx]
                xml_path = item.get('xml_path')
                if not xml_path:
                    messagebox.showwarning("Info", "Ta pozycja nie ma wygenerowanego pliku XML.")
                    return
            else:
                return

        def task():
            if self.model.check_status_upo(xml_path):
                # Update status if successful (logic mainly resides in model logs for now, 
                # but technically we could update item['status'] to 'PRZYJĘTA' if model returned specific status)
                self.refresh_ui()
                messagebox.showinfo("Sukces", "Pobrano UPO (szczegóły w logach).")
            else:
                self.refresh_ui()
                messagebox.showerror("Błąd", "Nie udało się pobrać UPO.")
        
        threading.Thread(target=task).start()

    def handle_preview(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")], title="Select XML file for visualization")
        if file_path:
            self.model.log(f"Generating visualization for {file_path}...")
            try:
                from ksef_client.views.ksef_viz import run_visualization
                if run_visualization(file_path, theme="corporate"):
                    self.model.log("Visualization generated.")
            except Exception as e:
                self.model.log(f"Visualization error: {e}", "ERROR")
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
            self.model.log(f"Initializing fetch: {ui_type} for last {days} days...")
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
