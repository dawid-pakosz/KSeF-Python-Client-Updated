import customtkinter as ctk
import os

class ProxyPasswordDialog(ctk.CTkToplevel):
    def __init__(self, master, username, on_confirm, **kwargs):
        super().__init__(master, **kwargs)
        
        self.title("Uwierzytelnianie Proxy AD")
        width = 400
        height = 250
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        
        # Stylistyka
        FONT_UI = ("Segoe UI", 13)
        FONT_BOLD = ("Segoe UI", 13, "bold")
        
        self.on_confirm = on_confirm
        
        # Centrowanie okna względem ekranu
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Zapewnienie, że okno jest na górze
        self.attributes("-topmost", True)
        self.grab_set()  # Modalność
        
        # Kontenery
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Opis
        self.lbl_desc = ctk.CTkLabel(
            self.main_frame, 
            text=f"Wymagane uwierzytelnianie", 
            font=FONT_BOLD,
            justify="center"
        )
        self.lbl_desc.pack(pady=(10, 20))
        
        self.lbl_info = ctk.CTkLabel(
            self.main_frame, 
            text="Wpisz hasło Active Directory, aby odblokować\npołączenie z serwerem KSeF przez proxy.", 
            font=("Segoe UI", 11),
            text_color="gray"
        )
        self.lbl_info.pack(pady=(0, 20))
        
        # Pole hasła
        self.entry_password = ctk.CTkEntry(
            self.main_frame, 
            placeholder_text="Hasło AD...", 
            show="*", 
            width=300,
            height=35
        )
        self.entry_password.pack(pady=10)
        self.entry_password.bind("<Return>", lambda e: self.confirm())
        self.entry_password.focus_set()
        
        # Przycisk
        self.btn_confirm = ctk.CTkButton(
            self.main_frame, 
            text="Zatwierdź i Połącz", 
            command=self.confirm,
            height=40,
            font=FONT_BOLD
        )
        self.btn_confirm.pack(pady=(20, 0))

    def confirm(self):
        password = self.entry_password.get()
        if password:
            self.on_confirm(password)
            self.destroy()
        else:
            self.entry_password.configure(border_color="red")

if __name__ == "__main__":
    # Kod testowy do samodzielnego uruchomienia okienka
    root = ctk.CTk()
    root.withdraw() # Ukrywamy główne okno
    
    def test_callback(pwd):
        print(f"Testowe przechwycenie hasła: {pwd}")
        root.quit()

    dialog = ProxyPasswordDialog(root, "test.user", test_callback)
    root.mainloop()
