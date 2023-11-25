from service_directory_file import ServiceDirectoryAndFile
from tooltip import ToolTip
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSystemTrayIcon, QApplication


class ClipboardManager:
    """Gestionnaire des opérations de copier/coller du presse-papier."""

    def __init__(
        self,
        app: QApplication,
        service: ServiceDirectoryAndFile,
        path_file: str,
        cloud: str,
    ) -> None:
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

    def set_icons(self) -> dict:
        """Initialise et retourne un dictionnaire d'icônes utilisées dans l'application."""

        def get_icon(asset_name):
            return QIcon(
                QPixmap(
                    ServiceDirectoryAndFile.resource_path(f"Assets/{asset_name}.png")
                ).scaledToWidth(
                    32, Qt.SmoothTransformation  # type: ignore
                )
            )

        return {
            self.cloud: get_icon(self.cloud),
            "Clipboard": get_icon("Clipboard"),
            "Loupe": get_icon("Loupe"),
        }

    def copy_to_cloud(self) -> tuple:  # type: ignore
        """Copie le contenu du presse-papier vers le fichier binaire sur le cloud."""

        if not self.clipboard.mimeData().formats():
            return "Le Presse-papier est vide !!!.", QSystemTrayIcon.Warning  # type: ignore

        self.service_directory_file.file_is_changed = True

        if self.clipboard.mimeData().hasImage():
            pixmap = self.clipboard.pixmap()
            self.service_directory_file.save_pixmap_to_cloud(pixmap)
            return f"Image transférée sur {self.cloud}", QIcon(pixmap)

        if self.clipboard.mimeData().hasText():
            text = self.clipboard.text()
            self.service_directory_file.save_text_to_cloud(text)
            return f"Texte transféré sur {self.cloud}", self._icons["Clipboard"]

    def paste_to_clipboard(self) -> tuple:
        """Colle le contenu du fichier binaire du cloud vers le presse-papier."""
        data = self.service_directory_file.read_binary_file()
        header = data[:4]
        if header == b"\x89PNG":
            image = QImage.fromData(data)
            self.clipboard.setImage(image)
            message = "Image collée dans le Presse-papier."
            type_message = QIcon(QPixmap(image))
            return message, type_message
        else:
            self.clipboard.setText(data.decode("utf-8"))
            message = "Texte collé dans le Presse-papier."
            type_message = self._icons["Clipboard"]
        return message, type_message

    def show_clipboard(self) -> tuple:
        """Affiche le contenu actuel du presse-papier."""
        if not self.clipboard.mimeData().formats():
            return "Le Presse-papier est vide !!!.", QSystemTrayIcon.Warning  # type: ignore
        if self.clipboard.mimeData().formats():
            if self.clipboard.mimeData().hasImage():
                pixmap = self._get_scaled_pixmap()
                self._set_pixmap(pixmap)
            else:
                self._set_text(self.clipboard.text())
            self._show_tooltip()
        return None, None

    def _get_scaled_pixmap(self):
        return self.clipboard.pixmap().scaledToWidth(
            350, Qt.SmoothTransformation | Qt.KeepAspectRatio  # type: ignore
        )

    def _set_pixmap(self, pixmap):
        self._tool_tip.setPixmap(pixmap)

    def _set_text(self, text):
        self._tool_tip.setText(text)

    def _show_tooltip(self):
        self._tool_tip.show()
