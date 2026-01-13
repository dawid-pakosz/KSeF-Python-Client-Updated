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
- `storage/` - Miejsce na dane generowane przez program
    - `sent/` - Faktury wysłane i wygenerowane (XML, UPO, Wizualizacje)
    - `received/` - Faktury pobrane z KSeF (XML, Wizualizacje)
    - `reports/` - Zestawienia Excel i inne raporty

## Jak używać narzędzia CLI?

Głównym punktem wejścia jest skrypt `scripts/ksef_tool.py`. Poniżej przykłady użycia:

### 0. Pierwsze uruchomienie (Inicjalizacja)
Musisz najpierw pobrać certyfikaty publiczne KSeF:
```bash
python scripts/ksef_tool.py 1 f init
```

### 1. Logowanie i odświeżanie sesji
```bash
# Pełne logowanie 
python scripts/ksef_tool.py 1 f login

# Odświeżenie tokena (jeśli sesja jeszcze trwa)
python scripts/ksef_tool.py 1 f refresh
```

### 2. Generowanie i wysyłka faktur
Możesz teraz generować testowe faktury bezpośrednio za pomocą narzędzia:
```bash
# Generowanie 1 faktury dla odbiorcy (firma nr 2)
# Plik zostanie zapisany w storage/sent/xml/
python scripts/ksef_tool.py 1 f invoice generate 2

# Wyślij wygenerowaną fakturę
python scripts/ksef_tool.py 1 f invoice send storage/sent/xml/9999999999-1234567890-XXXXXXXX.xml
```

### 3. Pobieranie faktur (Zakup/Sprzedaż)
Możesz listować i pobierać faktury, które zostały wystawione na Twój NIP przez innych dostawców:
```bash
# Listuj faktury zakupowe (Subject2) z ostatnich 30 dni
python scripts/ksef_tool.py 1 f invoice list

# Pobierz konkretną fakturę do storage/received/xml/
python scripts/ksef_tool.py 1 f invoice fetch 9999999999-20240105-XXXXXXXXXXXX-XX

# Eksportuj zestawienie do Excela (zapisane w storage/reports/)
python scripts/ksef_tool.py 1 f invoice export --type Subject1 --days 30
```

### 4. Zarządzanie sesją
```bash
python scripts/ksef_tool.py 1 f session open
python scripts/ksef_tool.py 1 f session status
python scripts/ksef_tool.py 1 f session close
```

### 3. Operacje na fakturach
```bash
# Wysyłka
python scripts/ksef_tool.py 1 f invoice send storage/sent/xml/faktura.xml
# Sprawdzenie statusu
python scripts/ksef_tool.py 1 f invoice check storage/sent/xml/faktura.xml
# Pobranie UPO (zapisane w storage/sent/upo/)
python scripts/ksef_tool.py 1 f invoice upo storage/sent/xml/faktura.xml
```

### 4. Wizualizacja
```bash
# Wizualizacja faktury wysłanej (zapisana w storage/sent/viz/)
python scripts/ksef_tool.py 1 f viz storage/sent/xml/faktura.xml --lang pl

# Wizualizacja faktury pobranej (zapisana w storage/received/viz/)
python scripts/ksef_tool.py 1 f viz storage/received/xml/faktura.xml --lang pl
```

## Porządki
- Stare skrypty `t-XX` zostały przeniesione do `scripts/legacy/`.
- Wygenerowane wizualizacje HTML trafiają do folderów `viz/` wewnątrz `storage/sent/` lub `storage/received/`.
