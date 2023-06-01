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
VERSION = "1.9.04"
CLOUD = "Dropbox"
# Pour utiliser Google Drive :
# CLOUD = "Mon Drive"
HOME = os.path.expanduser("~")
PATH_CLOUD = f"{HOME}{os.sep}{CLOUD}{os.sep}.ClipboardToCloud{os.sep}"
PATH_FILE = PATH_CLOUD + "clipboard.data"
TITLE = f"Clipboard To {CLOUD} {VERSION}"


class DirectoryError(Exception):
    """Levée d'exception lorsque la création du répertoire sur le cloud échoue."""

    def __init__(self, message):
        """Contructeur
        Args:
            message (str): Affiche le message d'erreur associé à l'exception.
        """
        self.message = message


class MessageManager:
    def __init__(self, tray):
        self._service_directory_file = ServiceDirectoryAndFile()
        self.tray = tray

    def copy_to_cloud(self) -> None:
        """Appel de la méthode copy_to_cloud() de l'objet clipboard de la classe Clipboard."""
        message, type_message = self.tray.clipboard.copy_to_cloud(
            service=self._service_directory_file
        )
        self.show_message(message=message, icon=type_message)

    def paste_to_clipboard(self) -> None:
        """Appel de la méthode paste_to_clipboard() de l'objet clipboard de la classe Clipboard."""
        # if self._service_directory_file.data_is_changed:
        message, type_message = self.tray.clipboard.paste_to_clipboard()
        self.show_message(message=message, icon=type_message)

    def show_clipboard(self):
        """Appel de la méthode show_clipboard() de l'objet clipboard de la classe Clipboard."r"""
        message, type_message = self.tray.clipboard.show_clipboard()
        if message:
            self.show_message(message=message, icon=type_message)

    def show_message(self, message: str, icon: QIcon, duration: int = 3000):
        """Affichage de la notification avec une durée de 3 secondes par défaut."""
        self.tray.obj.showMessage(TITLE, message, icon, duration)


class ServiceDirectoryAndFile:
    """Gestionnaire du répertoire sur le cloud et le fichier binaire."""

    def __init__(self, path_cloud=None, path_file=None, title=None):
        """Constructeur
        Args:
            path_cloud (str, optional): Chemin du répertoire sur le cloud. Defaults to None.
            path_file (str, optional): Chemin du fichier binaire sur le cloud. Defaults to None.
            title (str, optional): Titre de l'application. Defaults to None.
        """
        self.path_cloud: str = path_cloud or PATH_CLOUD
        self.path_file: str = path_file or PATH_FILE
        self.title: str = title or TITLE

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
            except (FileNotFoundError, PermissionError):
                raise DirectoryError(
                    message=f"Impossible de créer le répertoire {self.path_cloud}"
                )

    @staticmethod
    def resource_path(relative_path: str) -> str:
        """Utilisation du chemin absolu pour PyInstaller (option -ONEFILE)."""
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)  # type: ignore
        return relative_path


class TrayIcon:
    def __init__(self, app, title=None, cloud=None):
        self.app = app
        self.obj = QSystemTrayIcon()  # objet représentant TrayIcon
        self.widget = QWidget()
        self.clipboard = Clipboard(app=app)
        self._icons = self.clipboard._icons
        self.title = title or TITLE
        self.cloud = cloud or CLOUD
        self.platform = sys.platform
        self.message = MessageManager(self)
        self.create_trayicon()

    def create_trayicon(self):
        """Création et configuration de l'icône de la barre d'état système (system tray icon)."""
        self.obj.setIcon(self._icons["Clipboard"])
        self.obj.setVisible(True)
        self.obj.setToolTip(self.title)

        if self.platform == "win32":
            self.obj.activated.connect(self.tray_reason)

        menu = QMenu(self.widget)

        opt_copy = QAction(
            parent=self.widget,
            text=f"Transféré sur {self.cloud}",
            icon=self._icons[self.cloud],
        )
        opt_copy.triggered.connect(self.message.copy_to_cloud)

        menu.addAction(opt_copy)

        opt_paste = QAction(
            parent=self.widget,
            text="Coller dans le Presse-papier",
            icon=self._icons["Clipboard"],
        )
        opt_paste.triggered.connect(self.message.paste_to_clipboard)

        menu.addAction(opt_paste)

        show_clipboard = QAction(
            parent=self.widget,
            text="Apperçu du presse-papier",
            icon=self._icons["Loupe"],
        )
        show_clipboard.triggered.connect(self.message.show_clipboard)

        menu.addAction(show_clipboard)
        menu.addSeparator()

        quit_app = QAction(parent=self.widget, text="Quitter")
        quit_app.triggered.connect(self.app.quit)

        menu.addAction(quit_app)

        self.obj.setContextMenu(menu)

    def tray_reason(self, reason: int):
        """Affichage du menu (Windows) avec le clic gauche."""
        if reason == self.obj.Trigger:  # type: ignore
            self.obj.contextMenu().popup(QCursor.pos())


