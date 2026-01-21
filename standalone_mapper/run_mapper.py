import sys
import os
from mapper_engine import StandaloneMapper

def main():
    if len(sys.argv) < 2:
        print("\n--- KSeF Standalone Mapper ---")
        print("Użycie: python run_mapper.py <sciezka_do_pliku.xlsx>")
        return

    excel_file = sys.argv[1]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    settings_path = os.path.join(base_dir, "settings.json")
    mapping_path = os.path.join(base_dir, "mapping_config.json")

    if not os.path.exists(excel_file):
        print(f"Błąd: Nie znaleziono pliku Excel: {excel_file}")
        return

    try:
        mapper = StandaloneMapper(settings_path, mapping_path)
        print(f"Przetwarzanie: {excel_file}...")
        
        xml_path = mapper.create_xml(excel_file)
        
        print(f"\n[SUKCES] Wygenerowano plik: {xml_path}")
        print("Możesz go teraz sprawdzić w notatniku lub wczytać do KSeF.")
        
    except Exception as e:
        print(f"\n[BŁĄD] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
