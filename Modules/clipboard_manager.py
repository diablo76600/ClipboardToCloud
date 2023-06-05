import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from service_directory_file import ServiceDirectoryAndFile
from tooltip import ToolTip
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSystemTrayIcon


class ClipboardManager:
    """Gestionnaire des opérations de copier/coller du presse-papier."""

    def __init__(
        self, app, service: ServiceDirectoryAndFile, path_file: str, cloud: str
    ):
        """Contructeur
        Args:
            app (object): Instance de l'application.
            service (ServiceDirectoryAndFile) Instance de la classe ServiceDirectoryAndFile.
            path_file (str): Chemin du fichier binaire. Defaults to None.
            cloud (str): Nom du service cloud. Defaults to None.
        """
        self.app = app
        self.clipboard = app.clipboard()
        self.path_file = path_file
        self.cloud = cloud
        self._tool_tip = ToolTip(app)
        self._icons = self.set_icons()
        self.service_directory_file = service

    def set_icons(self):
        """Initialise et retourne un dictionnaire d'icônes utilisées dans l'application."""
        return {
            self.cloud: QIcon(
                QPixmap(
                    ServiceDirectoryAndFile.resource_path(f"Icons/{self.cloud}.png")
                ).scaledToWidth(
                    32, Qt.SmoothTransformation  # type: ignore
                )
            ),
            "Clipboard": QIcon(
                QPixmap(
                    ServiceDirectoryAndFile.resource_path("Icons/Clipboard.png")
                ).scaledToWidth(
                    32, Qt.SmoothTransformation  # type: ignore
                )
            ),
            "Loupe": QIcon(
                QPixmap(
                    ServiceDirectoryAndFile.resource_path("Icons/Loupe.png")
                ).scaledToWidth(
                    32, Qt.SmoothTransformation  # type: ignore
                )
            ),
        }

    def copy_to_cloud(self) -> tuple:
        """Copie le contenu du presse-papier vers le fichier binaire sur le cloud."""
        message = "Le Presse-papier est vide !!!."
        type_message = QSystemTrayIcon.Warning  # type: ignore
        if self.clipboard.mimeData().formats():
            if self.clipboard.mimeData().hasImage():
                pixmap = self.clipboard.pixmap()
                pixmap.save(self.path_file, "PNG")
                message = f"Image transférée sur {self.cloud}"
                type_message = QIcon(pixmap)
            elif self.clipboard.mimeData().hasText():
                text = self.clipboard.text()
                with open(self.path_file, "wb") as file:
                    file.write(text.encode("utf-8"))
                message = f"Texte transféré sur {self.cloud}"
                type_message = self._icons["Clipboard"]
        self.service_directory_file.file_is_changed = True
        return message, type_message

    def paste_to_clipboard(self) -> tuple:
        """Colle le contenu du fichier binaire du cloud vers le presse-papier."""
        with open(self.path_file, "rb") as file:
            data = file.read()
        header = data[0:4]
        message = "Texte collé dans le Presse-papier."
        type_message = self._icons["Clipboard"]
        if header == b"\x89PNG":
            image = QImage.fromData(data)
            self.clipboard.setImage(image)
            message = "Image collée dans le Presse-papier."
            type_message = QIcon(QPixmap(image))
        else:
            self.clipboard.setText(data.decode("utf-8"))
        return message, type_message

    def show_clipboard(self) -> tuple:
        """Affiche le contenu actuel du presse-papier."""
        message = "Le Presse-papier est vide !!!."
        type_message = QSystemTrayIcon.Warning  # type: ignore
        if self.clipboard.mimeData().formats():
            message = None
            type_message = None
            if self.clipboard.mimeData().hasImage():
                pixmap = self.clipboard.pixmap().scaledToWidth(
                    350, Qt.SmoothTransformation | Qt.KeepAspectRatio  # type: ignore
                )
                self._tool_tip.setPixmap(pixmap)
            else:
                self._tool_tip.setText(self.clipboard.text())
            self._tool_tip.show()
        return message, type_message
