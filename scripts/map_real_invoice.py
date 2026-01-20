import sys
import os

# Dodaj src do path, aby móc importować moduły
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ksef_client.services.mapper_service import MapperService
from ksef_client.utils.ksefconfig import Config

def main():
    if len(sys.argv) < 2:
        print("Użycie: python scripts/map_real_invoice.py <sciezka_do_excela> [nazwa_mapowania]")
        print("Przykład: python scripts/map_real_invoice.py storage/faktura_ksiegowosc.xlsx acc_pattern_1")
        return

    excel_path = sys.argv[1]
    mapping_name = sys.argv[2] if len(sys.argv) > 2 else "acc_pattern_1"

    if not os.path.exists(excel_path):
        print(f"Błąd: Plik nie istnieje: {excel_path}")
        return

    try:
        print(f"--- ROZPOCZYNAM MAPOWANIE ---")
        print(f"Plik wejściowy: {excel_path}")
        print(f"Użyty wzorzec: {mapping_name}")
        
        cfg = Config(firma=1) # Używamy firma1 z ksef.ini jako sprzedawcy
        mapper = MapperService(cfg)
        
        xml_path = mapper.create_xml_invoice(excel_path, mapping_name)
        
        print(f"\n--- SUKCES ---")
        print(f"Wygenerowano plik XML: {xml_path}")
        print("Możesz go teraz otworzyć i sprawdzić poprawność danych.")
        
    except Exception as e:
        print(f"\n--- BŁĄD ---")
        print(f"Wystąpił nieoczekiwany błąd podczas mapowania:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
