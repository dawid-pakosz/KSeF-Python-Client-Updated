import sys
import os

# Dodajemy src do path, aby importy działały
sys.path.append(os.path.join(os.getcwd(), 'src'))

from ksef_client.utils.ksefconfig import Config
from ksef_client.services.mapper_service import MapperService

def test_mapping():
    print("--- TEST MAPOWANIA KSeF ---")
    
    # 1. Konfiguracja (używamy firmy 1)
    cfg = Config(1)
    
    # 2. Inicjalizacja serwisu
    mapper = MapperService(cfg)
    
    # 3. Pliki
    excel_file = r"c:\Users\Admin\Desktop\Dudek\Python\Projekty\KSeF-Python-Client-V9_Kopia_Toola_z_modulem_Wiz_Po_Poprawkach_1\storage\test_mock_invoice.xlsx"
    mapping_name = "acc_pattern_1" # To co stworzyliśmy w config/mappings/
    
    if not os.path.exists(excel_file):
        print(f"Błąd: Nie znaleziono pliku {excel_file}. Uruchom najpierw create_mock_invoice.py")
        return

    print(f"Przetwarzanie pliku: {excel_file}")
    print(f"Użyty wzorzec: {mapping_name}")
    
    try:
        xml_path = mapper.create_xml_invoice(excel_file, mapping_name)
        print(f"✅ SUKCES! Wygenerowano plik XML: {xml_path}")
        
        # Podejrzymy fragment
        with open(xml_path, 'r', encoding='utf-8') as f:
            print("\nPodgląd wygenerowanego XML:")
            print("-" * 30)
            print(f.read())
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ BŁĄD podczas mapowania: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mapping()
