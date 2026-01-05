import sys
import os
import argparse
import json
import datetime

# Add src to path so we can import ksef_client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ksef_client.utils.ksefconfig import Config
from ksef_client.services.auth_service import AuthService
from ksef_client.services.invoice_service import InvoiceService, KSeFError

def main():
    parser = argparse.ArgumentParser(description="KSeF Professional CLI Tool")
    parser.add_argument("firma", type=int, help="Numer firmy (z ksef.ini)")
    parser.add_argument("osoba", choices=["f", "o"], help="Typ (f=firma, o=osoba)")
    
    subparsers = parser.add_subparsers(dest="command", help="Dostępne komendy")

    # Command: init
    subparsers.add_parser("init", help="Wstępna konfiguracja (pobieranie certyfikatów KSeF)")

    # Command: login
    subparsers.add_parser("login", help="Pełne logowanie do KSeF (InitToken)")

    # Command: refresh
    subparsers.add_parser("refresh", help="Odśwież token uwierzytelniający")

    # Command: session
    session_parser = subparsers.add_parser("session", help="Zarządzanie sesją")
    session_parser.add_argument("action", choices=["open", "close", "status"], help="Akcja sesji")

    # Command: invoice
    invoice_parser = subparsers.add_parser("invoice", help="Operacje na fakturach")
    invoice_subparsers = invoice_parser.add_subparsers(dest="action", help="Dostępne akcje")
    
    # Action: generate
    gen_parser = invoice_subparsers.add_parser("generate", help="Generuj testową fakturę XML")
    gen_parser.add_argument("odbiorca", type=int, help="Numer firmy odbiorcy (z ksef.ini)")
    gen_parser.add_argument("--count", type=int, default=1, help="Liczba faktur")

    # Action: send
    send_parser = invoice_subparsers.add_parser("send", help="Wyślij fakturę")
    send_parser.add_argument("file", help="Plik XML")

    # Action: check
    check_parser = invoice_subparsers.add_parser("check", help="Sprawdź status")
    check_parser.add_argument("file", help="Plik XML")

    # Action: upo
    upo_parser = invoice_subparsers.add_parser("upo", help="Pobierz UPO")
    upo_parser.add_argument("file", help="Plik XML")

    # Action: list
    list_parser = invoice_subparsers.add_parser("list", help="Listuj faktury zakupowe (Subject2)")
    list_parser.add_argument("--days", type=int, default=30, help="Liczba dni wstecz")
    list_parser.add_argument("--type", choices=["Subject1", "Subject2"], default="Subject2", help="Typ (S1=Sprzedaż, S2=Zakup)")

    # Action: fetch
    fetch_parser = invoice_subparsers.add_parser("fetch", help="Pobierz fakturę XML po numerze KSeF")
    fetch_parser.add_argument("ksef_number", help="Numer KSeF faktury")

    # Action: export
    export_parser = invoice_subparsers.add_parser("export", help="Eksportuj zestawienie faktur do Excela")
    export_parser.add_argument("--days", type=int, default=30, help="Liczba dni wstecz")
    export_parser.add_argument("--type", choices=["Subject1", "Subject2"], default="Subject2", help="Typ (S1=Sprzedaż, S2=Zakup)")

    # Command: viz
    viz_parser = subparsers.add_parser("viz", help="Wizualizacja faktury")
    viz_parser.add_argument("xml", help="Plik XML")
    viz_parser.add_argument("--lang", choices=["pl", "eng"], default="pl", help="Język")

    args = parser.parse_args()
    
    try:
        cfg = Config(args.firma, args.osoba == 'o', initialize=True)
        
        if args.command == "init":
            auth = AuthService(cfg)
            auth.fetch_certificates()
            print("[OK] Inicjalizacja zakończona pomyślnie.")
            
        elif args.command == "login":
            auth = AuthService(cfg)
            print(">>> Rozpoczynam logowanie (InitToken)...")
            auth.login()
            print("[OK] Zalogowano pomyślnie. Token zapisany.")
            
        elif args.command == "refresh":
            auth = AuthService(cfg)
            new_auth = auth.refresh_token()
            print("[OK] Token odświeżony pomyślnie.")
            
        elif args.command == "session":
            service = InvoiceService(cfg)
            if args.action == "open":
                ref = service.session_open()
                print(f"[OK] Sesja otwarta: {ref}")
            elif args.action == "close":
                service.session_close()
                print("[OK] Sesja zamknięta.")
            elif args.action == "status":
                print(f"Status sesji: {service.session['referenceNumber'] or 'Zamknięta'}")

        elif args.command == "invoice":
            if args.action == "generate":
                from ksef_client.utils.fv import Main as FVGenerator
                cfg2 = Config(args.odbiorca, False, initialize=True)
                FVGenerator().main(cfg, cfg2, args.count)
            else:
                service = InvoiceService(cfg)
                if args.action == "send":
                    ref = service.send_invoice(args.file)
                    print(f"[OK] Faktura wysłana. Ref: {ref}")
                elif args.action == "check":
                    status = service.check_invoice_status(args.file)
                    print(f"Status faktury: {json.dumps(status, indent=2)}")
                elif args.action == "upo":
                    path = service.download_upo(args.file)
                    print(f"[OK] UPO pobrane do: {path}")
                elif args.action == "list":
                    from ksef_client.services.query_service import QueryService
                    qs = QueryService(cfg)
                    print(f">>> Pobieranie listy faktur ({args.type}, {args.days} dni)...")
                    invoices = qs.list_invoices(args.days, args.type)
                    print(f"Znaleziono {len(invoices)} faktur:")
                    for inv in invoices:
                        ksef = inv.get('ksefNumber', 'Brak numeru')
                        date = inv.get('invoicingDate', inv.get('acquisitionTimestamp', 'Brak daty'))
                        amount = inv.get('grossAmount', '0.00')
                        
                        # Try to find any name and NIP in various possible fields
                        subject = inv.get('subjectBy') or inv.get('issuedBy') or inv.get('receivedBy') or {}
                        name = subject.get('name') or subject.get('fullName') or 'Brak nazwy'
                        nip = subject.get('identifier', {}).get('value', 'Brak NIP')
                        
                        print(f"- {ksef} | {date} | {nip} - {name} | {amount} PLN")
                elif args.action == "fetch":
                    from ksef_client.services.query_service import QueryService
                    qs = QueryService(cfg)
                    print(f">>> Pobieranie faktury {args.ksef_number}...")
                    path = qs.download_invoice(args.ksef_number)
                    print(f"[OK] Faktura zapisana w: {path}")
                elif args.action == "export":
                    from ksef_client.services.query_service import QueryService
                    from ksef_client.services.export_service import ExportService
                    qs = QueryService(cfg)
                    es = ExportService(cfg)
                    print(f">>> Pobieranie danych do eksportu ({args.type}, {args.days} dni)...")
                    invoices = qs.list_invoices(args.days, args.type)
                    if not invoices:
                        print("[!] Brak faktur do wyeksportowania.")
                    else:
                        filename = f"zestawienie_{args.type}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                        output_path = cfg.storage_dir / "output" / filename
                        path = es.export_to_excel(invoices, str(output_path))
                        print(f"[OK] Zestawienie zapisane w: {path}")

        elif args.command == "viz":
            from ksef_client.views.ksef_viz import run_visualization
            run_visualization(args.xml, args.lang)

    except KSeFError as e:
        msg = f"[!] Błąd KSeF: {e.msg}"
        print(msg.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
        if e.text: 
            print(e.text.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
    except Exception as e:
        msg = f"[X] Błąd: {e}"
        # Safe print for Windows consoles
        try:
            print(msg)
        except UnicodeEncodeError:
            print(msg.encode('ascii', errors='replace').decode('ascii'))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
