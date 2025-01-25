# Version 1 als Inspiration
# !!! Nicht ausführbar !!!
# !!! Nur als Beispiel für die Implementierung !!!

# app.py

import cv2
from tkinter import Label, Canvas, Button, filedialog, StringVar, ttk
from PIL import Image, ImageTk
from cameramanager import CameraManager
from classifiermanager import ClassifierManager
from filemanager import FileManager

class App:
    def __init__(self, root):
        # Initialisiert die App und GUI-Komponenten.
        self.root = root
        self.root.title("Gesichtserkennung")

        # Manager-Instanzen
        self.camera_manager = CameraManager()
        self.classifier_manager = ClassifierManager()
        self.file_manager = FileManager()

        # GUI-Komponenten
        self.canvas = Canvas(root, width=640, height=480)
        self.canvas.pack()

        # Info-Label
        self.info_label = Label(root, text="Gesichtserkennung: Live oder Bild auswählen")
        self.info_label.pack()

        # Kamera-Auswahlmenü
        self.camera_var = StringVar(value="Keine Kamera erkannt")
        self.camera_selector = ttk.Combobox(root, textvariable=self.camera_var, state="readonly")
        self.camera_selector.pack(pady=5)

        self.btn_refresh_cameras = Button(root, text="Kameras Aktualisieren", command=self.refresh_camera_list)
        self.btn_refresh_cameras.pack(pady=5)

        # Modus-Auswahl
        self.mode_var = StringVar(value="live")
        self.mode_selector = ttk.Combobox(root, textvariable=self.mode_var, state="readonly")
        self.mode_selector

        self.mode_selector["values"] = ["live", "file"]
        self.mode_selector.pack(pady=5)

        # Buttons
        self.btn_load_image = Button(root, text="Bild Laden", command=self.load_image_from_file)
        self.btn_load_image.pack(pady=5)

        self.btn_start_camera = Button(root, text="Live-Bild Starten", command=self.start_camera)
        self.btn_start_camera.pack(pady=5)

        self.btn_stop_camera = Button(root, text="Kamera Stoppen", command=self.stop_camera)
        self.btn_stop_camera.pack(pady=5)

        self.btn_train_classifier = Button(root, text="Klassifizierer Trainieren", 
                                           command=self.classifier_manager.train_classifier)
        self.btn_train_classifier.pack(pady=5)

        self.face_count_label = Label(root, text="Erkannte Gesichter: 0")
        self.face_count_label.pack(pady=10)

        # Variablen
        self.current_frame = None
        self.static_image = None
        self.refresh_camera_list()  # Beim Start Kameras aktualisieren

    def refresh_camera_list(self):
        # Aktualisiert die Kameraliste und zeigt verfügbare Kameras an.
        available_cameras = self.camera_manager.detect_cameras()
        if available_cameras:
            camera_names = [f"Kamera {index}" for index in available_cameras]
            self.camera_selector["values"] = camera_names
            self.camera_selector.current(0)
            print(f"Kameras gefunden: {camera_names}")
        else:
            self.camera_selector["values"] = ["Keine Kamera erkannt"]
            self.camera_selector.current(0)
            print("Keine Kameras gefunden.")
            
    def start_camera(self):
        # Startet die Kamera und den Live-Modus.
        print("Versuche, die Kamera zu starten...")
        camera_index = 0  # Default-Kamera
        try:
            self.camera_manager.start_camera(camera_index)
            print(f"Kamera {camera_index} erfolgreich gestartet.")
            self.update_frame() # Startet die Frame-Aktualisierung
        except Exception as e:
            self.info_label.config(text=f"Kamera konnte nicht gestartet werden: {str(e)}")
            print(f"Kamera-Fehler: {str(e)}")

    def stop_camera(self):
        # Stoppt die Kamera.
        print("Kamera wird gestoppt...")
        self.camera_manager.stop_camera()
        self.static_image = None  # Falls ein Bild angezeigt wurde, wird es zurückgesetzt.
        print("Kamera gestoppt.")

    def load_image_from_file(self):
        # Lädt ein Bild von der Festplatte und zeigt es an.
        print("Lade Bild von Datei...")

        file_path = self.file_manager.open_file_dialog(title="Bild auswählen")
        
        if file_path:
            image = cv2.imread(file_path)
            if image is not None:
                self.static_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                print(f"Bild {file_path} erfolgreich geladen.")
                self.update_frame()  # Bild anzeigen
            else:
                print(f"Fehler: Bild {file_path} konnte nicht gelesen werden.")
        else:
            print("Kein Bild ausgewählt.")

    def update_frame(self):
        # Holt ein Frame von der Kamera und zeigt es in der GUI an.
        if self.mode_var.get() == "live":
            ret, frame = self.camera_manager.get_frame()
            if ret:
                frame_height, frame_width = frame.shape[:2]
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()

                # Gesichtserkennung
                faces = self.classifier_manager.detect_faces(frame)
                num_faces = len(faces)

                # Zeichne grüne Rechtecke um erkannte Gesichter
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Berechnung der Skalierung unter Beibehaltung des Seitenverhältnisses
                scale = min(canvas_width / frame_width, canvas_height / frame_height)
                new_width = int(frame_width * scale)
                new_height = int(frame_height * scale)

                # Frame skalieren und konvertieren
                frame_resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)

                # Canvas zurücksetzen und Bild anzeigen
                self.canvas.delete("all")
                self.canvas.create_image(
                    canvas_width // 2, canvas_height // 2, anchor="center", image=imgtk
                )
                self.canvas.image = imgtk  # Referenz behalten

                # Gesichtszahl aktualisieren, falls sie sich ändert
                if not hasattr(self, "last_face_count") or self.last_face_count != num_faces:
                    self.face_count_label.config(text=f"Erkannte Gesichter: {num_faces}")
                    self.last_face_count = num_faces
            elif ret is False:
                self.canvas.delete("all")

        elif self.mode_var.get() == "file" and self.static_image is not None:
            # Bild vom Dateipfad anzeigen
            img = Image.fromarray(self.static_image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.canvas.delete("all")
            self.canvas.create_image(
                self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, 
                anchor="center", image=imgtk
            )
            self.canvas.image = imgtk  # Referenz behalten

        # Nächsten Frame planen
        self.root.after(10, self.update_frame)  # Alle 10 ms ein neuer Frame




# cameramanager.py

import cv2

class CameraManager:
    def __init__(self):
        # Initialisiert den Kamera-Manager.
        self.cap = None
        self.running = False

    def detect_cameras(self):
    # Erkennt verfügbare Kameras und gibt eine Liste der Indizes zurück.
        available_cameras = []
        for i in range(3):  # Teste nur die ersten 3 Kameras
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        return available_cameras

    def start_camera(self, camera_index=0):
        # Startet die Kamera mit dem angegebenen Index.
        self.cap = cv2.VideoCapture(camera_index)
        self.running = self.cap.isOpened()
        if not self.running:
            raise Exception(f"Kamera {camera_index} konnte nicht gestartet werden.")


    def stop_camera(self):
        # Stoppt die Kamera und gibt Ressourcen frei.
        if self.cap:
            self.cap.release()
        self.cap = None
        self.running = False

    def get_frame(self):
        # Liefert einen Frame von der Kamera.
        if self.cap is None or not self.cap.isOpened():
            return False, None
        ret, frame = self.cap.read()
        if ret:
            return ret, frame
        else:
            return False, None





# classifiermanager.py

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




# filemanager.py

from tkinter import filedialog

class FileManager:
    @staticmethod
    def open_file_dialog(title="Datei auswählen", filetypes=(("Bilder", "*.jpg;*.png;*.jpeg"), ("Alle Dateien", "*.*"))):
        file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
        return file_path





# main.py

from tkinter import Tk
from app import App

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()