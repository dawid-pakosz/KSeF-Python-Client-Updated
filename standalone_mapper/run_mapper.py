import os
import sys

# Dodaj bieżący folder do path, aby importy działały
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from template_mapper import TemplateMapper

import argparse

def main():
    parser = argparse.ArgumentParser(description="ACC Template Mapper CLI")
    parser.add_argument("excel_path", nargs='?', help="Ścieżka do pliku Excel (.xlsx)")
    parser.add_argument("--type", choices=["ACC_PLN_PROSTA", "ACC_MULTI", "ACC_EUR"], default="ACC_PLN_PROSTA", help="Typ mapowania")
    args = parser.parse_args()

    # Dynamic base directory (two levels up from standalone_mapper)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    rules_path = os.path.join(base_dir, "resources", "technical_rules.json")
    
    mapper = TemplateMapper(rules_path)

    if args.excel_path:
        # Konwersja konkretnego pliku
        excel_path = os.path.abspath(args.excel_path)
        xml_path = excel_path.replace(".xlsx", "_mapped.xml")
        print(f"--- Przetwarzam: {os.path.basename(excel_path)} (Tryb: {args.type}) ---")
        try:
            generated = mapper.create_xml(excel_path, xml_path, mapping_type=args.type)
            print(f"[OK] Sukces! Wygenerowano: {generated}")
        except Exception as e:
            print(f"[BŁĄD]: {e}")
    else:
        # Domyślny test dla plików wzorcowych
        excel_dir = os.path.join(base_dir, "wzory", "excel_input", "ACC_FAKTURA_PLN_PROSTA")
        files = ["2025-10-FV03.xlsx", "2025-10-FV04.xlsx"]
        print(f"--- Uruchamiam test domyślny (ACC PLN Prosta) ---")
        for f in files:
            p = os.path.join(excel_dir, f)
            try:
                gen = mapper.create_xml(p, p.replace(".xlsx", "_mapped.xml"))
                print(f"[OK] {f} -> {os.path.basename(gen)}")
            except Exception as e:
                print(f"[BŁĄD] {f}: {e}")

if __name__ == "__main__":
    main()
