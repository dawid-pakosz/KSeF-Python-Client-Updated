import pandas as pd
import os

def generate_template(output_path):
    print(f"Generowanie szablonu mapowania w: {output_path}")
    
    # Definiujemy strukturę mapowania
    # Kolumny:
    # 1. Sekcja (dla orientacji użytkownika)
    # 2. Nazwa Pola KSeF (opisowa)
    # 3. Sciezka_XML (gdzie to ma trafic w XML KSeF)
    # 4. Typ_Źródła (NAZWA, NAGLOWEK, ADRES, STALA)
    # 5. Wartosc_Mapowania (konkretna nazwa z Excela użytkownika)
    
    data = [
        # Nagłówek XML
        ["NAGŁÓWEK", "Kod Waluty", "Fa/KodWaluty", "STALA", "PLN"],
        ["NAGŁÓWEK", "Data Wystawienia", "Fa/P_1", "NAZWA", "date_issue"],
        ["NAGŁÓWEK", "Numer Faktury", "Fa/P_2", "NAZWA", "invoice_no"],
        
        # Podmiot 2 (Nabywca)
        ["NABYWCA", "NIP Nabywcy", "Podmiot2/DaneIdentyfikacyjne/NIP", "ADRES", "B5"],
        ["NABYWCA", "Nazwa Nabywcy", "Podmiot2/DaneIdentyfikacyjne/Nazwa", "NAZWA", "recipient_info"],
        
        # Pozycje faktury (Tabela) - tutaj użyjemy specjalnego prefixu dla wierszy
        ["WIERSZE", "Opis Usługi", "Fa/FaWiersz/P_7", "NAGLOWEK", "nazwa uslugi"],
        ["WIERSZE", "Ilość", "Fa/FaWiersz/P_8B", "NAGLOWEK", "ilosc"],
        ["WIERSZE", "Jednostka miary", "Fa/FaWiersz/P_8A", "NAGLOWEK", "jm"],
        ["WIERSZE", "Cena Netto", "Fa/FaWiersz/P_9A", "NAGLOWEK", "cena jednostkowa netto eur"],
        ["WIERSZE", "Wartość Netto", "Fa/FaWiersz/P_11", "NAGLOWEK", "wartosc sprzedazy eur"],
        ["WIERSZE", "Stawka VAT", "Fa/FaWiersz/P_12", "NAGLOWEK", "podatek vat stawka"],
    ]
    
    df = pd.DataFrame(data, columns=["Sekcja", "Nazwa Pola KSeF", "Sciezka_XML", "Typ_Źródła", "Wartosc_Mapowania"])
    
    # Tworzymy folder jeśli nie istnieje
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Zapisujemy do Excela
    df.to_excel(output_path, index=False)
    print(f"Sukces! Plik zapisany: {output_path}")

if __name__ == "__main__":
    # Używamy ścieżki w resources
    path = r"c:\Users\Admin\Desktop\Dudek\Python\Projekty\KSeF-Python-Client-V9_Kopia_Toola_z_modulem_Wiz_Po_Poprawkach_1\resources\templates\mapping_template_ACC1.xlsx"
    generate_template(path)
