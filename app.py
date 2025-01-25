import cv2
import numpy as np
# Importe aus den PySide6-Bibliotheken (für Layout, GUI-Elemente, etc.)
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QLabel, QComboBox, QStatusBar, QMessageBox, QSlider
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QSizePolicy 
from PySide6.QtGui import QPixmap, QImage , QPainter, QColor, QAction
from PySide6.QtCore import QTimer, Qt, QRect
# Importe der Manager-Klassen
from cameramanager import CameraManager
from classifiermanager import ClassifierManager
from filemanager import FileManager

# Hauptklasse App für GUI
class App(QMainWindow):
    """
    Hauptklasse für die GUI-Anwendung. 

    Attribute: camera_manager (CameraManager): Instanz des CameraManagers.
               classifier_manager (ClassifierManager): Instanz des ClassifierManagers.
               file_manager (FileManager): Instanz des FileManager.
               central_widget (QWidget): Zentrales Widget der Anwendung.
               status (QStatusBar): Statusleiste der Anwendung.
               
               image_display (QLabel): Anzeigebereich für Bilder/Kamera.
               animation_label (QLabel): Anzeigebereich für die Beispielanimation.
               camera_selector (QComboBox): Dropdown-Menü für die Auswahl der Kamera.
               mode_selector (QComboBox): Dropdown-Menü für die Auswahl des Modus.
               classifier_selector (QComboBox): Dropdown-Menü für die Auswahl des Klassifizierers.
               slider_custom_scaleFactor (QSlider): Slider für den scaleFactor des Klassifizierers.
               slider_custom_minNeighbors (QSlider): Slider für den minNeighbors des Klassifizierers.
               slider_custom_minSize (QSlider): Slider für den minSize des Klassifizierers.
               custom_classifier_label (QLabel): Label für die Anzeige des benutzerdefinierten Klassifizierers.
               
               btn_refresh_cameras (QPushButton): Button zum Aktualisieren der Kamera-Liste.
               btn_load_image (QPushButton): Button zum Laden eines Bildes.
               btn_start_camera (QPushButton): Button zum Starten/Stoppen der Kamera.
               btn_choose_classifier (QPushButton): Button zum Laden eines benutzerdefinierten Klassifizierers.
               btn_train_classifier (QPushButton): Button zum Trainieren des Klassifizierers.
               btn_screenshot (QPushButton): Button zum Erstellen eines Screenshots.
               
               num_objects (int): Anzahl der erkannten Objekte.
               object_count_label (QLabel): Label zur Anzeige der Anzahl der erkannten Objekte.
               
               timer (QTimer): Timer für die Aktualisierung der Frames.
               animation_timer (QTimer): Timer für die Beispielanimation.
               
               current_frame (np.ndarray): Aktueller Frame.
               static_image (np.ndarray): Statisches Bild.
               is_nightmode (bool): Nachtmodus-Status.
    
    Methoden:   __init__()
                toggle_fullscreen(), toggle_nightmode() 
                show_help(), show_about(), 
                load_stylesheet(filename),
                change_mode(text), change_classifier(text), load_predefined_classifier(classifier_id), load_custom_classifier(),
                refresh_camera_list(), start_camera(), stop_camera(), start_stop_camera(checked), 
                load_image_from_file(), reset_image(), load_reset_file(checked), 
                animation(), draw_haar_filter(), 
                update_frame().
    """
    # Initialisiert die GUI und die Manager-Instanzen.
    def __init__(self):
        """
        Initialisiert die GUI Elemente und Manager Instanzen.
        """
        super().__init__()
        
        # Manager Instanzen
        self.camera_manager = CameraManager()
        self.classifier_manager = ClassifierManager()
        self.file_manager = FileManager()

        self.setWindowTitle("Objekterkennung mit Haarcascades")   # Fenstertitel
        self.setGeometry(100, 100, 1000, 700)  # Start-Fenstergröße festlegen

        # Versuche Stylesheet zu laden (Sicherstellen das Programm im richtigen Verzeichnis gestartet wird)
        try:    
            try:
                self.load_stylesheet("style_sheet.css") # Um Fehlermeldung zu vermeiden
                self.load_stylesheet("b2-1_haarcascades/style_sheet.css") 
            except:
                pass
            self.i2 = cv2.imread("face_animation.jpg")
            self.i1 = cv2.imread("b2-1_haarcascades/face_animation.jpg")

        # Fehlerbehandlung beim Laden des Stylesheets
        except Exception as e: # Fehlerbehandlung 
            print("Fehler beim Laden des Stylesheets, stelle sicher das du im richtigen Verzeichnis ../b2-1_haarcascades/main.py startest")
        
        # Sicherstellen, dass App nicht abstürzt, wenn Bild nicht geladen werden kann
        if type(self.i1) != type(None):     
            self.image = QImage(self.i1.data, self.i1.shape[1], self.i1.shape[0], QImage.Format.Format_RGB888)
        elif type(self.i2) != type(None):    
            self.image = QImage(self.i2.data, self.i2.shape[1], self.i2.shape[0], QImage.Format.Format_RGB888)
        else: 
            self.image = QImage(250,250) # leeres Bild
        
        # Central Widget (Hauptbereich)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Menüleiste (Menüs und Aktionen)
        menu_bar = self.menuBar()
        view_menu = menu_bar.addMenu("Ansicht")
        self.fullscreen_action = QAction("Vollbild",self)
        self.fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(self.fullscreen_action)

        self.is_nightmode = False # Nachtmodus (deaktiviert)
        self.nightmode_action = QAction("Nachtmodus",self)
        self.nightmode_action.triggered.connect(self.toggle_nightmode)
        view_menu.addAction(self.nightmode_action)

        help_menu = menu_bar.addMenu("Info")
        help_action = QAction("Kurzanleitung",self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        about_action = QAction("Über", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        end_action = QAction("Beenden", self)
        end_action.triggered.connect(self.close)
        help_menu.addAction(end_action)

        # Main Layout im Central Widget
        debug_layout = QVBoxLayout(self.central_widget)
        main_layout = QHBoxLayout()
        # Status Anzeigeleiste (unterhalb des Hauptbreichs)
        debug_layout.addLayout(main_layout) 
        self.status = QStatusBar() 
        debug_layout.addWidget(self.status)
        
        # Kamera- und Bildanzeigebereich
        self.image_display = QLabel("Anzeigebereich für Bilder/Kamera")
        self.image_display.setProperty("status", "display") # Property für Style aus Stylesheet
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter) # Zentrierte Ausrichtung
        self.image_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # Größe passt sich an Fenstergröße an
        self.image_display.setMinimumSize(300,300)
        main_layout.addWidget(self.image_display)

        # Kontrollbereich Layout (rechts vom Bildanzeigebereich)
        control_panel = QVBoxLayout()

        # Beispielanimation Haar Cascades
        self.animation_label = QLabel()
        self.pixmap = QPixmap(self.image)
        self.pixmap = self.pixmap.scaled(250, 250)
        self.x = 0
        self.y = 0
        self.random_int = np.random.randint(0, 5)
        self.animation_label.setPixmap(self.pixmap)
        self.animation_label.setMinimumWidth(250)
        self.animation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_panel.addWidget(self.animation_label) # Animation zu Kontrollbereich hinzufügen

        # Kamera Dropdown Layout
        camera_layout = QHBoxLayout()
        self.camera_selector = QComboBox()
        self.camera_selector.addItem("Keine Kamera erkannt")
        camera_layout.addWidget(QLabel("Kamera:"))
        camera_layout.addWidget(self.camera_selector)

        self.btn_refresh_cameras = QPushButton("Kameras Aktualisieren")
        self.btn_refresh_cameras.clicked.connect(self.refresh_camera_list) # Klick-Event für Button
        control_panel.addWidget(self.btn_refresh_cameras)
        control_panel.addLayout(camera_layout) # Kamera Dropdown zu Kontrollbereich hinzufügen

        # Modus Auswahl Layout
        mode_layout = QHBoxLayout()
        self.mode_selector = QComboBox()
        self.mode_selector.setEnabled(True)
        self.mode_selector.addItems(["live", "file"])
        self.mode_selector.currentTextChanged.connect(self.change_mode) # Event für Auswahländerung
        mode_layout.addWidget(QLabel("Modus:"))
        mode_layout.addWidget(self.mode_selector)
        #mode_layout.addWidget(QLabel(""))
        control_panel.addLayout(mode_layout) # Modus Auswahl Dropdown zu Kontrollbereich hinzufügen

        # Buttons Layout
        buttons_layout = QVBoxLayout() # Vertikales Layout für Buttons

        # Bild laden
        self.btn_load_image = QPushButton("Bild Laden")
        self.btn_load_image.setCheckable(True)
        self.btn_load_image.setEnabled(False)
        self.btn_load_image.clicked.connect(self.load_reset_file)
        buttons_layout.addWidget(self.btn_load_image) # "Bild Laden" Button zu Kontrollbereich hinzufügen

        self.btn_start_camera = QPushButton("Live-Kamera Starten")
        self.btn_start_camera.setCheckable(True)
        self.btn_start_camera.setEnabled(False)
        self.btn_start_camera.clicked.connect(self.start_stop_camera)
        buttons_layout.addWidget(self.btn_start_camera) # "Live-Kamera Starten" Button zu Kontrollbereich hinzufügen
        
    
        classifier_layout = QHBoxLayout()
        self.classifier_selector = QComboBox()
        self.classifier_selector.setEnabled(True)
        self.classifier_selector.addItems(["face", "eye", "smile", "upperbody", "fullbody", "profileface", "Eigener Klassifizierer"])
        self.classifier_selector.setCurrentText("face")
        self.classifier_selector.currentTextChanged.connect(self.change_classifier)
        classifier_layout.addWidget(QLabel("Klassifizierer:"))
        classifier_layout.addWidget(self.classifier_selector)
        buttons_layout.addLayout(classifier_layout) # Klassifizierer Dropdown zu Kontrollbereich hinzufügen

        slider_layout = QVBoxLayout() # Vertikales Layout für Slider

        # scaleFactor Slider
        scaleFactor_layout = QHBoxLayout() # Horizontales Layout für Label und Slider
        self.label_custom_scaleFactor = QLabel("scaleFactor:")
        self.slider_custom_scaleFactor = QSlider(Qt.Orientation.Horizontal)
        self.slider_custom_scaleFactor.setMinimumWidth(150)
        self.slider_custom_scaleFactor.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.slider_custom_scaleFactor.setRange(10, 30)  # 1.0 bis 3.0 (multipliziert mal 10)
        self.slider_custom_scaleFactor.setValue(1.05)  # Default 1.2
        self.label_custom_scaleFactor.setText(f"scaleFactor: {self.slider_custom_scaleFactor.value()/10}")
        self.slider_custom_scaleFactor.valueChanged.connect(self.update_scaleFactor)
        self.slider_custom_scaleFactor.setSingleStep(1) # Schrittweite 0.1
        self.slider_custom_scaleFactor.setEnabled(False)
        
        scaleFactor_layout.addWidget(self.label_custom_scaleFactor) 
        scaleFactor_layout.addWidget(self.slider_custom_scaleFactor)
        slider_layout.addLayout(scaleFactor_layout) 

        # minNeighbors Slider
        minNeighbors_layout = QHBoxLayout() # Horizontales Layout für Label und Slider
        self.label_custom_minNeighbors = QLabel("minNeighbors:")
        self.slider_custom_minNeighbors = QSlider(Qt.Orientation.Horizontal)
        self.slider_custom_minNeighbors.setMinimumWidth(150)
        self.slider_custom_minNeighbors.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.slider_custom_minNeighbors.setRange(1, 20)  # von 1 bis 10
        self.slider_custom_minNeighbors.setValue(3)  # Default 3
        self.label_custom_minNeighbors.setText(f"minNeighbors: {self.slider_custom_minNeighbors.value()}")
        self.slider_custom_minNeighbors.valueChanged.connect(self.update_minNeighbors)
        self.slider_custom_minNeighbors.setSingleStep(1)
        self.slider_custom_minNeighbors.setEnabled(False)
        minNeighbors_layout.addWidget(self.label_custom_minNeighbors)
        minNeighbors_layout.addWidget(self.slider_custom_minNeighbors)
        slider_layout.addLayout(minNeighbors_layout)

        # minSize Slider
        minSize_layout = QHBoxLayout() # Horizontales Layout für Label und Slider
        self.label_custom_minSize = QLabel("minSize:")
        self.slider_custom_minSize = QSlider(Qt.Orientation.Horizontal)
        self.slider_custom_minSize.setMinimumWidth(150)
        self.slider_custom_minSize.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) 
        self.slider_custom_minSize.setRange(20, 200)  # von 20 bis 200
        self.slider_custom_minSize.setValue(30)  # Default 30
        self.label_custom_minSize.setText(f"minSize: {self.slider_custom_minSize.value()}")
        self.slider_custom_minSize.valueChanged.connect(self.update_minSize)
        self.slider_custom_minSize.setSingleStep(5)
        self.slider_custom_minSize.setEnabled(False)
        minSize_layout.addWidget(self.label_custom_minSize)
        minSize_layout.addWidget(self.slider_custom_minSize)
        slider_layout.addLayout(minSize_layout)

        buttons_layout.addLayout(slider_layout) # Slider Layout zu Kontrollbereich hinzufügen

        # Label zur Anzeige des Namens der benutzerdefinierten Klassifizierer-XML-Datei
        self.custom_classifier_label = QLabel("")
        buttons_layout.addWidget(self.custom_classifier_label)

        # Buttons für Klassifizierer
        self.btn_choose_classifier = QPushButton("Eigener Klassifizierer Laden")
        self.btn_choose_classifier.setEnabled(False)
        self.btn_choose_classifier.clicked.connect(self.load_custom_classifier)
        buttons_layout.addWidget(self.btn_choose_classifier)

        self.btn_train_classifier = QPushButton("Klassifizierer Trainieren")
        self.btn_train_classifier.setEnabled(False)
        #self.btn_train_classifier.clicked.connect(self.classifier_manager.train_classifier)
        buttons_layout.addWidget(self.btn_train_classifier)

        self.btn_screenshot = QPushButton("Screenshot")
        self.btn_screenshot.setEnabled(False)
        self.btn_screenshot.clicked.connect(self.save_screenshot)
        buttons_layout.addWidget(self.btn_screenshot)
        control_panel.addLayout(buttons_layout) # Button Layout zu Kontrollbereich hinzufügen

        # Erkannte Objekte Label (Anzeige der Anzahl der erkannten Objekte)
        objects_layout = QHBoxLayout()
        self.num_objects = 0 # Anzahl der erkannten Objekte
        self.object_count_label = QLabel("")
        self.object_count_label.setText(f"<a style=\"text-decoration:none;\" href=\"http://www.easteregg.com\"> {self.num_objects} </a>") 
        self.object_count_label.setOpenExternalLinks(True)
        self.object_count_label.setAlignment(Qt.AlignmentFlag.AlignLeft) # Ausrichtung links
        self.object_count_label.setAlignment(Qt.AlignmentFlag.AlignVCenter) # Vertikale Zentrierung
        self.object_count_label.setStyleSheet("font-weight: bold;") 
        objects_layout.addWidget(QLabel("Erkannte Objekte: "))
        objects_layout.addWidget(self.object_count_label)
        control_panel.addLayout(objects_layout)

        main_layout.addLayout(control_panel) # Kontrollbereich zu Hauptlayout hinzufügen

        # Timer für die Aktualisierung der Frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame) 

        # Timer für Beispielanimation
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animation)
        self.animation_timer.start(50)  # Animationsgeschwindigkeit in ms

        # Variablen
        self.current_frame = None # Aktueller Frame
        self.static_image = None # Statisches Bild

        # Kameraliste bei Programmstart aktualisieren
        self.btn_refresh_cameras.click() # Simuliert Klick des Kameras aktualisieren Buttons
        #self.change_mode(self.mode_selector.currentText()) # Modus basierend auf Auswahl initialisieren

    # Animiert die Haar Cascade Features
    def animation(self):
        """
        Beispielanimation von Haar Cascade Features.
        Sinnvoll um Response des GUI zu testen und durch Programmcode verursachten lag zu erkennen
        """
        try:
            if self.x + 60 >= 250:
                self.x = 0
                self.y += 60
                self.random_int = np.random.randint(0, 5)

            if self.y + 60 >= 250:
                self.x = 0
                self.y = 0
                
            self.x += 10
            self.draw_haar_filter()
        except Exception as e:
            print(f"Fehler beim Erstellen der Animation: {str(e)}") # Debug-Ausgabe in Konsole    
            

    # Zeichnet Haar Cascade Features als Overlay auf das Bild.
    def draw_haar_filter(self):
        try:
            overlay_pixmap = self.pixmap.copy() # Kopie des Originalbildes
            painter = QPainter(overlay_pixmap) # Painter-Objekt für Overlay
            x, y = self.x, self.y # Position des Haar Cascade Features

            # Zufällige Auswahl eines Haar Cascade Features
            if self.random_int == 0:
                painter.fillRect(QRect(x,      y, 20, 60), QColor("white"))
                painter.fillRect(QRect(x + 20, y, 20, 60), QColor("black"))
                painter.fillRect(QRect(x + 40, y, 20, 60), QColor("white"))
            elif self.random_int == 1:
                painter.fillRect(QRect(x, y,      60, 20), QColor("white"))
                painter.fillRect(QRect(x, y + 20, 60, 20), QColor("black"))
                painter.fillRect(QRect(x, y + 40, 60, 20), QColor("white"))
            elif self.random_int == 2:
                painter.fillRect(QRect(x     , y     , 30, 30), QColor("white"))
                painter.fillRect(QRect(x + 30, y     , 30, 30), QColor("black"))
                painter.fillRect(QRect(x     , y + 30, 30, 30), QColor("white"))
                painter.fillRect(QRect(x + 30, y + 30, 30, 30), QColor("black"))
            elif self.random_int == 3:
                painter.fillRect(QRect(x     , y     , 30, 30), QColor("white"))
                painter.fillRect(QRect(x + 30, y     , 30, 30), QColor("white"))
                painter.fillRect(QRect(x     , y + 30, 30, 30), QColor("black"))
                painter.fillRect(QRect(x + 30, y + 30, 30, 30), QColor("black"))
            elif self.random_int == 4:
                painter.fillRect(QRect(x     , y     , 30, 30), QColor("white"))
                painter.fillRect(QRect(x + 30, y     , 30, 30), QColor("black"))
                painter.fillRect(QRect(x     , y + 30, 30, 30), QColor("black"))
                painter.fillRect(QRect(x + 30, y + 30, 30, 30), QColor("white"))
            else:
                painter.fillRect(QRect(x     , y     , 30, 30), QColor("black"))
                painter.fillRect(QRect(x + 30, y     , 30, 30), QColor("white"))
                painter.fillRect(QRect(x     , y + 30, 30, 30), QColor("white"))
                painter.fillRect(QRect(x + 30, y + 30, 30, 30), QColor("black"))

            painter.end() 
            self.animation_label.setPixmap(overlay_pixmap) # Overlay-Bild setzen
        except Exception as e:
            print(f"Fehler beim Anzeigen der Haar-Features: {str(e)}") # Debug-Ausgabe in Konsole
            

    # Schaltet zwischen Vollbildmodus und Fenstermodus um.
    def toggle_fullscreen(self):
        try:
            if self.isFullScreen():
                self.showNormal()
                self.fullscreen_action.setText("Vollbild")
            else:
                self.showFullScreen()
                self.fullscreen_action.setText("Fenstermodus")
        except Exception as e:
            print(f"Fehler beim Umschalten des Vollbildmodus: {str(e)}") # Debug-Ausgabe in Konsole
            
    
    # Schaltet zwischen Nachtmodus und Tagmodus (stylesheets) um.
    def toggle_nightmode(self):
        # Versuche Stylesheet zu laden
        if self.is_nightmode:
            try:
                    self.load_stylesheet("style_sheet.css") # Um Fehlermeldung zu vermeiden
                    self.load_stylesheet("b2-1_haarcascades/style_sheet.css")
                    self.status.showMessage("Nachtmodus deaktiviert.")
            # Fehlerbehandlung beim Laden des Stylesheets
            except Exception as e: # Fehlerbehandlung 
                print("Fehler beim Laden des Stylesheets, stelle sicher das du im richtigen Verzeichnis ../b2-1_haarcascades/main.py startest")
            self.nightmode_action.setText("Nachtmodus")
        else:
            try:  
                    self.load_stylesheet("night_mode.css") # Um Fehlermeldung zu vermeiden
                    self.load_stylesheet("b2-1_haarcascades/night_mode.css")
                    self.status.showMessage("Nachtmodus aktiviert.")               
            # Fehlerbehandlung beim Laden des Stylesheets
            except Exception as e: # Fehlerbehandlung 
                print("Fehler beim Laden des Stylesheets, stelle sicher das du im richtigen Verzeichnis ../b2-1_haarcascades/main.py startest")
            self.nightmode_action.setText("Tagmodus")
        
        self.is_nightmode = not self.is_nightmode  # Nachtmodus-Status umschalten 
        
    
    # Zeigt ein Dialogfeld mit einer Kurzanleitung an (erreichbar über Menü->Info->Kurzanleitung)
    def show_help(self):
        QMessageBox.about(self, "Kurzanleitung",  "Kamera und Modus auswählen und auf Live-Kamera Starten klicken.\n\nAlternativ Modus auf 'file' setzen und Bild Laden.\n\nObjekte werden automatisch erkannt, markiert und gezählt.\n\nVortrainierte als auch eigene Klassifizierer können geladen werden.\n\nDazu einfach den entsprechenden Button klicken und die XML-Datei auswählen.\n\nViel Spaß!")
    
    # Zeigt ein Dialogfeld mit Informationen über die Anwendung an (erreichbar über Menü->Info->Über)
    def show_about(self):
        QMessageBox.about(self, "Über", "Anwendung zur Objekterkennung mit Haarcascades\n\nProgrammiert von der Projektgruppe B2-1 im Master AKI an der FH SWF Iserlohn\n\nYannic\nEmelie\nLeon\nPhilipp\n\nJanuar 2025")

    # Lädt ein Stylesheet aus einer Datei.
    def load_stylesheet(self, filename):
        """
        Lädt ein Stylesheet aus einer Datei und wendet es auf die Anwendung an.

        Parameter: filename (str): Dateiname des Stylesheets.
        """
        try:
            with open(filename, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"Error: Stylesheet file '{filename}' not found.")

    # Ändert den Modus basierend auf der Auswahl im Dropdown-Menü.
    def change_mode(self, text):
        """
        Ändert den Anzeige-Modus basierend auf der Auswahl im Dropdown-Menü.

        Parameter: text (str): Text des ausgewählten Modus.
        """
        try:
            if text == "live":
                available_cameras = self.camera_manager.detect_cameras()
                if available_cameras:
                    self.btn_start_camera.setEnabled(True)
                    self.btn_start_camera.setProperty("status","start")
                    self.btn_start_camera.style().unpolish(self.btn_start_camera) 
                    self.btn_start_camera.style().polish(self.btn_start_camera)    
                    self.btn_load_image.setEnabled(False)
                    self.btn_load_image.setProperty("status","unavailable")
                    self.btn_load_image.style().unpolish(self.btn_load_image)
                    self.btn_load_image.style().polish(self.btn_load_image)
                    self.status.showMessage("Modus auf Live-Kamera geändert.")
                else:
                    self.status.showMessage("Keine Kamera erkannt.")
                    print("Keine Kamera erkannt.")

            elif text == "file":
                self.btn_start_camera.setEnabled(False)
                self.btn_start_camera.setProperty("status", "unavailable")
                self.btn_start_camera.style().unpolish(self.btn_start_camera)
                self.btn_start_camera.style().polish(self.btn_start_camera)
                self.btn_load_image.setEnabled(True)
                self.btn_load_image.setProperty("status","start")
                self.btn_load_image.style().unpolish(self.btn_load_image)
                self.btn_load_image.style().polish(self.btn_load_image)
                self.status.showMessage("Modus auf Bild laden geändert.")
            else:
                self.btn_start_camera.setEnabled(False)
                self.btn_load_image.setEnabled(False)
        except Exception as e:
            print(f"Fehler beim Ändern des Modus: {str(e)}") # Debug-Ausgabe in Konsole
            self.status.showMessage(f"Fehler beim Ändern des Modus: {str(e)}") # Statusnachricht in Statusleiste
        
    
    # Ändert den Klassifizierer basierend auf der Auswahl im Dropdown-Menü.
    def change_classifier(self, text):
        """
        Ändern des Klassifizierers basierend auf der Auswahl im Dropdown-Menü.

        Parameter: text (str): Text des ausgewählten Klassifizierers.
        """
        try:
            self.btn_choose_classifier.setEnabled(False)
            self.slider_custom_scaleFactor.setEnabled(False)
            self.slider_custom_minNeighbors.setEnabled(False)
            self.slider_custom_minSize.setEnabled(False)
            self.custom_classifier_label.setText("")
            if text == "face":
                self.load_predefined_classifier("face")
            elif text == "eye":
                self.load_predefined_classifier("eye")
            elif text == "smile":
                self.load_predefined_classifier("smile")
            elif text == "upperbody":
                self.load_predefined_classifier("upperbody")
            elif text == "fullbody":
                self.load_predefined_classifier("fullbody")
            elif text == "profileface":
                self.load_predefined_classifier("profileface")
            elif text == "Eigener Klassifizierer":
                self.classifier_manager.current_classifier ="custom"
                self.btn_choose_classifier.setEnabled(True)
                self.slider_custom_scaleFactor.setEnabled(True)
                self.slider_custom_minNeighbors.setEnabled(True)
                self.slider_custom_minSize.setEnabled(True)
                self.custom_classifier_label.setText("Datei auswählen...")
            else:
                self.classifier_manager.load_classifier("face")
        except Exception as e:
            print(f"Fehler beim Ändern des Klassifizierers: {str(e)}") # Debug-Ausgabe in Konsole
            self.status.showMessage(f"Fehler beim Ändern des Klassifizierers: {str(e)}") # Statusnachricht in Statusleiste
            

    # Lädt vordefinierte Klassifizierer mit den entsprechenden Parametern.
    def load_predefined_classifier(self, classifier_id):
        """
        Lädt einen vordefinierten Klassifizierer basierend auf der Klassifizierer ID.

        Parameter: classifier_id (str): ID des Klassifizierers (z. B. "face", "eye", "smile").
        """
        try:
            self.classifier_manager.load_classifier(classifier_id)
            self.slider_custom_scaleFactor.blockSignals(True)
            self.slider_custom_minNeighbors.blockSignals(True)
            self.slider_custom_minSize.blockSignals(True)
            self.slider_custom_scaleFactor.setValue(int(self.classifier_manager.classifiers[classifier_id]["scaleFactor"]*10))
            self.label_custom_scaleFactor.setText(f"scaleFactor: {self.classifier_manager.classifiers[classifier_id]['scaleFactor']}")
            self.slider_custom_minNeighbors.setValue(self.classifier_manager.classifiers[classifier_id]["minNeighbors"])
            self.label_custom_minNeighbors.setText(f"minNeighbors: {self.classifier_manager.classifiers[classifier_id]['minNeighbors']}")
            self.slider_custom_minSize.setValue(self.classifier_manager.classifiers[classifier_id]["minSize"][0])
            self.label_custom_minSize.setText(f"minSize: {self.classifier_manager.classifiers[classifier_id]['minSize'][0]}")
            self.slider_custom_scaleFactor.blockSignals(False)
            self.slider_custom_minNeighbors.blockSignals(False)
            self.slider_custom_minSize.blockSignals(False)
            self.status.showMessage(f"Vordefinierter Klassifizierer {classifier_id} geladen.")
        except Exception as e:
            print(f"Fehler beim Laden des vordefinierten Klassifizierers: {str(e)}") # Debug-Ausgabe in Konsole
            self.status.showMessage(f"Fehler beim Laden des vordefinierten Klassifizierers: {str(e)}") # Statusnachricht in Statusleiste
            

    # Lädt benutzerdefinierten Klassifizierer aus einer Datei.
    def load_custom_classifier(self):
        try:
            classifier_name = self.classifier_manager.load_custom_classifier()
            self.custom_classifier_label.setText(classifier_name)
            self.status.showMessage(f"Benutzerdefinierter Klassifizierer {classifier_name} geladen.")
        except Exception as e:
            print(f"Fehler beim Laden des benutzerdefinierten Klassifizierers: {str(e)}") # Debug-Ausgabe in Konsole
            self.status.showMessage(f"Fehler beim Laden des benutzerdefinierten Klassifizierers: {str(e)}") # Statusnachricht in Statusleiste
            

    # Aktualisiert die Liste der verfügbaren Kameras.
    def refresh_camera_list(self):
        """
        Aktualisiert die Liste der verfügbaren Kameras.
        """
        try:
            available_cameras = self.camera_manager.detect_cameras()
            self.camera_selector.clear()
            if available_cameras:
                camera_names = [f"Kamera {index}" for index in available_cameras]
                self.camera_selector.addItems(camera_names)
                self.status.showMessage(f"Kameras gefunden: {camera_names}")
                self.btn_start_camera.setEnabled(True)
                self.btn_start_camera.setProperty("status","start")
                self.btn_start_camera.style().unpolish(self.btn_start_camera) # Zurücksetzen des Styles 
                self.btn_start_camera.style().polish(self.btn_start_camera) # Neuanwenden des Styles
            else:
                self.camera_selector.addItem("Keine Kamera erkannt")
                self.status.showMessage("Keine Kameras gefunden.")
                self.btn_start_camera.setEnabled(False) # Bug: setEnable ändert Button-Style nicht automatisch"
                self.btn_start_camera.setProperty("status", "unavailable") # Ändert Style des Buttons durch Property (Style Sheet)
                self.btn_start_camera.style().unpolish(self.btn_start_camera) # Zurücksetzen des Styles 
                self.btn_start_camera.style().polish(self.btn_start_camera) # Neuanwenden des Styles
        except Exception as e:
            print(f"Fehler beim Aktualisieren der Kamera-Liste: {str(e)}") # Debug-Ausgabe in Konsole
            

    # Startet die Kamera.   
    def start_camera(self):
        """
        Startet die Kamera basierend auf dem ausgewählten Kamera-Index.
        """
        camera_index = self.camera_selector.currentIndex()  # Kamera-Index auswählen
        try:
            self.btn_refresh_cameras.setEnabled(False)
            self.camera_selector.setEnabled(False)
            self.mode_selector.setEnabled(False)
            self.classifier_selector.setEnabled(False)
            self.btn_screenshot.setEnabled(True)
            self.btn_start_camera.setProperty("status","stop")
            self.btn_start_camera.style().unpolish(self.btn_start_camera)  # Reset style
            self.btn_start_camera.style().polish(self.btn_start_camera)    # Reapply style
            self.btn_start_camera.setText("Live-Kamera Stoppen")
            self.camera_manager.start_camera(camera_index)
            print(f"Kamera {camera_index} erfolgreich gestartet.")
            self.status.showMessage(f"Kamera {camera_index} erfolgreich gestartet.")
            self.timer.start(10)  # Update alle 10 ms
        except Exception as e:
            self.animation_label.setText(f"Kamera konnte nicht gestartet werden: {str(e)}") 
            self.status.showMessage(f"Kamera-Fehler: {str(e)}")
            print(f"Kamera konnte nicht gestartet werden: {str(e)}") # Debug-Ausgabe in Konsole
        
    
    # Stoppt die Kamera.
    def stop_camera(self):
        """
        Stoppt die Kamera und gibt Ressourcen frei.
        """
        try:
            self.btn_refresh_cameras.setEnabled(True)
            self.camera_selector.setEnabled(True)
            self.mode_selector.setEnabled(True)
            self.classifier_selector.setEnabled(True)
            self.btn_screenshot.setEnabled(False)
            self.btn_start_camera.setProperty("status","start") # Setzt Property für Style zurück
            self.btn_start_camera.style().unpolish(self.btn_start_camera) # Zurücksetzen des Styles 
            self.btn_start_camera.style().polish(self.btn_start_camera) # Neuanwenden des Styles
            self.btn_start_camera.setText("Live-Kamera Starten")
            self.status.showMessage("Kamera wird gestoppt...") # Statusnachricht in Statusleiste
            self.camera_manager.stop_camera() # Kamera stoppen aus CameraManager ausführen
            self.timer.stop() # Timer stoppen(keine Frames mehr aktualisieren)
            self.num_objects = 0 # Anzahl der erkannten Objekte auf 0 zurücksetzen
            self.object_count_label.setText(f"<a style=\"text-decoration:none;\" href=\"http://www.easteregg.com\"> {self.num_objects} </a>")
            self.current_frame = None # Bild löschen
            self.image_display.clear()  # Bildanzeige leeren
            self.image_display.setText("Anzeigebereich für Bilder/Kamera")  # Optionale Standardnachricht
            self.status.showMessage("Kamera gestoppt.") # Statusnachricht in Statusleiste
        except Exception as e: # Fehlerbehandlung
            print(f"Fehler beim Stoppen der Kamera: {str(e)}") # Debug-Ausgabe in Konsole
            


    # Startet oder stoppt die Kamera, je nach Status des Buttons.
    def start_stop_camera(self,checked):
        """
        Startet oder stoppt die Kamera basierend auf dem Status des Buttons.

        Parameter: checked (bool): Status des Buttons (True = Start, False = Stop).
        """
        if checked:                 
            self.start_camera()
            print("Kamera gestartet") # Debug-Ausgabe in Konsole
        else:
            self.stop_camera()
            print("Kamera gestartet") # Debug-Ausgabe in Konsole
        

    # Lädt ein Bild aus einer Datei.
    def load_image_from_file(self):
        """
        Läd ein Bild aus einer Datei und zeigt es in der GUI an. (Dateiauswahl über System-Dialog)
        """
        try:
            self.btn_refresh_cameras.setEnabled(False)
            self.camera_selector.setEnabled(False)
            self.mode_selector.setEnabled(False)
            self.classifier_selector.setEnabled(False)
            self.btn_load_image.setProperty("status","stop") # Setzt Property für Style zurück
            self.btn_load_image.style().unpolish(self.btn_load_image) # Zurücksetzen des Styles
            self.btn_load_image.style().polish(self.btn_load_image) # Neuanwenden des Styles 
            self.btn_load_image.setText("Bild Reset")
            self.status.showMessage("Bild wird geladen...") # Statusnachricht in Statusleiste
            file_path = self.file_manager.open_file_picture() # Aufruf der Methode zum Öffnen einer Datei aus dem FileManager
            if file_path:
                self.static_image = self.file_manager.load_image(file_path) # Aufruf der Methode zum Laden eines Bildes aus dem FileManager
                self.static_image = cv2.cvtColor(self.static_image, cv2.COLOR_BGR2RGB) # OpenCV (standard) BGR, Umwandlung in RGB
                self.btn_start_camera.setEnabled(False)
                self.timer.start(50) # Update alle 50 ms
                self.status.showMessage(f"Bild {file_path} erfolgreich geladen.") # Statusnachricht in Statusleiste
                print(f"Bild {file_path} erfolgreich geladen.") # Debug-Ausgabe in Konsole

        except Exception as e: # Fehlerbehandlung
            self.status.showMessage(f"Fehler beim Laden des Bildes: {str(e)}")
            print(f"Fehler beim Laden des Bildes: {str(e)}") # Debug-Ausgabe in Konsole
        

    # Setzt das Bild zurück.
    def reset_image(self):
        """
        Setzt das Bild zurück und löscht es aus der Anzeige.
        """
        try:
            self.btn_refresh_cameras.setEnabled(True)
            self.camera_selector.setEnabled(True)
            self.classifier_selector.setEnabled(True)
            self.mode_selector.setEnabled(True)
            
            self.btn_load_image.setProperty("status","start")
            self.btn_load_image.style().unpolish(self.btn_load_image)  
            self.btn_load_image.style().polish(self.btn_load_image)   
            self.btn_load_image.setText("Bild Laden")
            self.status.showMessage("Bild wird zurückgesetzt...")
            self.static_image = None # Bild löschen
            self.timer.stop() # Timer stoppen (keine Frames mehr aktualisieren)
            self.btn_screenshot.setEnabled(False)
            self.image_display.clear() # Bildanzeige leeren
            self.image_display.setText("Anzeigebereich für Bilder/Kamera")
            self.num_objects = 0 # Anzahl der erkannten Objekte auf 0 zurücksetzen
            self.object_count_label.setText(f"<a style=\"text-decoration:none;\" href=\"http://www.easteregg.com\"> {self.num_objects} </a>")
            self.status.showMessage("Bild zurückgesetzt.") # Statusnachricht in Statusleiste 
            print("Bild zurückgesetzt.") # Debug-Ausgabe in Konsole
        except Exception as e: # Fehlerbehandlung
            self.status.showMessage(f"Fehler beim Zurücksetzen des Bildes: {str(e)}")
            print(f"Fehler beim Zurücksetzen des Bildes: {str(e)}") # Debug-Ausgabe in Konsole
        

    # Lädt ein Bild aus einer Datei und setzt den Button zurück.
    def load_reset_file(self, checked):
        """
        Läd ein Bild aus einer Datei und setzt den Button zurück.

        Parameter: checked (bool): Status des Buttons (True = Laden, False = Zurücksetzen).
        """
        try:
            if checked:
                self.load_image_from_file()
                print("Bild laden...")
            else:
                self.reset_image()
                print("Bild zurücksetzen...")
        except Exception as e: # Fehlerbehandlung
            print(f"Fehler beim Laden/Zurücksetzen des Bildes: {str(e)}") # Debug-Ausgabe in Konsole
        

    # Erstellt einen Screenshot des aktuellen Frames.
    def save_screenshot(self):
        """
        Speichert einen Screenshot des aktuellen Frames.
        """
        try:
            self.status.showMessage("Screenshot wird gespeichert...")
            
            if self.file_manager.save_screenshot(self.current_frame): # Aufruf der Methode zum Speichern eines Screenshots aus dem FileManager
                self.status.showMessage("Screenshot erfolgreich gespeichert.")
            else:
                self.status.showMessage("Fehler: Screenshot konnte nicht gespeichert werden.")
        except Exception as e: # Fehlerbehandlung
            print(f"Fehler beim Speichern des Screenshots: {str(e)}") # Debug-Ausgabe in Konsole
            
        
    # Aktualisiert den scaleFactor des Klassifizierers basierend auf dem Slider-Wert.
    def update_scaleFactor(self, value):
        try:
            self.classifier_manager.update_scaleFactor(value/10)
            self.label_custom_scaleFactor.setText(f"scaleFactor: {value/10}")
        except Exception as e:
            print(f"Fehler beim Aktualisieren von scaleFactor: {str(e)}") # Debug-Ausgabe in Konsole    
            

    # Aktualisiert den minNeighbors des Klassifizierers basierend auf dem Slider-Wert.
    def update_minNeighbors(self, value):
        try:
            self.classifier_manager.update_minNeighbors(value)
            self.label_custom_minNeighbors.setText(f"minNeighbors: {value}")
        except Exception as e: # Fehlerbehandlung
            print(f"Fehler beim Aktualisieren von minNeighbors: {str(e)}") # Debug-Ausgabe in Konsole
            

    # Aktualisiert den minSize des Klassifizierers basierend auf dem Slider-Wert.
    def update_minSize(self, value):
        try:
            self.classifier_manager.update_minSize(value)
            self.label_custom_minSize.setText(f"minSize: {value}")
        except Exception as e: # Fehlerbehandlung
            print(f"Fehler beim Aktualisieren von minSize: {str(e)}") # Debug-Ausgabe in Konsole    
            

    # Holt ein Frame von der Kamera und zeigt es in der GUI an. 
    def update_frame(self):
        """
        Lädt den aktuellen Frame, auf grundlage das Aktuellen Modus(live/file) und erkennt Objekte und zeigt Sie in der GUI an.
        """
        try:
            if self.mode_selector.currentText() == "live": # Abfrage des aktuellen Modus, wenn Modus "live", dann
                frame, ret = self.camera_manager.get_frame() # Frame von Kamera holen mit Aufruf aus CameraManager
                if not ret: # Wenn Kamera keine Frames mehr liefert/disconnected, stoppe Kamera und aktualisiere Kamera-Liste
                    self.stop_camera()
                    self.refresh_camera_list()
                    self.btn_start_camera.setChecked(False)
                    return  
                
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # OpenCV (standard) BGR, Umwandlung in RGB
                self.current_frame = frame

                # Objekterkennung
                objects = self.classifier_manager.detect_faces(frame, self.classifier_manager.current_classifier) # Aufruf der Methode zur Objekterkennung aus dem ClassifierManager
                self.num_objects = len(objects) # Anzahl der erkannten Objekte
                self.object_count_label.setText(f"<a style=\"text-decoration:none;\" href=\"http://www.easteregg.com\"> {self.num_objects} </a>")
                    
                # Zeichne grüne Rechtecke um erkannte Gesichter
                for (x, y, w, h) in objects:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2) # Zeichne grünes Rechteck um Objekt
                
                # Anzeige des Frames im Anzeigebereich
                height, width, channel = frame.shape # Größe des Frames
                aspect_ratio = height/width # Seitenverhältnis
                bytes_per_line = 3 * width  # 3 Kanäle pro Pixel (RGB)

                q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888) # Erstelle QImage aus Frame 
                pixmap = QPixmap.fromImage(q_image) # Erstelle Pixmap aus QImage

                # Logik für das Skalieren des Bildes
                i_h = self.image_display.height() # Höhe des QLabel(image_display)
                w_asp = int(i_h * (width/height)) # Berechne Breite des Bildes basierend auf Höhe und Seitenverhältnis
                if(w_asp <= self.image_display.width()): 
                    i_w = w_asp 
                else:
                    i_w = self.image_display.width()
                    i_h = int(i_w * aspect_ratio)
                scaled_pixmap = pixmap.scaled(i_w,i_h) 
                self.image_display.setPixmap(scaled_pixmap) # Setze Pixmap in QLabel(image_display)
                
            elif self.mode_selector.currentText() == "file": # Abfrage des aktuellen Modus, wenn Modus "live", dann
                
                frame = self.static_image 
                self.current_frame = frame

                # Objekterkennung
                objects = self.classifier_manager.detect_faces(frame, self.classifier_manager.current_classifier)
                self.num_objects = len(objects) # Anzahl der erkannten Objekte
                self.object_count_label.setText(f"<a style=\"text-decoration:none;\" href=\"http://www.easteregg.com\"> {self.num_objects} </a>")
                    
                # Zeichne grüne Rechtecke um erkannte Gesichter
                for (x, y, w, h) in objects:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2) # Zeichne grünes Rechteck um Objekt

                height, width, channel = frame.shape # Größe des Frames
                aspect_ratio = height/width # Seitenverhältnis
                bytes_per_line = 3 * width  # 3 Kanäle pro Pixel (RGB)

                q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888) # Erstelle QImage aus Frame 
                pixmap = QPixmap.fromImage(q_image) # Erstelle Pixmap aus QImage

                # Logik für das Skalieren des Bildes
                i_h = self.image_display.height() # Höhe des QLabel(image_display)
                w_asp = int(i_h * (width/height)) # Berechne Breite des Bildes basierend auf Höhe und Seitenverhältnis
                if(w_asp <= self.image_display.width()): 
                    i_w = w_asp 
                else:
                    i_w = self.image_display.width()
                    i_h = int(i_w * aspect_ratio)
                scaled_pixmap = pixmap.scaled(i_w,i_h) 
                self.image_display.setPixmap(scaled_pixmap) # Setze Pixmap in QLabel(image_display)         
                

            # Screenshot-Button aktivieren, wenn Frame vorhanden
            if not self.current_frame is None:
                self.btn_screenshot.setEnabled(True)
            else:
                self.btn_screenshot.setEnabled(False)
            self.current_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_RGB2BGR) # OpenCV (standard) BGR, Umwandlung in RGB
            # Zeichne grüne Rechtecke um erkannte Gesichter
            for (x, y, w, h) in objects:
                cv2.rectangle(self.current_frame, (x, y), (x + w, y + h), (0, 255, 0), 2) # Zeichne grünes Rechteck um Objekt
        except Exception as e: # Fehlerbehandlung
            print(f"Fehler beim Aktualisieren des Frames: {str(e)}") # Debug-Ausgabe in Konsole
            


