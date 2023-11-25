# -*- Coding: utf-8 -*-
# Created by Diablo76 on 14/02/2023 -- 07:41:27.
""" ClipboardToCloud est un script qui permet de récupérer le contenu
    du presse-papier d'un ordinateur à un autre
    sans tenir compte de l'OS et du réseau.
    Par défaut, il fonctionne avec Dropbox mais il peut être adapté
    pour d'autre Cloud (Google Drive etc...) """


import os
import sys
from Modules.service_directory_file import ServiceDirectoryAndFile, DirectoryError
from Modules.clipboard_manager import ClipboardManager
from Modules.tray_icon import TrayIcon
from Modules.file_watcher import FileWatcher
from Modules.splash_screen import SplashScreen
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow

# Constantes globales
VERSION = "1.9.7"
CLOUD = "Dropbox"
# Pour utiliser Google Drive :
# CLOUD = "Mon Drive"
HOME = os.path.expanduser("~")
PATH_CLOUD = f"{HOME}{os.sep}{CLOUD}{os.sep}.ClipboardToCloud{os.sep}"
PATH_FILE = f"{PATH_CLOUD}clipboard.data"
TITLE = f"Clipboard To {CLOUD} {VERSION}"


class ClipboardToCloudManager(QMainWindow):
    """Gestionnaire de l'application et des interactions avec l'utilisateur."""

    def __init__(self) -> None:
        """Constructeur"""
        self.service_directory_file = ServiceDirectoryAndFile(
            path_cloud=PATH_CLOUD, manager=self, path_file=PATH_FILE, title=TITLE
        )
        self.clipboard = ClipboardManager(
            app=app,
            service=self.service_directory_file,
            path_file=PATH_FILE,
            cloud=CLOUD,
        )
        self.tray = TrayIcon(app=app, manager=self, title=TITLE, cloud=CLOUD)
        self.directory_exist_and_create_file()
        self.watcher = FileWatcher(
            path_file=PATH_FILE, manager=self, service=self.service_directory_file
        )
        super().__init__()

    def copy_to_cloud(self) -> None:
        """Appel de la méthode copy_to_cloud() de l'objet clipboard de la classe Clipboard."""
        message, type_icon = self.clipboard.copy_to_cloud()
        self.show_message(message=message, icon=type_icon)

    def paste_to_clipboard(self) -> None:
        """Appel de la méthode paste_to_clipboard() de l'objet clipboard de la classe Clipboard."""
        message, type_icon = self.clipboard.paste_to_clipboard()
        self.show_message(message=message, icon=type_icon)

    def show_clipboard(self):
        """Appel de la méthode show_clipboard() de l'objet clipboard de la classe Clipboard."""
        message, type_icon = self.clipboard.show_clipboard()
        if message:
            self.show_message(message=message, icon=type_icon)

    def show_message(self, message: str, icon: QIcon, duration: int = 3000) -> None:
        """Affichage de la notification avec une durée de 3 secondes par défaut."""
        self.tray.showMessage(TITLE, message, icon, duration)

    def directory_exist_and_create_file(self) -> None:
        """Vérifie l'existence du répertoire sur le cloud et création du fichier binaire."""
        try:
            self.service_directory_file.directory_exist_and_create_file_with_title()
        except DirectoryError as err:
            QMessageBox.warning(
                self.tray.widget_messagebox,
                self.service_directory_file.title,
                err.message,
            )
            sys.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    SplashScreen(title=TITLE)
    manager = ClipboardToCloudManager()
    sys.exit(app.exec_())
