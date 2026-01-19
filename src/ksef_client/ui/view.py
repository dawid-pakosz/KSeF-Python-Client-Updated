import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
import os

# Konfiguracja podstawowa
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Stylistyka V5.7 Professional
FONT_UI = ("Segoe UI", 13)
FONT_BOLD = ("Segoe UI", 13, "bold")
FONT_TITLE_MAIN = ("Segoe UI", 22, "bold") 
FONT_DASH_TITLE = ("Segoe UI", 28, "bold")
FONT_SMALL = ("Segoe UI", 11)
CORNER_RADIUS = 10
HEADER_HEIGHT = 85
SIDEBAR_WIDTH = 285 
SIDEBAR_PADX = 40 

class NavButton(ctk.CTkButton):
    def __init__(self, master, text, icon_text, command, **kwargs):
        display_text = f"  {icon_text}   {text}"
        
        params = {
            "corner_radius": 0,
            "height": 52,
            "fg_color": "transparent",
            "text_color": ("gray10", "gray90"),
            "hover_color": ("gray75", "gray25"),
            "anchor": "w",
            "font": FONT_UI
        }
        params.update(kwargs)
        
        super().__init__(master, text=display_text, command=command, **params)

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, callbacks, **kwargs):
        super().__init__(master, corner_radius=0, fg_color=("gray95", "gray5"), **kwargs)
        
        self.logo_frame = ctk.CTkFrame(self, height=HEADER_HEIGHT, corner_radius=0, fg_color="transparent")
        self.logo_frame.pack(fill="x")
        self.logo_frame.pack_propagate(False)

        self.logo_label = ctk.CTkLabel(self.logo_frame, text="KSeF App", font=FONT_TITLE_MAIN)
        self.logo_label.pack(side="left", padx=SIDEBAR_PADX)

        self.sep = ctk.CTkFrame(self, height=1, fg_color=("gray85", "gray20"))
        self.sep.pack(fill="x")

        self.nav_buttons = {}
        
        self.btn_dash = NavButton(self, text="Dashboard", icon_text="🏠", command=lambda: callbacks['menu']("session"))
        self.btn_dash.pack(fill="x", pady=(40, 0))
        self.nav_buttons["session"] = self.btn_dash

        self.btn_sales = NavButton(self, text="Invoices Sales", icon_text="📤", command=lambda: callbacks['menu']("sales"))
        self.btn_sales.pack(fill="x", pady=0)
        self.nav_buttons["sales"] = self.btn_sales

        self.btn_purchases = NavButton(self, text="Invoices Purchase", icon_text="📥", command=lambda: callbacks['menu']("purchases"))
        self.btn_purchases.pack(fill="x", pady=0)
        self.nav_buttons["purchases"] = self.btn_purchases

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="x", pady=10)

        self.btn_login = NavButton(self.bottom_frame, text="Login / Open Session", icon_text="🔑", 
                                   command=callbacks['session_actions']['login'])
        self.btn_login.pack(fill="x", pady=(20, 0))

        self.theme_btn = NavButton(self.bottom_frame, text="Toggle Theme", icon_text="🌓", command=self.toggle_theme)
        self.theme_btn.pack(fill="x")

    def set_active_tab(self, tab_name):
        ACTIVE_BG = "#0066cc"
        ACTIVE_TEXT = "white"
        
        for name, btn in self.nav_buttons.items():
            if name == tab_name:
                btn.configure(fg_color=ACTIVE_BG, text_color=ACTIVE_TEXT, hover_color="#0052a3")
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray75", "gray25"))

    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        new_mode = "Dark" if current == "Light" else "Light"
        ctk.set_appearance_mode(new_mode)

class TopHeader(ctk.CTkFrame):
    def __init__(self, master, model, **kwargs):
        super().__init__(master, height=HEADER_HEIGHT, corner_radius=0, fg_color=("white", "gray10"), border_width=0, **kwargs)
        self.model = model
        self.pack_propagate(False)

        self.title_container = ctk.CTkFrame(self, fg_color="transparent")
        self.title_container.pack(side="left", fill="both", expand=True, padx=40)
        
        self.lbl_title = ctk.CTkLabel(self.title_container, text=f"Witaj!", font=FONT_TITLE_MAIN)
        self.lbl_title.pack(side="left", expand=False)

    def set_title(self, text):
        self.lbl_title.configure(text=text)

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, model, callbacks, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.model = model
        
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.4, anchor="center")

        self.title = ctk.CTkLabel(self.center_frame, text="KSeF Desktop Client", font=FONT_DASH_TITLE)
        self.title.pack(pady=10)

        self.desc = ctk.CTkLabel(self.center_frame, text="Professional tool for invoice management.\nWelcome back! Use the sidebar button to\nopen a secure session with KSeF.", font=FONT_UI, text_color="gray")
        self.desc.pack(pady=(0, 40))

