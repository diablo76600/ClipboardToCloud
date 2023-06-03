# -*- Coding: utf-8 -*-
# Created by Diablo76 on 14/02/2023 -- 07:41:27.
""" ClipboardToCloud est un script qui permet de récupérer le contenu
    du presse-papier d'un ordinateur à un autre
    sans tenir compte de l'OS et du réseau.
    Par défaut, il fonctionne avec Dropbox mais il peut être adapté
    pour d'autre Cloud (Google Drive etc...) """

import os
import sys
from typing import Union
from service_directory_file import DirectoryError, ServiceDirectoryAndFile
from PyQt5.QtCore import Qt, QTimer, QFileSystemWatcher
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
VERSION = "1.9.04"
CLOUD = "Dropbox"
# Pour utiliser Google Drive :
# CLOUD = "Mon Drive"
HOME = os.path.expanduser("~")
PATH_CLOUD = f"{HOME}{os.sep}{CLOUD}{os.sep}.ClipboardToCloud{os.sep}"
PATH_FILE = PATH_CLOUD + "clipboard.data"
TITLE = f"Clipboard To {CLOUD} {VERSION}"





class ToolTip(QLabel):
    """Affichage d'un QLabel d'apparence QToolTip."""

    def __init__(self, ns: int = 2500) -> None:
        super().__init__()
        self.ns = ns
        self.setWindowFlags(Qt.ToolTip)  # type: ignore
        self.setStyleSheet(
            "border: 1px solid black; background-color: rgb(255,239,213)"
        )
        self.setWindowOpacity(0.8)
        self.center = app.screens()[0].availableGeometry().center()

    def show(self) -> None:
        """Affichage du tooltip au centre de l'écran
        avec une durée de 2.5 secondes."""
        super().show()
        self.move(
            int(self.center.x() - self.width() / 2),
            int(self.center.y() - self.height() / 2),
        )
        QTimer.singleShot(self.ns, self.hide)


class ClipboardToCloudManager(QWidget):
    """Gestionnaire de l'application et des interactions avec l'utilisateur."""

    def __init__(self):
        """Constructeur
        Args:
            app (object, optional): Instance de l'application. Defaults to None.
        """
        super().__init__()
        self.service_directory_file = ServiceDirectoryAndFile(path_cloud=PATH_CLOUD, path_file=PATH_FILE, title=TITLE)
        self.clipboard = Clipboard(self.service_directory_file)
        self.tray = TrayIcon(self)
        self.directory_exist_and_create_file_with_title()
        self.timer = TimerDataChanged(
            manager=self, service=self.service_directory_file
        )

    def copy_to_cloud(self) -> None:
        """Appel de la méthode copy_to_cloud() de l'objet clipboard de la classe Clipboard."""
        message, type_message = self.clipboard.copy_to_cloud()
        self.show_message(message=message, icon=type_message)

    def paste_to_clipboard(self) -> None:
        """Appel de la méthode paste_to_clipboard() de l'objet clipboard de la classe Clipboard."""
        message, type_message = self.clipboard.paste_to_clipboard()
        self.show_message(message=message, icon=type_message)

    def show_clipboard(self):
        """Appel de la méthode show_clipboard() de l'objet clipboard de la classe Clipboard."r"""
        message, type_message = self.clipboard.show_clipboard()
        if message:
            self.show_message(message=message, icon=type_message)

    def show_message(self, message: str, icon: QIcon, duration: int = 3000):
        """Affichage de la notification avec une durée de 3 secondes par défaut."""
        self.tray.showMessage(TITLE, message, icon, duration)

    def directory_exist_and_create_file_with_title(self) -> None:
        """Vérifie l'existence du répertoire sur le cloud et création du fichier binaire."""
        try:
            self.service_directory_file.directory_exist_and_create_file_with_title()
        except DirectoryError as err:
            QMessageBox.warning(
                    self.tray.widget, self.service_directory_file.title, err.message
            )
            sys.exit()


class Clipboard:
    """Gestionnaire des opérations de copier/coller du presse-papier."""

    def __init__(self, service: ServiceDirectoryAndFile, path_file=None, cloud=None):
        """Contructeur
        Args:
            app (object): Instance de l'application.
            path_file (str, optional): Chemin du fichier binaire. Defaults to None.
            cloud (str, optional): Nom du service cloud. Defaults to None.
        """
        self.clipboard = app.clipboard()
        self.path_file = path_file or PATH_FILE
        self.cloud = cloud or CLOUD
        self._tool_tip = ToolTip()
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
        self.service_directory_file.old_data = os.stat(self.path_file).st_mtime  # type: ignore
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


class TimerDataChanged:
    def __init__(
        self, manager: ClipboardToCloudManager, service: ServiceDirectoryAndFile
    ):
        self._obj = QTimer()
        self.manager = manager
        self.service_directory_file = service
        self._initialize_timer()

    def _initialize_timer(self, interval=1000):
        self._obj.setInterval(interval)
        self._obj.timeout.connect(self.mainloop)
        self._obj.start()

    def mainloop(self):
        self.service_directory_file.data_changed()
        if self.service_directory_file.data_is_changed:
            self.manager.paste_to_clipboard()


class TrayIcon(QSystemTrayIcon):
    def __init__(self, manager: ClipboardToCloudManager, title=None, cloud=None):
        super().__init__()
        self.widget = QWidget()
        self.manager = manager
        self.title = title or TITLE
        self.cloud = cloud or CLOUD
        self.platform = sys.platform
        self._icons = self.manager.clipboard._icons
        self._create_trayicon()

    def _create_trayicon(self):
        """Création et configuration de l'icône de la barre d'état système (system tray icon)."""
        self.setIcon(self._icons["Clipboard"])
        self.setVisible(True)
        self.setToolTip(self.title)

        if self.platform == "win32":
            self.activated.connect(self._tray_reason)

        menu = QMenu()
        opt_copy = QAction(
            parent=self,
            text=f"Transféré sur {self.cloud}",
            icon=self._icons[self.cloud],
        )
        opt_copy.triggered.connect(self.manager.copy_to_cloud)
        menu.addAction(opt_copy)
        opt_paste = QAction(
            parent=self,
            text="Coller dans le Presse-papier",
            icon=self._icons["Clipboard"],
        )
        opt_paste.triggered.connect(self.manager.paste_to_clipboard)
        menu.addAction(opt_paste)
        show_clipboard = QAction(
            parent=self,
            text="Apperçu du presse-papier",
            icon=self._icons["Loupe"],
        )
        show_clipboard.triggered.connect(self.manager.show_clipboard)
        menu.addAction(show_clipboard)
        menu.addSeparator()
        quit_app = QAction(parent=self, text="Quitter")
        quit_app.triggered.connect(app.exit)
        menu.addAction(quit_app)
        self.setContextMenu(menu)

    def _tray_reason(self, reason: int):
        """Affichage du menu (Windows) avec le clic gauche."""
        if reason == self.Trigger:  # type: ignore
            self.contextMenu().popup(QCursor.pos())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = ClipboardToCloudManager()
    sys.exit(app.exec_())
