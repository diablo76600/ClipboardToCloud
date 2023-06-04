import sys
import os


class DirectoryError(Exception):
    """Levée d'exception lorsque la création du répertoire sur le cloud échoue."""

    def __init__(self, message):
        """Contructeur
        Args:
            message (str): Affiche le message d'erreur associé à l'exception.
        """
        self.message = message


class ServiceDirectoryAndFile:
    """Gestionnaire du répertoire sur le cloud et le fichier binaire."""

    def __init__(self, path_cloud, path_file, title):
        """Constructeur
        Args:
            path_cloud (str, optional): Chemin du répertoire sur le cloud. Defaults to None.
            path_file (str, optional): Chemin du fichier binaire sur le cloud. Defaults to None.
            title (str, optional): Titre de l'application. Defaults to None.
        """
        self.path_cloud: str = path_cloud
        self.path_file: str = path_file
        self.title: str = title
        try:
            self.old_data = os.stat(self.path_file).st_mtime
        except FileNotFoundError:
            self.old_data = None
        self.data_is_changed = False

    def data_changed(self):
        """Contrôle si le fichier binaire a été modifié depuis la dernière vérification."""
        new_data = os.stat(self.path_file).st_mtime
        if new_data != self.old_data:
            # manager.paste_to_clipboard()  Ne pas dépendre de l'UI
            self.data_is_changed = True
            self.old_data = new_data
        else:
            self.data_is_changed = False

    def directory_exist_and_create_file_with_title(self) -> None:
        """Controle et création du répertoire sur le Cloud"""
        if not os.path.isdir(self.path_cloud):
            try:
                os.mkdir(self.path_cloud)
                with open(self.path_file, "wb") as file:
                    file.write(self.title.encode("utf-8"))
            except PermissionError:
                raise DirectoryError(
                    message=f"Impossible de créer le répertoire {self.path_cloud}"
                )

    @staticmethod
    def resource_path(relative_path: str) -> str:
        """Utilisation du chemin absolu pour PyInstaller (option -ONEFILE)."""
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)  # type: ignore
        return relative_path