class SalesView(ctk.CTkFrame):
    def __init__(self, master, callbacks, mapping_templates, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        BTN_COLOR = "#0066cc"
        BTN_HOVER = "#0052a3"

        self.toolbar = ctk.CTkFrame(self, height=60, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=25, pady=(20, 15))

        self.btn_convert = ctk.CTkButton(self.toolbar, text="Excel -> XML", command=callbacks['convert'], corner_radius=8, fg_color=BTN_COLOR, hover_color=BTN_HOVER)
        self.btn_convert.pack(side="left", padx=5)

        self.btn_send = ctk.CTkButton(self.toolbar, text="Send XML", command=callbacks['send_xml'], corner_radius=8, fg_color=BTN_COLOR, hover_color=BTN_HOVER)
        self.btn_send.pack(side="left", padx=5)

        self.btn_upo = ctk.CTkButton(self.toolbar, text="Check UPO", command=callbacks['check_upo'], corner_radius=8, fg_color=BTN_COLOR, hover_color=BTN_HOVER)
        self.btn_upo.pack(side="left", padx=5)

        self.btn_viz = ctk.CTkButton(self.toolbar, text="Preview", command=callbacks['preview'], corner_radius=8, fg_color=BTN_COLOR, hover_color=BTN_HOVER)
        self.btn_viz.pack(side="left", padx=5)

        self.combo_mapping = ctk.CTkOptionMenu(self.toolbar, values=mapping_templates, width=200, corner_radius=8)
        self.combo_mapping.pack(side="right", padx=5)

        self.table_container = ctk.CTkScrollableFrame(self, corner_radius=10, border_width=1, border_color=("gray85", "gray20"))
        self.table_container.pack(fill="both", expand=True, padx=30, pady=10)
        
        self.table_label = ctk.CTkLabel(self.table_container, text="[ List of sent invoices will appear here ]", font=FONT_UI, text_color="gray")
        self.table_label.pack(expand=True, pady=100)

class PurchasesView(ctk.CTkFrame):
    def __init__(self, master, callbacks, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        BTN_COLOR = "#0066cc"
        BTN_HOVER = "#0052a3"

        self.toolbar = ctk.CTkFrame(self, height=60, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=25, pady=(20, 15))

        self.btn_sync = ctk.CTkButton(self.toolbar, text="Fetch from KSeF", command=callbacks['sync'], corner_radius=8, fg_color=BTN_COLOR, hover_color=BTN_HOVER)
        self.btn_sync.pack(side="left", padx=5)

        self.btn_export = ctk.CTkButton(self.toolbar, text="Export to Excel", command=callbacks['export'], corner_radius=8, fg_color=BTN_COLOR, hover_color=BTN_HOVER)
        self.btn_export.pack(side="left", padx=5)

        self.table_container = ctk.CTkScrollableFrame(self, corner_radius=10, border_width=1, border_color=("gray85", "gray20"))
        self.table_container.pack(fill="both", expand=True, padx=30, pady=10)
        
        self.table_label = ctk.CTkLabel(self.table_container, text="[ List of purchase invoices will appear here ]", font=FONT_UI, text_color="gray")
        self.table_label.pack(expand=True, pady=100)

class KSeFViewV4(ctk.CTk):
    def __init__(self, callbacks, model):
        super().__init__()

        self.callbacks = callbacks
        self.model = model

        self.title("KSeF Desktop Client Professional")
        self.geometry("1400x950")
        self.minsize(1050, 800)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.sidebar = Sidebar(self, callbacks, width=SIDEBAR_WIDTH)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")

        self.header = TopHeader(self, model)
        self.header.grid(row=0, column=1, sticky="ew")

        self.workspace_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.workspace_area.grid(row=1, column=1, sticky="nsew")
        
        self.views = {
            "session": DashboardView(self.workspace_area, model, callbacks['session_actions']),
            "sales": SalesView(self.workspace_area, callbacks['sales_actions'], model.mapping_templates),
            "purchases": PurchasesView(self.workspace_area, callbacks['purchase_actions'])
        }

        self.console_container = ctk.CTkFrame(self.workspace_area, height=180, corner_radius=12, 
                                             fg_color=("white", "gray12"), border_width=1, border_color=("gray85", "gray20"))
        self.console_container.pack(side="bottom", fill="x", padx=30, pady=(0, 30))
        self.console_container.pack_propagate(False)

        self.console_header = ctk.CTkFrame(self.console_container, fg_color="transparent")
        self.console_header.pack(fill="x", padx=15, pady=(8, 0))

        self.status_label = ctk.CTkLabel(self.console_header, text="No Session", font=FONT_BOLD, text_color="#dc3545") # Red (Danger)
        self.status_label.pack(side="left")

        self.console_label = ctk.CTkLabel(self.console_header, text="| Action Summary", font=FONT_BOLD, text_color="gray50")
        self.console_label.pack(side="left", padx=10)

        self.txt_console = ctk.CTkTextbox(self.console_container, fg_color="transparent", font=("Consolas", 11), 
                                         text_color=("gray30", "gray70"), corner_radius=10)
        self.txt_console.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.txt_console.insert("0.0", "KSeF System Ready. Waiting for action...\n")
        self.txt_console.configure(state="disabled")

        self.show_view("session")

    def show_view(self, name):
        self.sidebar.set_active_tab(name)

        if name == "session":
            self.header.set_title(f"Welcome, {self.model.user_name}!")
        elif name == "sales":
            self.header.set_title("Module: Invoices Sales")
        elif name == "purchases":
            self.header.set_title("Module: Invoices Purchase")

        for view in self.views.values():
            view.pack_forget()
        if name in self.views:
            self.console_container.pack_forget()
            self.views[name].pack(fill="both", expand=True)
            self.console_container.pack(side="bottom", fill="x", padx=30, pady=(0, 30))

    def log(self, message):
        self.txt_console.configure(state="normal")
        self.txt_console.insert("end", f"> {message}\n")
        self.txt_console.see("end")
        self.txt_console.configure(state="disabled")

    def update_ui(self, model):
        self.header.set_title(f"Welcome, {model.user_name}!")
        
        # Update session status in Action Summary bar
        if model.is_logged_in:
            self.status_label.configure(text="Session Active", text_color="#28a745") # Green (Success)
        else:
            self.status_label.configure(text="No Session", text_color="#dc3545") # Red (Danger)
