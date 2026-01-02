import requests
import os

urls = {
    "WspolneSzablonyWizualizacji_v12-0E.xsl": "http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2022/01/07/eD/DefinicjeSzablony/WspolneSzablonyWizualizacji_v12-0E.xsl",
    "KodyKrajow_v10-0E.xsd": "http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2022/01/05/eD/DefinicjeTypy/KodyKrajow_v10-0E.xsd"
}

def download_dependencies():
    print("--- POBIERANIE ZALEŻNOŚCI XSLT (OFFLINE) ---")
    
    for filename, url in urls.items():
        if os.path.exists(filename):
            print(f"[OK] Plik już istnieje: {filename}")
            continue
            
        print(f"Pobieranie: {filename} z {url} ...")
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            with open(filename, "wb") as f:
                f.write(r.content)
            print(f"[SUKCES] Pobrano {filename}")
        except Exception as e:
            print(f"[BŁĄD] Nie udało się pobrać {filename}: {e}")

if __name__ == "__main__":
    download_dependencies()
