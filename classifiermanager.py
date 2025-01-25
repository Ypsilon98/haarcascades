import cv2
from tkinter import filedialog

class ClassifierManager:
    def __init__(self):
        # Initialisiert den Klassifizierer-Manager.
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def load_classifier(self):
        # Lädt eine Haar-Cascade XML-Datei zum Erkennen von Gesichtern.
        file_path = filedialog.askopenfilename(title="Wähle Haar-Cascade XML-Datei",
                                               filetypes=(("XML-Dateien", "*.xml"), ("Alle Dateien", "*.*")))
        if file_path:
            self.face_cascade = cv2.CascadeClassifier(file_path)


    def train_classifier(self):
        # Trainiert einen benutzerdefinierten Haar-Cascade Klassifizierer.
        # Beispiel-Logik für das Training eines Klassifizierers:
        # Du kannst hier den Prozess implementieren, um z. B. Positiv- und Negativbilder zu verarbeiten.
        file_path = filedialog.askdirectory(title="Wähle Trainingsdatensatz-Ordner")
        if file_path:
            # Füge hier Code für das Training mit OpenCV hinzu (z. B. mit cv2.trainCascadeClassifier).
            print(f"Klassifizierer mit Daten aus {file_path} trainieren...")
        else:
            print("Kein Ordner ausgewählt!")

    def detect_faces(self, frame):
        # Erkennt Gesichter in einem gegebenen Frame.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(30, 30))
        return faces
