import tkinter as tk
from tkinter import filedialog, messagebox, ttk, font
import customtkinter as ctk
from PIL import Image
import os
import sys

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

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def load_icon(name, size=(24, 24), h_margin=15):
    """Loads a PNG icon, generates dark mode version, and adds horizontal margin"""
    icon_path = os.path.join("resources", "icons", f"{name}.png")
    if not os.path.exists(icon_path):
        return None
    
    # Load original
    img_orig = Image.open(icon_path).convert("RGBA")
    img_orig = img_orig.resize(size, Image.Resampling.LANCZOS)
    
    # Create a wider transparent canvas to "pad" the icon from the left
    canvas_w = size[0] + h_margin
    canvas_h = size[1]
    
    def process_image(img):
        # Create white version if needed for dark mode
        # (This is a simplified version of what we had before)
        r, g, b, a = img.split()
        white_channel = a.point(lambda _: 255)
        # Note: We can check if we want white or original. 
        # But for dark mode we definitely want white.
        return Image.merge("RGBA", (white_channel, white_channel, white_channel, a))

    img_light_final = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    img_light_final.paste(img_orig, (h_margin, 0), img_orig)
    
    img_dark_pre = process_image(img_orig)
    img_dark_final = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    img_dark_final.paste(img_dark_pre, (h_margin, 0), img_dark_pre)
    
    return ctk.CTkImage(light_image=img_light_final, dark_image=img_dark_final, size=(canvas_w, canvas_h))

class NavButton(ctk.CTkButton):
    def __init__(self, master, text, icon_text=None, image=None, command=None, **kwargs):
        if image:
            display_text = f" {text}" # Small space after padded image
        else:
            display_text = f"  {icon_text}   {text}" if icon_text else text
        
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
        
        super().__init__(master, text=display_text, image=image, command=command, **params)

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, callbacks, model, **kwargs):
        super().__init__(master, corner_radius=0, fg_color=("gray95", "gray5"), **kwargs)
        self.model = model
        
        self.logo_frame = ctk.CTkFrame(self, height=HEADER_HEIGHT, corner_radius=0, fg_color="transparent")
        self.logo_frame.pack(fill="x")
        self.logo_frame.pack_propagate(False)

        # Container for logo and version
        self.logo_container = ctk.CTkFrame(self.logo_frame, fg_color="transparent")
        self.logo_container.pack(side="left", padx=SIDEBAR_PADX)

        self.logo_label = ctk.CTkLabel(self.logo_container, text="KSeF App", font=FONT_TITLE_MAIN)
        self.logo_label.pack(side="top", anchor="w")
        
        self.version_label = ctk.CTkLabel(self.logo_container, text=f"ver: {self.model.app_version}", 
                                         font=("Segoe UI", 11), text_color="gray")
        self.version_label.pack(side="top", anchor="w")

        self.sep = ctk.CTkFrame(self, height=1, fg_color=("gray85", "gray20"))
        self.sep.pack(fill="x")

        # Custom Icons
        icon_send = load_icon("paper-plane", size=(20, 20))
        icon_inbox = load_icon("inbox", size=(20, 20))
        icon_home = load_icon("home", size=(20,20))
        icon_key = load_icon("key", size=(20,20))
        icon_theme_mode = load_icon("theme", size=(20,20))
        
        self.nav_buttons = {}

        self.btn_dash = NavButton(self, text="Dashboard", image=icon_home, command=lambda: callbacks['menu']("session"))
        self.btn_dash.pack(fill="x", pady=(40, 0))
        self.nav_buttons["session"] = self.btn_dash


        self.btn_sales = NavButton(self, text="Send Invoices", image=icon_send, command=lambda: callbacks['menu']("sales"))
        self.btn_sales.pack(fill="x", pady=0)
        self.nav_buttons["sales"] = self.btn_sales

        self.btn_purchases = NavButton(self, text="Received Invoices", image=icon_inbox, command=lambda: callbacks['menu']("purchases"))
        self.btn_purchases.pack(fill="x", pady=0)
        self.nav_buttons["purchases"] = self.btn_purchases

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="x", pady=10)

        self.btn_login = NavButton(self.bottom_frame, text="Login / Open Session", image=icon_key, command=callbacks['session_actions']['login'])
        self.btn_login.pack(fill="x", pady=(5, 0))

        self.theme_btn = NavButton(self.bottom_frame, text="Toggle Theme", image=icon_theme_mode, command=self.toggle_theme)
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
        
        # Notify the root window to refresh non-native components (like Treeview)
        if hasattr(self.master, "handle_theme_change"):
            self.after(10, self.master.handle_theme_change) 

