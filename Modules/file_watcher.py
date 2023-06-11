import os
from PyQt5.QtCore import QFileSystemWatcher
from service_directory_file import ServiceDirectoryAndFile



class FileWatcher(QFileSystemWatcher):
    """Surveillance des modifications du fichier binaire sur le cloud."""

    def __init__(self, path_file: str, manager, service: ServiceDirectoryAndFile) -> None:
        """Constructeur

        Args:
            path_file (str): Chemin de fichier bimaire
            manager (ClipboardToCloud): Instance de la classe ClipboardToCloudManager.
            service (ServiceDirectoryAndFile): Instance de la classe ServiceDirectoryAndFile.
        """
        super().__init__()
        self.path_file = path_file
        self.addPath(self.path_file)
        self.fileChanged.connect(self.file_changed)
        self.service_directory_file = service
        self.manager = manager

    
        """ """
    def file_changed(self):
        """Controle des modification du fichier binaire"""
        
        if not self.service_directory_file.file_is_changed:
            self.manager.paste_to_clipboard()
        self.service_directory_file.file_is_changed = True

