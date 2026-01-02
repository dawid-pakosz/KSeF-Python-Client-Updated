import sys
import os
from lxml import etree

def generate_visualization(xml_path, xsl_path, output_html_path):
    print(f"--- GENERATOR WIZUALIZACJI ---")
    print(f"1. Wczytywanie XML:  {xml_path}")
    if not os.path.exists(xml_path):
        print(f"BŁĄD: Plik XML nie istnieje: {xml_path}")
        return

    print(f"2. Wczytywanie XSLT: {xsl_path}")
    if not os.path.exists(xsl_path):
        print(f"BŁĄD: Plik XSLT nie istnieje: {xsl_path}")
        return

    try:
        # Parsowanie XML i XSLT
        dom = etree.parse(xml_path)
        xslt = etree.parse(xsl_path)
        transform = etree.XSLT(xslt)
        # Pass local XSD for schema-krajow to avoid remote fetch
        newdom = transform(dom, schema_krajow=etree.XSLT.strparam('KodyKrajow_v10-0E.xsd'))
        
        # Zapis do pliku
        # method="html" zapewnia poprawne tagi HTML (np. <br> zamiast <br/> co przeglądarki wolą)
        html_content = etree.tostring(newdom, pretty_print=True, method="html", encoding="unicode")
        
        print(f"4. Zapisywanie wyniku do: {output_html_path}")
        with open(output_html_path, "w", encoding="utf-8") as f:
            # Dodajemy doctype dla pewności poprawnego wyświetlania polskich znaków i styli
            if not html_content.strip().startswith("<!DOCTYPE"):
                 f.write("<!DOCTYPE html>\n")
            f.write(html_content)
            
        print(f"--- SUKCES! ---")
        print(f"Otwórz plik '{output_html_path}' w przeglądarce, aby zobaczyć wizualizację.")
        
    except Exception as e:
        print(f"\n!!! BŁĄD PODCZAS GENEROWANIA !!!")
        print(f"{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Domyślne pliki - jeśli nie podano argumentów
    # Możesz zmienić te nazwy na swoje pliki
    
    # 1. Szukamy jakiegoś pliku XML w katalogu, jeśli nie podano konkretnego
    target_xml = "9999999999-1234567890-1766397567.203448.xml" 
    
    # 2. Nasz nowy styl
    target_xsl = "styl-fa3-eng.xsl"
    
    # 3. Wynik
    target_html = "faktura-wizualizacja.html"

    # Obsługa argumentów z linii poleceń (opcjonalnie)
    # python x-viz-generator.py [plik.xml]
    if len(sys.argv) > 1:
        target_xml = sys.argv[1]

    generate_visualization(target_xml, target_xsl, target_html)
