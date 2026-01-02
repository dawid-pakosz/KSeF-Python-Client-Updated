# KSeF Backend - Profesjonalna Architektura (MVC)

Zreorganizowane repozytorium backendowe oparte na wzorcach projektowych "Enterprise". Logika biznesowa została odseparowana od skryptów narzędziowych i zasobów.

## Struktura Katalogów

- `src/ksef_client/` - Serce aplikacji (kod źródłowy)
    - `api/` - Niskopoziomowy klient API
    - `services/` - Logika biznesowa (AuthService, InvoiceService)
    - `utils/` - Narzędzia (Konfiguracja, Kryptografia, Walidacja)
    - `views/` - Silnik wizualizacji faktur
- `resources/` - Pliki statyczne (Schematy .xsd, Style .xsl)
- `scripts/` - Skrypty CLI dla użytkownika
- `config/` - Pliki konfiguracyjne (.ini, .json)
- `storage/` - Miejsce na dane generowane przez program (Archives, UPO, Output)

## Jak używać narzędzia CLI?

Głównym punktem wejścia jest skrypt `scripts/ksef_tool.py`. Poniżej przykłady użycia:

### 1. Odświeżenie tokena
```bash
python scripts/ksef_tool.py 1 f refresh
```

### 2. Zarządzanie sesją
```bash
python scripts/ksef_tool.py 1 f session open
python scripts/ksef_tool.py 1 f session status
python scripts/ksef_tool.py 1 f session close
```

### 3. Operacje na fakturach
```bash
# Wysyłka
python scripts/ksef_tool.py 1 f invoice send storage/archives/faktura.xml
# Sprawdzenie statusu
python scripts/ksef_tool.py 1 f invoice check storage/archives/faktura.xml
# Pobranie UPO
python scripts/ksef_tool.py 1 f invoice upo storage/archives/faktura.xml
```

### 4. Wizualizacja
```bash
python scripts/ksef_tool.py 1 f viz storage/archives/faktura.xml --lang pl
```

## Porządki
- Stare skrypty `t-XX` zostały przeniesione do `scripts/legacy/`.
- Wygenerowane pliki HTML trafiają teraz automatycznie do `storage/output/`.
