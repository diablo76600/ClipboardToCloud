import sys
import os
import time
from pathlib import Path


class DirectoryError(Exception):
    """Levée d'exception lorsque la création du répertoire sur le cloud échoue."""

    def __init__(self, message) -> None:
        """Contructeur
        Args:
            message (str): Affiche le message d'erreur associé à l'exception.
        """
        self.message = message


class ServiceDirectoryAndFile:
    """Gestionnaire du répertoire sur le cloud et le fichier binaire."""

    def __init__(self, path_cloud: str, path_file: str, title: str) -> None:
        """Constructeur
        Args:
            path_cloud (str, optional): Chemin du répertoire sur le cloud. Defaults to None.
            path_file (str, optional): Chemin du fichier binaire sur le cloud. Defaults to None.
            title (str, optional): Titre de l'application. Defaults to None.
        """
        
        self.path_cloud = path_cloud
        self.path_file = path_file
        self.title = title
        self.file_is_changed = False

    def directory_exist_and_create_file_with_title(self) -> None:
        """Controle et création du répertoire sur le Cloud"""

        if not os.path.isdir(self.path_cloud):
            try:
                file = Path(self.path_file)
                file.parent.mkdir(exist_ok=True, parents=True)
                file.write_text(self.title, encoding="utf-8")
            except PermissionError:
                raise DirectoryError(
                    message=f"Impossible de créer le répertoire {self.path_cloud}"
                )

    def read_binary_file(self):
        """Lecture du fichier binaire sur le cloud

        Returns:
            _type_: _description_
        """
        while True:
            try:
                with open(self.path_file, "rb") as file:
                    data = file.read()
                    break
            except FileNotFoundError:
                time.sleep(0.1)
        return data

    @staticmethod
    def resource_path(relative_path: str) -> str:
        """Utilisation du chemin absolu pour PyInstaller (option -ONEFILE)."""

        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)  # type: ignore
        return relative_path