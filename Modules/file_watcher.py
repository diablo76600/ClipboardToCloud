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

        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(path_file)
        self.watcher.fileChanged.connect(self.file_changed)
        self.service_directory_file = service
        self.manager = manager

    
        """ """
    def file_changed(self):
        """Controle des modification du fichier binaire"""

        self.service_directory_file.check_file_changed()
        if not self.service_directory_file.file_is_changed:
            self.manager.paste_to_clipboard()
        self.service_directory_file.file_is_changed = False
