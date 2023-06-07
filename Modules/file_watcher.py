import os
from PyQt5.QtCore import QTimer, QObject
from service_directory_file import ServiceDirectoryAndFile



class FileWatcher:
    """Surveillance des modifications du fichier binaire sur le cloud."""

    def __init__(self, path_file: str, manager, service: ServiceDirectoryAndFile) -> None:
        """Constructeur

        Args:
            path_file (str): Chemin de fichier bimaire
            manager (ClipboardToCloud): Instance de la classe ClipboardToCloudManager.
            service (ServiceDirectoryAndFile): Instance de la classe ServiceDirectoryAndFile.
        """

        self.file_path = path_file
        self.last_modified = os.stat(path_file).st_mtime

        # Créez un QTimer pour vérifier périodiquement les modifications
        self.timer = QTimer()
        self.timer.timeout.connect(self.file_changed)
        self.timer.start(1000)  # Vérifier toutes les 1 second
        self.service_directory_file = service
        self.manager = manager

    
        """ """
    def file_changed(self):
        self.service_directory_file.check_file_changed()
        if not self.service_directory_file.file_is_changed:
            self.manager.paste_to_clipboard()
        self.service_directory_file.file_is_changed = False
