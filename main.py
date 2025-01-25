from PySide6.QtWidgets import QApplication 
from app import App

# Hauptprogramm
if __name__ == "__main__":
        
    app = QApplication([]) # PySide6-Anwendung erstellen
    window = App() # App-Objekt erstellen
    window.show() # Fenster (GUI) anzeigen 
    app.exec()  # Hauptschleife starten