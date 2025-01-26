import cv2
from filemanager import FileManager

# Klasse zum Verwalten von Klassifizierern und zum Erkennen von Objekten in einem Frame.
class ClassifierManager:
    """
    Klasse zum Verwalten von Klassifizierern und zum Erkennen von Objekten in einem Frame.
    """

    # Initialisiert den Klassifizierer-Manager.
    def __init__(self):
        """
        Initialisiert den Klassifizierer-Manager.
        """

        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml") # Standard-Gesichtsklassifizierer wird geladen
            self.file_manager = FileManager()
            self.current_classifier = "face"

            # Dictionary für native OpenCV-Klassifizierer
            self.classifiers = {
                "face": {
                "file": "haarcascade_frontalface_default.xml",
                "scaleFactor": 1.05,
                "minNeighbors": 3,
                "minSize": (30, 30)
                },
                "eye": {
                "file": "haarcascade_eye.xml",
                "scaleFactor": 1.1,
                "minNeighbors": 5,
                "minSize": (20, 20)
                },
                "smile": {
                "file": "haarcascade_smile.xml",
                "scaleFactor": 1.1,
                "minNeighbors": 15,
                "minSize": (25, 25)
                },
                "upperbody": {
                "file": "haarcascade_upperbody.xml",
                "scaleFactor": 1.05,
                "minNeighbors": 3,
                "minSize": (50, 50)
                },
                "fullbody": {
                "file": "haarcascade_fullbody.xml",
                "scaleFactor": 1.05,
                "minNeighbors": 3,
                "minSize": (50, 50)
                },
                "profileface": {
                "file": "haarcascade_profileface.xml",
                "scaleFactor": 1.1,
                "minNeighbors": 3,
                "minSize": (30, 30)
                },
                "custom": {
                "file": "",
                "scaleFactor": 1.05,
                "minNeighbors": 3,
                "minSize": (30, 30)
                }
            }

        except cv2.error as e:
            print(f"Fehler beim Initialisieren des Klassifizierer-Managers: {e}")

    # Aktualisiert die Parameter des benutzerdefinierten Klassifizierers.
    def update_scaleFactor(self, value):
        """
        Aktualisiert den scaleFactor des benutzerdefinierten Klassifizierers.
        :param value: Wert für scaleFactor (z. B. 1.05).
        :return: None
        """

        try:
            self.classifiers["custom"]["scaleFactor"] = value
        except Exception as e: # Fehlerbehandlung
            print("Fehler beim Aktualisieren des scaleFactor")
    
    # Aktualisiert die Parameter des benutzerdefinierten Klassifizierers.
    def update_minNeighbors(self, value):
        """
        Aktualisiert den minNeighbors des benutzerdefinierten Klassifizierers.
        :param value: Wert für minNeighbors (z. B. 3).
        :return: None
        """

        try:
            self.classifiers["custom"]["minNeighbors"] = value
        except Exception as e: # Fehlerbehandlung
            print("Fehler beim Aktualisieren des minNeighbors")
     
    # Aktualisiert die Parameter des benutzerdefinierten Klassifizierers.
    def update_minSize(self, value):
        """
        Aktualisiert den minSize des benutzerdefinierten Klassifizierers.
        :param value: Wert für minSize (z. B. 30).
        :return: None
        """

        try:
            self.classifiers["custom"]["minSize"] = (value, value)
        except Exception as e: # Fehlerbehandlung
            print("Fehler beim Aktualisieren des minSize")

    # Lädt eine Haar-Cascade XML-Datei zum Erkennen von Gesichtern.
    def load_custom_classifier(self):
        """
        Lädt eine Haar-Cascade XML-Datei zum Erkennen von Gesichtern.
        :return: Name des geladenen Klassifizierers oder eine Fehlermeldung.
        """
        
        try:
            file_path = self.file_manager.open_file_classifier()
            if file_path:
                self.face_cascade = cv2.CascadeClassifier(file_path)
                self.custom_classifier_name = file_path.split("/")[-1]
            else:
                if hasattr(self, 'custom_classifier_name'):
                    return self.custom_classifier_name
                else:
                    return "Datei auswählen..."

            return self.custom_classifier_name
        except Exception as e: # Fehlerbehandlung
            print("Fehler beim Laden des benutzerdefinierten Klassifizierers")
            return "Fehler beim Laden"
    

    # Lädt einen nativen OpenCV-Klassifizierer basierend auf einer angegebenen ID.
    def load_classifier(self, classifier_id):
        """
        Lädt einen nativen OpenCV-Klassifizierer basierend auf einer angegebenen ID.

        :param classifier_id: ID des gewünschten Klassifizierers (z. B. "face", "eye", "smile").
        :return: Name des geladenen Klassifizierers oder eine Fehlermeldung.
        """ 
        try:
            if classifier_id not in self.classifiers:
                print(f"Ungültige ID: '{classifier_id}'")
                return "Ungültige ID!"

            # Den Dateipfad für den gewünschten Klassifizierer erstellen
            classifier_info = self.classifiers[classifier_id]
            classifier_path = cv2.data.haarcascades + classifier_info["file"]
            print(f"Lade Klassifizierer '{classifier_info['file']}'...")

            # Versuchen, den Klassifizierer zu laden
        
            self.face_cascade = cv2.CascadeClassifier(classifier_path)
            self.current_classifier = classifier_id
    
        except cv2.error as e:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            self.current_classifier = "face"
            print(f"Laden des Klassifizierers '{classifier_info['file']}' fehlgeschlagen")
            return "Laden fehlgeschlagen! Standard wird zurückgesetzt"

        print(f"Klassifizierer '{classifier_info['file']}' erfolgreich geladen.")
        return classifier_info["file"]




    # Trainiert einen benutzerdefinierten Haar-Cascade Klassifizierer.
    def train_classifier(self):
        pass


    # Erkennt Objekte in einem gegebenen Frame.
    def detect_faces(self, frame, classifier_id = "face"):
        """
        Erkennt Objekte in einem gegebenen Frame.
        :param frame: Frame, in dem Objekte erkannt werden sollen.
        :param classifier_id: ID des Klassifizierers, der verwendet werden soll.
        :return: Liste der erkannten Objekte oder None, falls ein Fehler auftritt
        """

        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            classifier_info = self.classifiers[classifier_id]
            objects = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=classifier_info["scaleFactor"], 
                minNeighbors=classifier_info["minNeighbors"], 
                minSize=classifier_info["minSize"]
            )
            #print(f"{classifier_info['scaleFactor']}, {classifier_info['minNeighbors']}, {classifier_info['minSize']}")
            return objects
        
        except cv2.error as e:
            #print(f"Fehler beim Erkennen von Objekten: {e}")
            return None
        
        