class ToolTip(QLabel):
    """Affichage d'un QLabel d'apparence QToolTip."""

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
        avec une durée de 2.5 secondes."""
        super().show()
        self.move(
            int(self.center.x() - self.width() / 2),
            int(self.center.y() - self.height() / 2),
        )
        QTimer.singleShot(2500, self.hide)


class Clipboard:
    """Gestionnaire des opérations de copier/coller du presse-papier."""

    def __init__(self, app, path_file=None, cloud=None):
        """Contructeur
        Args:
            app (object): Instance de l'application.
            path_file (str, optional): Chemin du fichier binaire. Defaults to None.
            cloud (str, optional): Nom du service cloud. Defaults to None.
        """
        self.app = app
        self.clipboard = app.clipboard()
        self.path_file = path_file or PATH_FILE
        self.cloud = cloud or CLOUD

        self._tool_tip = ToolTip(app=app)

        self._icons = self._set_icons()

    def _set_icons(self):
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

    def copy_to_cloud(self, service: ServiceDirectoryAndFile) -> None:
        """Copie le contenu du presse-papier vers le fichier binaire sur le cloud."""
        message = "Le Presse-papier est vide !!!."
        type_message = QSystemTrayIcon.Warning
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
            service.old_data = os.stat(self.path_file).st_mtime
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

    def show_clipboard(self) -> None:
        """Affiche le contenu actuel du presse-papier."""
        message = "Le Presse-papier est vide !!!."
        type_message = QSystemTrayIcon.Warning
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


class Timer:
    def __init__(self):
        self.obj = QTimer()
        self._service_directory_file = ServiceDirectoryAndFile()
        self._initialize_timer()

    def _initialize_timer(self, interval=1000):
        self.obj.setInterval(interval)
        self.obj.timeout.connect(self._service_directory_file.data_changed)
        self.obj.start()


class ClipboardToCloudManager:
    """Gestionnaire de l'application et des interactions avec l'utilisateur."""

    def __init__(self, app=None):
        """Constructeur
        Args:
            app (object, optional): Instance de l'application. Defaults to None.
        """
        self._service_directory_file = ServiceDirectoryAndFile()
        self._exec(app=app or QApplication(sys.argv))

    def _exec(self, app=None):
        """Méthode interne qui exécute les étapes d'initialisation."""
        self.app = app or QApplication(sys.argv)
        self.tray = TrayIcon(app=app)
        self.message = MessageManager(self.tray)
        # self.timer = Timer(app=app)

    def directory_exist_and_create_file_with_title(self) -> None:
        """Vérifie l'existence du répertoire sur le cloud et création du fichier binaire."""
        try:
            self._service_directory_file.directory_exist_and_create_file_with_title()
        except DirectoryError as err:
            QMessageBox.warning(
                self.tray.widget, self._service_directory_file.title, err.message
            )
            sys.exit()

    def run(self):
        """Appel la méthode exec_() de l'objet app."""
        sys.exit(manager.app.exec_())


if __name__ == "__main__":
    manager = ClipboardToCloudManager()
    manager.directory_exist_and_create_file_with_title()
    Timer()
    manager.run()
