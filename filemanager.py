import os
from tkinter import filedialog
import cv2


# FileManager-Klasse zum Verwalten von Dateioperationen.
# Unterstützt die Auswahl von Bild- und XML-Dateien.
class FileManager:
    """
    Klasse zum Verwalten von Dateioperationen.
    Unterstützt die Auswahl von Bild- und XML-Dateien.
    """
    

    # Initialisiert die Dateitypen-Filter für Bilder und Klassifizierungsdateien.
    def __init__(self):
        """
        Initialisiert die Dateitypen-Filter für Bilder und Klassifizierungsdateien.
        """
        try:        
            self.filetypes_pictures = [("Bilder", "*.jpg *.png *.jpeg"), ("Alle Dateien", "*.*")]
            self.filetypes_classifier = [("XML-Dateien", "*.xml"), ("Alle Dateien", "*.*")]
        except Exception as e: # Fehlerbehandlung
            print("Fehler beim Initialisieren des Datei-Managers")


    # Öffnet ein Dialogfeld zur Auswahl einer Bilddatei.
    def open_file_picture(self, title="Bild auswählen"):
        """
        Öffnet ein Dialogfeld zur Auswahl einer Bilddatei.

        :param title: Titel des Dialogfelds (Standard: "Bild auswählen").
        :return: Pfad zur ausgewählten Datei oder None, falls abgebrochen.
        """

        return self._open_file(title, self.filetypes_pictures)

    
    

    # Öffnet ein Dialogfeld zur Auswahl einer Klassifizierungsdatei (XML).
    def open_file_classifier(self, title="Klassifizierungsdatei auswählen"):
        """
        Öffnet ein Dialogfeld zur Auswahl einer Klassifizierungsdatei (XML).

        :param title: Titel des Dialogfelds (Standard: "Klassifizierungsdatei auswählen").
        :return: Pfad zur ausgewählten Datei oder None, falls abgebrochen.
        """
        
        return self._open_file(title, self.filetypes_classifier)


    

    # Allgemeine Methode zum Öffnen eines Dialogfelds zur Dateiauswahl.
    def _open_file(self, title, filetypes):

        """
        Allgemeine Methode zum Öffnen eines Dialogfelds zur Dateiauswahl.

        :param title: Titel des Dialogfelds.
        :param filetypes: Dateitypenfilter für das Dialogfeld.
        :return: Pfad zur ausgewählten Datei oder None, falls abgebrochen.
        """
        try:
            file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
            if file_path:
                print(f"Datei ausgewählt: {file_path}")
                return file_path
            else:
                print("Keine Datei ausgewählt.")
                return None
        except Exception as e: # Fehlerbehandlung
            print("Fehler beim Öffnen der Datei")
            return None
            

    
    
    
    #　Lädt ein Bild von einem angegebenen Dateipfad.
    #　Das geladene Bild als NumPy-Array oder None, falls fehlgeschlagen.
    def load_image(self, file_path):
        """
        Lädt ein Bild von einem angegebenen Dateipfad.
        :param  file_path: Pfad zur Bilddatei.
        :return: Das geladene Bild als NumPy-Array oder None, falls fehlgeschlagen.
        """

        try:
            if not os.path.exists(file_path):
                print(f"Fehler: Datei {file_path} nicht gefunden.")
                return None

            image = cv2.imread(file_path)
            if image is None:
                print(f"Fehler: Datei {file_path} konnte nicht geladen werden.")
            else:
                print(f"Bild erfolgreich geladen: {file_path}")
            return image
        except Exception as e: # Fehlerbehandlung
            print("Fehler beim Laden des Bildes")
            return None
           
        
        
    # Speichert einen Screenshot des aktuellen Frames mit grünen Rechtecken.
    def save_screenshot(self, image):
        """
        Speichert einen Screenshot des aktuellen Frames mit grünen Rechtecken.
        :param image: NumPy-Array des Bildes.
        :return: True, wenn das Bild erfolgreich gespeichert wurde, sonst False.
        """

        try:            
            # Wähle den Dateipfad aus
            file_path = filedialog.asksaveasfilename(
                title="Speicherort für Screenshot auswählen",
                defaultextension=".png",
                filetypes=[("PNG Dateien", "*.png"), ("JPEG Dateien", "*.jpg *.jpeg"), ("Alle Dateien", "*.*")]
            )
            
            if not file_path:
                print("Speichern abgebrochen.")
                return False
            
            if cv2.imwrite(file_path, image):
                print(f"Bild erfolgreich gespeichert: {file_path}")
                return True
            else:
                print(f"Fehler: Bild konnte nicht gespeichert werden.")
                return False
        except Exception as e: # Fehlerbehandlung
            print("Fehler beim Speichern des Bildes")
            return False