# -*- Coding: utf-8 -*-
# Created by Diablo76 on 14/02/2023 -- 07:41:27.
""" ClipboardToCloud est un script qui permet de récupérer le contenu
    du presse-papier d'un ordinateur à un autre
    sans tenir compte de l'OS et du réseau.
    Par défaut, il fonctionne avec Dropbox mais il peut être adapté
    pour d'autre Cloud (Google Drive etc...) """

import os
import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QImage, QPixmap, QCursor
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QLabel,
    QWidget,
    QMenu,
    QMessageBox,
    QSystemTrayIcon,
)

# Constantes globales
VERSION = "1.9.01"
CLOUD = "Dropbox"
HOME = os.path.expanduser("~")
PATH_CLOUD = f"{HOME}{os.sep}{CLOUD}{os.sep}.ClipboardToCloud{os.sep}"
PATH_FILE = PATH_CLOUD + "clipboard.data"
TITLE = f"Clipboard To {CLOUD} {VERSION}"


class DirectoryError(Exception):
    def __init__(self, message):
        self.message = message


class ServiceDirectoryAndFile:

    def __init__(self, path_cloud = None, path_file = None, title = None):
        self.path_cloud: str = path_cloud or PATH_CLOUD
        self.path_file: str = path_file or PATH_FILE
        self.title: str = title or TITLE

        self.old_data = None
        self.new_data = None

    def data_changed(self) -> float:
        """Contrôle du fichier binaire"""
        new_data: float = os.stat(self.path_file).st_mtime
        if new_data != self.old_data:
            self.old_data = new_data
    
    def directory_exist_and_create_file_with_title(self) -> None:
        """Controle et création du répertoire sur le Cloud"""
        if not os.path.isdir(self.path_cloud):
            try:
                os.mkdir(self.path_cloud)
                with open(self.path_file, "wb") as file:
                    file.write(self.title.encode("utf-8"))
            except (FileNotFoundError, PermissionError):
                raise DirectoryError(message=f"Impossible de créer le répertoire {self.path_cloud}")

    @staticmethod
    def resource_path(relative_path: str) -> str:
        """Utilisation du chemin absolu pour PyInstaller option -ONEFILE)"""
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return relative_path


class ToolTip(QLabel):
    """Affichage d'un QLabel d'apparence QToolTip"""


    def __init__(self, app) -> None:

        super().__init__()
        self.setWindowFlags(Qt.ToolTip)  # type: ignore
        self.setStyleSheet(
            "border: 1px solid black; background-color: rgb(255,239,213)"
        )
        self.setWindowOpacity(0.8)
        self.center = app.screens()[0].availableGeometry().center()

    def show(self) -> None:
        """Affichage du tooltip au centre de l'écran
        avec une durée de 2.5 secondes"""

        super().show()
        self.move(
            int(self.center.x() - self.width() / 2),
            int(self.center.y() - self.height() / 2),
        )
        QTimer.singleShot(2500, self.hide)


class Clipboard:
    
    def __init__(self, app, path_file=None, cloud=None):
        self.app = app
        self.obj = app.clipboard()
        self.path_file = path_file or PATH_FILE
        self.cloud = cloud or CLOUD

    def copy_to_cloud(self) -> None:

        if self.obj.mimeData().formats():

            if self.obj.mimeData().hasImage():
                pixmap = self.obj.pixmap()
                pixmap.save(self.path_file, "PNG")
                self.show_message(f"Image transférée sur {self.cloud}.", QIcon(pixmap))

            elif self.obj.mimeData().hasText():
                text = self.obj.text()
                with open(self.path_file, "wb") as file:
                    file.write(text.encode("utf-8"))
                self.show_message(
                    f"Texte transféré sur {self.cloud}.", self.icons["Dropbox"]
                )
            self.old_data = os.stat(self.path_file).st_mtime

        else:

            self.show_message(
                "Le Presse-papier est vide !!!.",
                QSystemTrayIcon.Warning,  # type: ignore
            )
    
    def paste_to_clipboard(self) -> None:

        with open(self.path_file, "rb") as file:
            data = file.read()
        header = data[0:4]

        if header == b"\x89PNG":

            image = QImage.fromData(data)
            self.obj.setImage(image)
            self.show_message(
                "Image collée dans le Presse-papier.", QIcon(QPixmap(image))
            )

        else:

            self.obj.setText(data.decode("utf-8"))
            self.show_message(
                "Texte collé dans le Presse-papier.", self.icons["Clipboard"]
            )
    
    def show_clipboard(self) -> None:
        """Affichage du presse-papier"""

        if self.obj.mimeData().formats():

            if self.obj.mimeData().hasImage():

                pixmap = self.obj.pixmap().scaledToWidth(
                    350, Qt.SmoothTransformation | Qt.KeepAspectRatio  # type: ignore
                )
                self.tool_tip.setPixmap(pixmap)

            else:

                self.tool_tip.setText(self.obj.text())
            self.tool_tip.show()

        else:

            self.show_message(
                "Le Presse-papier est vide !!!.",
                QSystemTrayIcon.Warning,  # type: ignore
            )


