import sys
import os
import argparse
import json

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

    # Command: refresh
    subparsers.add_parser("refresh", help="Odśwież token uwierzytelniający")

    # Command: session
    session_parser = subparsers.add_parser("session", help="Zarządzanie sesją")
    session_parser.add_argument("action", choices=["open", "close", "status"], help="Akcja sesji")

    # Command: invoice
    invoice_parser = subparsers.add_parser("invoice", help="Operacje na fakturach")
    invoice_parser.add_argument("action", choices=["send", "check", "upo"], help="Akcja")
    invoice_parser.add_argument("file", help="Plik XML faktury")

    # Command: viz
    viz_parser = subparsers.add_parser("viz", help="Wizualizacja faktury")
    viz_parser.add_argument("xml", help="Plik XML")
    viz_parser.add_argument("--lang", choices=["pl", "eng"], default="pl", help="Język")

    args = parser.parse_args()
    
    try:
        cfg = Config(args.firma, args.osoba == 'o')
        
        if args.command == "refresh":
            auth = AuthService(cfg)
            new_auth = auth.refresh_token()
            print("✅ Token odświeżony pomyślnie.")
            
        elif args.command == "session":
            service = InvoiceService(cfg)
            if args.action == "open":
                ref = service.session_open()
                print(f"✅ Sesja otwarta: {ref}")
            elif args.action == "close":
                service.session_close()
                print("✅ Sesja zamknięta.")
            elif args.action == "status":
                print(f"Status sesji: {service.session['referenceNumber'] or 'Zamknięta'}")

        elif args.command == "invoice":
            service = InvoiceService(cfg)
            if args.action == "send":
                ref = service.send_invoice(args.file)
                print(f"✅ Faktura wysłana. Ref: {ref}")
            elif args.action == "check":
                status = service.check_invoice_status(args.file)
                print(f"Status faktury: {json.dumps(status, indent=2, ensure_ascii=False)}")
            elif args.action == "upo":
                path = service.download_upo(args.file)
                print(f"✅ UPO pobrane do: {path}")

        elif args.command == "viz":
            from ksef_client.views.ksef_viz import run_visualization
            run_visualization(args.xml, args.lang)

    except KSeFError as e:
        print(f"❌ Błąd KSeF: {e.msg}")
        if e.text: print(e.text)
    except Exception as e:
        print(f"❌ Błąd: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
