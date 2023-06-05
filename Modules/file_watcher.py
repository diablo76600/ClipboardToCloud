from service_directory_file import ServiceDirectoryAndFile
from PyQt5.QtCore import QFileSystemWatcher


class FileWatcher:
    """Surveillance des modifications du fichier binaire sur le cloud."""

    def __init__(self, path_file: str, manager, service: ServiceDirectoryAndFile) -> None:
        """Constructeur

        Args:
            path_file (str): Chemin de fichier bimaire
            manager (ClipboardToCloud): Instance de la classe ClipboardToCloudManager.
            service (ServiceDirectoryAndFile): Instance de la classe ServiceDirectoryAndFile.
        """
        
        self._watcher = QFileSystemWatcher()
        self._watcher.addPath(path_file)
        self._watcher.fileChanged.connect(self.file_changed)
        self.service_directory_file = service
        self.manager = manager

    def file_changed(self) -> None:
        """ """

        if self.service_directory_file.file_is_changed is False:
            self.manager.paste_to_clipboard()
        self.service_directory_file.file_is_changed = False