class TopHeader(ctk.CTkFrame):
    def __init__(self, master, model, **kwargs):
        super().__init__(master, height=HEADER_HEIGHT, corner_radius=0, fg_color=("white", "gray10"), border_width=0, **kwargs)
        self.model = model
        self.pack_propagate(False)

        self.title_container = ctk.CTkFrame(self, fg_color="transparent")
        self.title_container.pack(side="left", fill="both", expand=True, padx=40)
        
        # User Welcome and Environment Badge
        self.info_container = ctk.CTkFrame(self.title_container, fg_color="transparent")
        self.info_container.pack(side="left", fill="y", pady=15)

        self.lbl_title = ctk.CTkLabel(self.info_container, text=f"Witaj!", font=FONT_TITLE_MAIN)
        self.lbl_title.pack(side="top", anchor="w")
        
        env_text = self.model.env
        #color = "#dc3545" if "PROD" in env_text else "#28a745" if "TEST" in env_text else "#ffc107"
        self.lbl_env = ctk.CTkLabel(self.info_container, text=f"Environment: {env_text}", 
                                   font=("Segoe UI", 12, "bold"), text_color="gray")
        self.lbl_env.pack(side="top", anchor="w")

    def set_title(self, text):
        self.lbl_title.configure(text=text)

def setup_treeview_styles():
    """Konfiguracja stylów dla ttk.Treeview - Pełna obsługa motywów."""
    style = ttk.Style()
    
    # Próba wymuszenia odświeżenia stylu
    style.theme_use("default")
    
    appearance = ctk.get_appearance_mode().lower()
    
    if appearance == "dark":
        bg_color = "#1d1d1d"
        fg_color = "#e1e1e1"
        header_bg = "#2b2b2b"
        header_fg = "#ffffff"
        row_even = "#252525"
        row_odd = "#1d1d1d"
    else:
        bg_color = "#ffffff"
        fg_color = "#000000"
        header_bg = "#f0f0f0"
        header_fg = "#000000"
        row_even = "#f9f9f9"
        row_odd = "#ffffff"

    selected_bg = "#0066cc"
    
    style.configure("Treeview", 
        background=bg_color,
        foreground=fg_color,
        fieldbackground=bg_color,
        rowheight=35,
        font=("Segoe UI", 11),
        borderwidth=1,       # Dodanie obramowania
        relief="flat"
    )
    
    style.configure("Treeview.Heading", 
        background=header_bg,
        foreground=header_fg,
        relief="groove",      # Efekt linii pionowych w nagłówkach
        borderwidth=1,
        font=("Segoe UI", 11, "bold")
    )
    
    style.map("Treeview.Heading",
        background=[('active', '#0052a3')],
        foreground=[('active', 'white')]
    )

    style.map("Treeview",
        background=[('selected', selected_bg)],
        foreground=[('selected', 'white')]
    )
    
    return row_even, row_odd

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
        self.callbacks = callbacks
        self.mapping_templates = mapping_templates
        
        BTN_COLOR = "#0066cc"
        BTN_HOVER = "#0052a3"

        self.toolbar = ctk.CTkFrame(self, height=60, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=25, pady=(20, 15))

        self.btn_import = ctk.CTkButton(self.toolbar, text="1. Import XLSX ▾", command=self.show_import_menu, 
                                       corner_radius=8, width=140, fg_color=BTN_COLOR, hover_color=BTN_HOVER)
        self.btn_import.pack(side="left", padx=5)

        

        self.btn_generate = ctk.CTkButton(self.toolbar, text="2. Generate XML", command=callbacks['generate'], corner_radius=8, width=120, fg_color=BTN_COLOR, hover_color=BTN_HOVER)
        self.btn_generate.pack(side="left", padx=5)

        self.btn_send = ctk.CTkButton(self.toolbar, text="3. Send (KSeF)", command=callbacks['send_xml'], corner_radius=8, width=120, fg_color=BTN_COLOR, hover_color=BTN_HOVER)
        self.btn_send.pack(side="left", padx=5)

        self.btn_upo = ctk.CTkButton(self.toolbar, text="Download UPO", command=callbacks['check_upo'], corner_radius=8, width=60, fg_color="#6c757d", hover_color="#5a6268")
        self.btn_upo.pack(side="left", padx=5)

        self.btn_viz = ctk.CTkButton(self.toolbar, text="Create PDF Preview", command=callbacks['preview'], corner_radius=8, width=80, fg_color="#17a2b8", hover_color="#138496")
        self.btn_viz.pack(side="left", padx=5)

        self.btn_remove = ctk.CTkButton(self.toolbar, text="Clear Data", command=callbacks['remove'], corner_radius=8, fg_color="#dc3545", hover_color="#c82333")
        self.btn_remove.pack(side="right", padx=5)

        # Menu dla przycisku importu (zamiast combo_mapping)
        self.import_menu = tk.Menu(self, tearoff=0, font=("Segoe UI", 10), bg="white", fg="black", activebackground=BTN_COLOR)
        for template in mapping_templates:
            self.import_menu.add_command(label=f"Szablon: {template}", 
                                         command=lambda t=template: self.callbacks['import'](t))

        self.table_container = ctk.CTkFrame(self, corner_radius=10, border_width=1, border_color=("gray85", "gray20"))
        self.table_container.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Setup Treeview Styles (shared helper)
        setup_treeview_styles()

        # Define Columns
        self.columns = (
            "status", "file", "template",
            "p1_nip", "p1_country", "p1_name", "p1_addr",
            "p2_nip", "p2_country", "p2_name", "p2_jst", "p2_gv",
            "inv_no", "date_issued", "date_service", "curr",
            "net", "vat", "gross",
            "payment", "footer"
        )
        
        self.tree = ttk.Treeview(self.table_container, columns=self.columns, show="headings", selectmode="extended")
        
        # Headings
        headers = {
            "status": "STATUS", "file": "Plik", "template": "Szablon",
            "p1_nip": "Sprzedawca NIP", "p1_country": "Sprzedawca Kod Kr.", "p1_name": "Sprzedawca Nazwa", "p1_addr": "Sprzedawca Adres",
            "p2_nip": "Nabywca NIP", "p2_country": "Nabywca Kod Kr.", "p2_name": "Nabywca Nazwa", "p2_jst": "Nabywca JST", "p2_gv": "Nabywca GV",
            "inv_no": "Nr Faktury", "date_issued": "Data Wyst.", "date_service": "Data Usł.", "curr": "Waluta",
            "net": "Netto", "vat": "VAT", "gross": "Brutto",
            "payment": "Płatność", "footer": "Stopka"
        }
        
        for col, title in headers.items():
            self.tree.heading(col, text=title, command=lambda c=col: self.sort_column(c, False))
            
        # Column Configuration (Widths)
        self.tree.column("status", width=100, anchor="center", stretch=False)
        self.tree.column("file", width=150, anchor="w", stretch=False)
        self.tree.column("template", width=150, anchor="w", stretch=False)
        
        self.tree.column("p1_nip", width=100, anchor="w", stretch=False)
        self.tree.column("p1_country", width=50, anchor="center", stretch=False)
        self.tree.column("p1_name", width=150, anchor="w", stretch=False)
        self.tree.column("p1_addr", width=200, anchor="w", stretch=False)
        
        self.tree.column("p2_nip", width=100, anchor="w", stretch=False)
        self.tree.column("p2_country", width=50, anchor="center", stretch=False)
        self.tree.column("p2_name", width=150, anchor="w", stretch=False)
        self.tree.column("p2_jst", width=50, anchor="center", stretch=False)
        self.tree.column("p2_gv", width=50, anchor="center", stretch=False)
        
        self.tree.column("inv_no", width=120, anchor="w", stretch=False)
        self.tree.column("date_issued", width=90, anchor="center", stretch=False)
        self.tree.column("date_service", width=90, anchor="center", stretch=False)
        self.tree.column("curr", width=50, anchor="center", stretch=False)
        
        self.tree.column("net", width=90, anchor="e", stretch=False)
        self.tree.column("vat", width=80, anchor="e", stretch=False)
        self.tree.column("gross", width=90, anchor="e", stretch=False)
        
        self.tree.column("payment", width=100, anchor="w", stretch=False)
        self.tree.column("footer", width=150, anchor="w", stretch=False)

        # Scrollbars
        self.vsb = ctk.CTkScrollbar(self.table_container, orientation="vertical", command=self.tree.yview)
        self.hsb = ctk.CTkScrollbar(self.table_container, orientation="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        # Grid Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns", padx=(1, 0))
        self.hsb.grid(row=1, column=0, sticky="ew", pady=(1, 0))
        
        self.table_container.grid_rowconfigure(0, weight=1)
        self.table_container.grid_columnconfigure(0, weight=1)

    def show_import_menu(self):
        # Wyświetl menu pod przyciskiem
        x = self.btn_import.winfo_rootx()
        y = self.btn_import.winfo_rooty() + self.btn_import.winfo_height()
        self.import_menu.post(x, y)

    def sort_column(self, col, reverse):
        """Sorts treeview content when a column header is clicked."""
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        
        # Try numeric sort for amount columns
        if col in ["net", "vat", "gross"]:
            try:
                l.sort(key=lambda t: float(t[0].replace(',', '.')), reverse=reverse)
            except (ValueError, AttributeError):
                l.sort(reverse=reverse)
        else:
            l.sort(reverse=reverse)

        # Rearrange items in sorted order
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
            # Re-apply zebra tags after moving
            tag = 'even' if index % 2 == 0 else 'odd'
            self.tree.item(k, tags=(tag,))

        # Reverse sort next time
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def update_table(self, data_list):
        """
        data_list: List of tuples matching the columns
        """
        # Refresh styles
        setup_treeview_styles()
        
        # Clear current
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not data_list:
            return

        # Insert new (cleaning newlines for visibility)
        for i, row in enumerate(data_list):
            tag = 'even' if i % 2 == 0 else 'odd'
            # Clean newlines from all cells to prevent row overlap
            row_clean = tuple(str(x).replace('\n', ' ').strip() if x is not None else "" for x in row)
            self.tree.insert("", "end", values=row_clean, tags=(tag,))
        
        # Zebra striping
        row_even, row_odd = setup_treeview_styles() # Get colors
        self.tree.tag_configure('even', background=row_even)
        self.tree.tag_configure('odd', background=row_odd)

        if data_list:
            self._autofit_columns()

    def _autofit_columns(self):
        """Automatically adjusts column widths based on content."""
        f = font.Font(family="Segoe UI", size=11)
        for col in self.columns:
            # Measure header
            header_text = self.tree.heading(col)['text']
            max_w = f.measure(header_text) + 25
            
            # Measure items (first 100)
            for item in self.tree.get_children()[:100]:
                val = str(self.tree.set(item, col))
                w = f.measure(val) + 20
                if w > max_w:
                    max_w = w
            
            if max_w > 500: max_w = 500
            if max_w < 50: max_w = 50
            
            # Allow 'p2_name' (Nabywca) to stretch
            is_stretch = (col == "p2_name")
            self.tree.column(col, width=max_w, minwidth=max_w, stretch=is_stretch)