class ClipboardToCloudManager:
    """ClipboardToCloudManager"""

    def __init__(self, app=None):

        self.app = app or QApplication(sys.argv)
        self.widget = QWidget()
        self.service_directory_file = ServiceDirectoryAndFile()
        self.tool_tip = ToolTip(app=self.app)
        self.clipboard = Clipboard(app=self.app)
        self._exec()
        self.tray = QSystemTrayIcon()
        self._icons = self._set_icons()
        self.create_trayicon()
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.service_directory_file.data_changed)
        self.timer.start()

    def _set_icons(self):

        return {
            "Dropbox": QIcon(
                QPixmap(ServiceDirectoryAndFile.resource_path("Icons/dropbox.png")).scaledToWidth(
                    32, Qt.SmoothTransformation  # type: ignore
                )
            ),
            "Clipboard": QIcon(
                QPixmap(ServiceDirectoryAndFile.resource_path("Icons/clipboard.png")).scaledToWidth(
                    32, Qt.SmoothTransformation  # type: ignore
                )
            ),
            "Loupe": QIcon(
                QPixmap(ServiceDirectoryAndFile.resource_path("Icons/loupe.png")).scaledToWidth(
                    32, Qt.SmoothTransformation  # type: ignore
                )
            ),
        }

    def _exec(self):

        self.directory_exist_and_create_file_with_title()

    def directory_exist_and_create_file_with_title(self) -> None:

        try:
            self.service_directory_file.directory_exist_and_create_file_with_title()
        except DirectoryError as err:
            QMessageBox.warning(
                    self.widget, self.service_directory_file.title, err.message
            )

    def copy_to_cloud(self) -> None:
        """Copie du fichier binaire sur le Cloud"""

        self.clipboard.copy_to_cloud()

    def paste_to_clipboard(self) -> None:
        """Copie du fichier binaire du cloud vers le presse-papier"""

        self.clipboard.paste_to_clipboard()

    def create_trayicon(self):
        """Création du QSystemTrayIcon"""

        self.tray.setIcon(self._icons["Clipboard"])
        self.tray.setVisible(True)
        self.tray.setToolTip(TITLE)
        if sys.platform == "win32":
            self.tray.activated.connect(self.tray_reason)
        menu = QMenu(self.widget)
        opt_copy = QAction(
            parent=self.widget, text=f"Transféré sur {CLOUD}", icon=self._icons["Dropbox"]
        )
        opt_copy.triggered.connect(self.copy_to_cloud)
        menu.addAction(opt_copy)
        opt_paste = QAction(
            parent=self.widget,
            text="Coller dans le Presse-papier",
            icon=self._icons["Clipboard"],
        )
        opt_paste.triggered.connect(self.paste_to_clipboard)
        menu.addAction(opt_paste)
        show_clipboard = QAction(
            parent=self.widget, text="Apperçu du presse-papier", icon=self._icons["Loupe"]
        )
        show_clipboard.triggered.connect(self.show_clipboard)
        menu.addAction(show_clipboard)
        menu.addSeparator()

        quit_app = QAction(parent=self.widget, text="Quitter")
        quit_app.triggered.connect(self.app.quit)
        menu.addAction(quit_app)
        self.tray.setContextMenu(menu)

    def tray_reason(self, reason: int):
        """Affichage du menu (Windows) avec le clic gauche"""

        if reason == self.tray.Trigger:  # type: ignore
            self.tray.contextMenu().popup(QCursor.pos())

    def show_clipboard(self):
        """Affichage du presse-papier"""

        self.clipboard.show_clipboard()

    def show_message(self, message: str, icon: QIcon, duration: int = 3000):
        """Affichage de la notification avec une durée de 3 secondes par défaut"""

        self.tray.showMessage(TITLE, message, icon, duration)
    
    def mainloop(self):

        sys.exit(manager.app.exec_())

if __name__ == "__main__":

    manager = ClipboardToCloudManager()
    manager.mainloop()
