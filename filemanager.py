from tkinter import filedialog

class FileManager:
    @staticmethod
    def open_file_dialog(title="Datei auswählen", filetypes=(("Bilder", "*.jpg;*.png;*.jpeg"), ("Alle Dateien", "*.*"))):
        file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
        return file_path