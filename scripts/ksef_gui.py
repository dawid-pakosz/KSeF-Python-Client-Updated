import sys
import os

# Dodaj src do path, aby można było importować ksef_client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    from ksef_client.ui.controller import KSeFController
except ImportError as e:
    print(f"Błąd importu: {e}")
    print("Upewnij się, że zainstalowałeś wymagane biblioteki: pip install customtkinter Pillow")
    sys.exit(1)

def main():
    # Uruchom aplikację MVC
    app = KSeFController()
    app.run()

if __name__ == "__main__":
    main()
