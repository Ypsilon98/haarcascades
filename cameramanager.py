import cv2

# Kamera-Manager-Klasse zum Verwalten von Kameraoperationen.
class CameraManager:

    # Initialisiert den Kamera-Manager.
    def __init__(self):
        """
        Initialisiert den Kamera-Manager.
        """        
        try:
            self.cap = None # Kamera-Objekt
        except Exception as e: # Fehlerbehandlung
            print("Fehler beim Initialalisiern des Kamera-Managers")
    
    
    # Erkennt verfügbare Kameras und gibt eine Liste der Indizes zurück.
    # Testet nur die ersten drei Kameras
    def detect_cameras(self):
        """
        Erkennt verfügbare Kameras und gibt eine Liste der Indizes zurück.
        """
        try:
            available_cameras = []
            for camera_id in range (3): # Testet nur die ersten drei Kameras
                self.cap = cv2.VideoCapture(camera_id)  # Kamera mit Index camera_id öffnen
                if self.cap.isOpened(): # Testen, ob Kamera geöffnet wurde
                    available_cameras.append(camera_id) # Kamera ist verfügbar und wird zur Liste hinzugefügt
                    self.cap.release()
            return available_cameras
        
        except Exception as e: # Fehlerbehandlung
            print("Fehler beim Erkennen der Kameras")
            return None

    # Startet die Kamera mit dem angegebenen Index.
    def start_camera(self, camera_id =0):
        """
        Startet die Kamera mit dem angegebenen Index.
        """
        try:
            self.cap = cv2.VideoCapture(camera_id)  # Kamera mit Index camera_id öffnen

            # Testen, ob Kamera geöffnet wurde.
            if self.cap.isOpened():
                print (f"Kamera mit ID {camera_id} wurde erfolgreich geöffnet")
                return self.cap
            else:
                print (f"Fehler: Kamera mit ID {camera_id} konnte nicht geöffnet werden")
                return None
            
        except Exception as e: # Fehlerbehandlung
            print("Fehler beim Öffnen der Kamera")
            return None
        

    # Stoppt die Kamera und gibt Ressourcen frei.
    def stop_camera(self):
        """
        Stoppt die Kamera und gibt Ressourcen frei.
        """
        try:

            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
                print("Kamera erfolgreich geschlossen")

        except Exception as e: # Fehlerbehandlung
            print("Fehler beim Schließen der Kamera")


    # Liefert einen Frame von der Kamera.
    def get_frame(self):
        """
        Liefert einen Frame von der Kamera.
        """
        try:
            if self.cap is not None and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    return frame, True
                else:
                    return None, False
        except Exception as e: # Fehlerbehandlung
            print("Fehler beim Abrufen des Frames")
            return None, False
    