class PurchasesView(ctk.CTkFrame):
    def __init__(self, master, callbacks, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        BTN_COLOR = "#0066cc"
        BTN_HOVER = "#0052a3"

        # Toolbar container
        self.toolbar = ctk.CTkFrame(self, height=80, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=25, pady=(20, 15))

        # Filter controls container
        self.filter_frame = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        self.filter_frame.pack(side="left", padx=5)

        # Invoice type selector (Subject1 = sent, Subject2 = received)
        self.var_invoice_type = ctk.StringVar(value="Sales invoices (Subject1)")
        self.lbl_type = ctk.CTkLabel(self.filter_frame, text="Invoice type:", font=FONT_UI)
        self.lbl_type.pack(side="left", padx=(0, 5))
        self.opt_type = ctk.CTkOptionMenu(
            self.filter_frame,
            values=["Sales invoices (Subject1)", "Purchase invoices (Subject2)"],
            variable=self.var_invoice_type,
            width=180,
            command= lambda _: None 
        )
        self.opt_type.pack(side="left", padx=(0, 10))           

        # Mapping to actual API values (used in controller):
        # "Sales invoices (Subject1)" -> "Subject1"
        # "Purchase invoices (Subject2)" -> "Subject2"


        # Days slider
        self.var_days = ctk.IntVar(value=30)
        self.lbl_days = ctk.CTkLabel(self.filter_frame, text="Period (days):", font=FONT_UI)
        self.lbl_days.pack(side="left", padx=(0, 5))
        self.slider_days = ctk.CTkSlider(
            self.filter_frame,
            from_=1,
            to=90,
            number_of_steps=89,
            variable=self.var_days,
            width=150,
            command=lambda v: self.lbl_days_val.configure(text=f"{int(float(v))} d")
        )
        self.slider_days.pack(side="left")
        self.lbl_days_val = ctk.CTkLabel(self.filter_frame, text="30 d", font=FONT_UI)
        self.lbl_days_val.pack(side="left", padx=(5, 0))

        # Action buttons (Fetch & Export)
        self.btn_clear = ctk.CTkButton(self.toolbar, text="Clear Data", command=self.reset_table, corner_radius=8, fg_color="#dc3545", hover_color="#c82333")
        self.btn_clear.pack(side="right", padx=5)
        self.btn_export = ctk.CTkButton(self.toolbar, text="Export to Excel", command=callbacks['export'], corner_radius=8, fg_color=BTN_COLOR, hover_color=BTN_HOVER)
        self.btn_export.pack(side="right", padx=5)
        self.btn_sync = ctk.CTkButton(self.toolbar, text="Fetch from KSeF", command=callbacks['sync'], corner_radius=8, fg_color=BTN_COLOR, hover_color=BTN_HOVER)
        self.btn_sync.pack(side="right", padx=5)

        # Container for Treeview
        self.table_frame = ctk.CTkFrame(self, corner_radius=10, border_width=1, border_color=("gray85", "gray20"))
        self.table_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # Setup Treeview
        setup_treeview_styles()
        
        self.columns = ("nip", "name", "ksef_no", "inv_no", "date", "net", "gross", "vat", "curr")
        self.tree = ttk.Treeview(self.table_frame, columns=self.columns, show="headings", selectmode="browse")
        
        # Define headings with sorting command
        for col in self.columns:
            display_names = {
                "nip": "NIP", "name": "Nazwa", "ksef_no": "Numer KSeF", 
                "inv_no": "Nr faktury", "date": "Data wyst.", "net": "Netto", 
                "gross": "Brutto", "vat": "VAT", "curr": "Waluta"
            }
            self.tree.heading(col, text=display_names[col], command=lambda _c=col: self.sort_column(_c, False))

        # Column settings
        self.tree.column("nip", width=110, anchor="w", stretch=False)
        self.tree.column("name", width=220, anchor="w")
        self.tree.column("ksef_no", width=300, anchor="w")
        self.tree.column("inv_no", width=120, anchor="w")
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("net", width=90, anchor="e")
        self.tree.column("gross", width=90, anchor="e")
        self.tree.column("vat", width=80, anchor="e")
        self.tree.column("curr", width=50, anchor="center")

        # MODERN SCROLLBARS (ctk instead of ttk)
        self.vsb = ctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
        self.hsb = ctk.CTkScrollbar(self.table_frame, orientation="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        # Layout using grid
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns", padx=(1, 0))
        self.hsb.grid(row=1, column=0, sticky="ew", pady=(1, 0))
        
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

    def update_table(self, data_list):
        """
        data_list: List of tuples (nip, name, ksef_no, inv_no, date, net, gross, vat, currency)
        """
        # Refresh styles based on current theme and get zebra colors
        row_even, row_odd = setup_treeview_styles()

        # Clear current data
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not data_list:
            return

        # Insert new data (cleaning newlines)
        for i, row in enumerate(data_list):
            tag = 'even' if i % 2 == 0 else 'odd'
            row_clean = tuple(str(x).replace('\n', ' ').strip() if x is not None else "" for x in row)
            self.tree.insert("", "end", values=row_clean, tags=(tag,))
        
        # Zebra striping - Dynamically set colors
        self.tree.tag_configure('even', background=row_even)
        self.tree.tag_configure('odd', background=row_odd)

        if data_list:
            self._autofit_columns()

    def _autofit_columns(self):
        """Automatically adjusts column widths based on content."""
        f = font.Font(family="Segoe UI", size=11)
        for col in self.columns:
            header_text = self.tree.heading(col)['text']
            max_w = f.measure(header_text) + 25
            for item in self.tree.get_children()[:100]:
                val = str(self.tree.set(item, col))
                w = f.measure(val) + 20
                if w > max_w:
                    max_w = w
            
            if max_w > 500: max_w = 500
            if max_w < 50: max_w = 50
            
            # Allow 'name' column to stretch to fill remaining space
            is_stretch = (col == "name")
            self.tree.column(col, width=max_w, minwidth=max_w, stretch=is_stretch)

    def refresh_theme(self):
        """Refreshes the table colors without reloading data."""
        row_even, row_odd = setup_treeview_styles()
        self.tree.tag_configure('even', background=row_even)
        self.tree.tag_configure('odd', background=row_odd)

    def reset_table(self):
        """Clears all entries from the table."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def sort_column(self, col, reverse):
        """Sorts treeview content when a column header is clicked."""
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        
        # Try numeric sort for amount columns
        if col in ["net", "gross", "vat"]:
            try:
                l.sort(key=lambda t: float(t[0].replace(',', '.')), reverse=reverse)
            except ValueError:
                l.sort(reverse=reverse)
        else:
            l.sort(reverse=reverse)

        # Rearrange items in sorted order
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
            # Re-apply zebra tags after moving
            tag = 'even' if index % 2 == 0 else 'odd'
            self.tree.item(k, tags=(tag,))

        # Reverse sort next time
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

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

        self.sidebar = Sidebar(self, callbacks, model, width=SIDEBAR_WIDTH)
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

    def handle_theme_change(self):
        """Propagates theme change to all sub-views that need manual refresh."""
        for view in self.views.values():
            if hasattr(view, "refresh_theme"):
                view.refresh_theme()
