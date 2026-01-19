import customtkinter as ctk
import os

class ProxyPasswordDialog(ctk.CTkToplevel):
    def __init__(self, master, username, on_confirm, **kwargs):
        super().__init__(master, **kwargs)
        
        self.title("Proxy AD Authentication")
        width = 460  # slightly wider to accommodate eye button
        height = 260  # a bit taller for better spacing
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        
        # Styling
        FONT_UI = ("Segoe UI", 13)
        FONT_BOLD = ("Segoe UI", 13, "bold")
        
        self.on_confirm = on_confirm
        
        # Center window on screen
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Ensure window is on top
        self.attributes("-topmost", True)
        self.grab_set()  # Modal
        
        # Containers
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Description
        self.lbl_desc = ctk.CTkLabel(
            self.main_frame, 
            text=f"Authentication Required", 
            font=FONT_BOLD,
            justify="center"
        )
        self.lbl_desc.pack(pady=(10, 20))
        
        self.lbl_info = ctk.CTkLabel(
            self.main_frame, 
            text="Please enter your Active Directory password\nto unlock the KSeF server connection.", 
            font=("Segoe UI", 11),
            text_color="gray"
        )
        self.lbl_info.pack(pady=(0, 20))
        
        # Password container
        self.pass_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.pass_container.pack(fill="x", pady=10)

        # Invisible spacer to balance the eye button on the right
        # Button width (35) + padx (5) = 40
        self.spacer = ctk.CTkLabel(self.pass_container, text="", width=40)
        self.spacer.pack(side="left", expand=True)

        # Password entry
        self.entry_password = ctk.CTkEntry(
            self.pass_container, 
            placeholder_text="Password...", 
            show="*", 
            width=260,
            height=35
        )
        self.entry_password.pack(side="left")
        self.entry_password.bind("<Return>", lambda e: self.confirm())
        self.entry_password.focus_set()

        # Show/Hide button
        self.btn_show_pass = ctk.CTkButton(
            self.pass_container,
            text="👁️",
            width=35,
            height=35,
            fg_color="transparent",
            hover_color=("gray85", "gray25"),
            text_color=("gray20", "gray80"),
            command=self.toggle_password
        )
        self.btn_show_pass.pack(side="left", padx=(5, 0), expand=True)
        
        # Button
        self.btn_confirm = ctk.CTkButton(
            self.main_frame, 
            text="Confirm and Connect", 
            command=self.confirm,
            height=40,
            font=FONT_BOLD
        )
        self.btn_confirm.pack(pady=(20, 0))

    def toggle_password(self):
        """Switches password visibility."""
        if self.entry_password.cget("show") == "*":
            self.entry_password.configure(show="")
            self.btn_show_pass.configure(text_color="#0066cc") # Blue highlight when visible
        else:
            self.entry_password.configure(show="*")
            self.btn_show_pass.configure(text_color=("gray20", "gray80"))

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
