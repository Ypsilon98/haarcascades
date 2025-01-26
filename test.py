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

