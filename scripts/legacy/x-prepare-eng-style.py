import os

# Konfiguracja
SOURCE_FILE = "styl-fa3.xsl"
TARGET_FILE = "styl-fa3-eng.xsl"

# Mapa zamian: "Szukany tekst PL" -> "Tekst PL / ENG"
# Możesz tu dopisywać dowolne tłumaczenia
replacements = {
    # Nagłówki główne
    "<b>SPRZEDAWCA</b>": "<b>SPRZEDAWCA / SELLER</b>",
    "<b>NABYWCA</b>": "<b>NABYWCA / BUYER</b>",
    "e-FAKTURA KSeF": "e-FAKTURA KSeF / e-INVOICE",
    
    # Dane szczegółowe
    "Faktura podstawowa": "Faktura podstawowa / Basic Invoice",
    "Faktura korygująca": "Faktura korygująca / Correction Invoice",
    
    # Pola
    "Data wystawienia": "Data wystawienia / Date of issue",
    "Numer faktury": "Numer faktury / Invoice No",
    "Kod waluty": "Kod waluty / Currency code",
    "Kolejny numer faktury": "Kolejny numer faktury / Sequential invoice number",
    
    # Adresy i ID
    "NIP:": "NIP / Tax ID:",
    "Adres:": "Adres / Address:",
    "Kod kraju:": "Kod kraju / Country code:",
    "Nazwa:": "Nazwa / Name:",
    
    # Stopka / Sumy (warto doprecyzować, bo to często w tabelach)
    "Suma": "Suma / Total",
    "Razem": "Razem / Total",
    "Kwota": "Kwota / Amount",
    "Waluta": "Waluta / Currency",
    "Cena jedn": "Cena jedn. / Unit price",
}

def create_english_style():
    print(f"--- TWORZENIE ANGIESLKIEGO STYLU ---")
    
    if not os.path.exists(SOURCE_FILE):
        print(f"BŁĄD: Brak pliku źródłowego: {SOURCE_FILE}")
        return

    print(f"1. Czytanie oryginału: {SOURCE_FILE}")
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    print("2. Aplikowanie tłumaczeń...")
    count = 0
    
    # Prosta zamiana stringów
    for pl, pl_eng in replacements.items():
        if pl in content:
            content = content.replace(pl, pl_eng)
            count += 1
            # print(f"   [OK] {pl} -> {pl_eng}") 
        else:
            # Niektóre frazy mogą być inaczej sformatowane w kodzie XSLT (np. spacje, entery),
            # więc prosta zamiana może ich nie znaleźć. To normalne.
            print(f"   [!] Nie znaleziono frazy (dokładne dopasowanie): '{pl}'")

    print(f"   Dokonano {count} zmian.")

    print(f"3. Zapisywanie nowego pliku: {TARGET_FILE}")
    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("Gotowe. Teraz możesz używać tego pliku w generatorze.")

if __name__ == "__main__":
    create_english_style()
