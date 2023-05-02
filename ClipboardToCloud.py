# -*- Coding: utf-8 -*-
# Created by Diablo76 on 14/02/2023 -- 07:41:27.
# ClipboardToCloud est un script qui permet de récupérer le contenu
# du presse-papier d'un ordinateur à un autre. 

import os
import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QImage, QPixmap
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
VERSION = "1.09"
CLOUD = "Dropbox"
HOME = os.path.expanduser("~")
PATH_CLOUD = f"{HOME}{os.sep}{CLOUD}{os.sep}.ClipboardToCloud{os.sep}"
PATH_FILE = PATH_CLOUD + "clipboard.data"
TITLE = f"Clipboard To {CLOUD} {VERSION}"


class ToolTip(QLabel):
    """Affichage d'un QLabel d'apparence QToolTip"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.ToolTip)  # type: ignore
        self.setStyleSheet(
            "border: 1px solid black; background-color: rgb(200,200,180)"
        )
        self.setWindowOpacity(0.8)
        self.center = app.screens()[0].availableGeometry().center()

    def show(self):
        """Affichage du tooltip au centre de l'écran
        avec une durée de 2.5 secondes"""
        super().show()
        self.move(
            int(self.center.x() - self.width() / 2),
            int(self.center.y() - self.height() / 2),
        )
        QTimer.singleShot(2500, self.hide)


class ClipboardToCloudManager(QWidget):
    """ClipboardManager"""
    def __init__(self):
        super().__init__()
        self.directory_exist()
        self.tray = QSystemTrayIcon()
        self.tool_tip = ToolTip()
        self.icons = {
            "Dropbox": QIcon(QPixmap("dropbox.png")),
            "Clipboard": QIcon(QPixmap("clipboard.png")),
            "Loupe": QIcon(QPixmap("loupe.png")),
        }
        self.clipboard = app.clipboard()
        self.create_trayicon()
        self.old_data = os.path.getsize(PATH_FILE)
        self.new_data = None
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.data_changed)
        self.timer.start()

    def directory_exist(self):
        """Controle et création du répertoire sur le Cloud"""
        if not os.path.isdir(PATH_CLOUD):
            try:
                os.mkdir(PATH_CLOUD)
                with open(PATH_FILE, "wb") as file:
                    file.write(TITLE.encode("utf-8"))
            except (FileNotFoundError, PermissionError):
                QMessageBox.warning(
                    self, TITLE, f"Impossible de créer le répertoire {PATH_CLOUD}"
                )
                sys.exit()

    def data_changed(self):
        """Contrôle de l'état du fichier"""
        self.new_data = os.path.getsize(PATH_FILE)
        if self.new_data != self.old_data:
            self.paste_to_clipboard()
            self.old_data = self.new_data

    def copy_to_cloud(self):
        """Copie du fichier binaire sur le Cloud"""
        if self.clipboard.mimeData().formats():
            if self.clipboard.mimeData().hasImage():
                pixmap = self.clipboard.pixmap()
                pixmap.save(PATH_FILE, "PNG")
                self.show_message(f"Image copiée dans {CLOUD}.", QIcon(pixmap))
            elif self.clipboard.mimeData().hasText():
                text = self.clipboard.text()
                with open(PATH_FILE, "wb") as file:
                    file.write(text.encode("utf-8"))
                self.show_message(f"Texte copié dans {CLOUD}.", self.icons["Dropbox"])
            self.old_data = os.path.getsize(PATH_FILE)
        else:
            self.show_message(
                "Le Presse-papier est vide !!!.",
                QSystemTrayIcon.Warning,  # type: ignore
            )

    def paste_to_clipboard(self):
        """Copie du fichier binaire du cloud vers le presse-papier"""
        with open(PATH_FILE, "rb") as file:
            data = file.read()
        header = data[0:4]
        if header == b"\x89PNG":
            image = QImage.fromData(data)
            self.clipboard.setImage(image)
            self.show_message(
                "Image collée dans le Presse-papier.", QIcon(QPixmap(image))
            )
        else:
            self.clipboard.setText(data.decode("utf-8"))
            self.show_message(
                "Texte collé dans le Presse-papier.", self.icons["Clipboard"]
            )

    def create_trayicon(self):
        """Création du QSystemTrayIcon"""
        self.tray.setIcon(self.icons["Clipboard"])
        self.tray.setVisible(True)
        self.tray.setToolTip(TITLE)
        menu = QMenu(self)
        opt_copy = QAction(
            parent=self, text=f"Copier dans {CLOUD}", icon=self.icons["Dropbox"]
        )
        opt_copy.triggered.connect(self.copy_to_cloud)
        menu.addAction(opt_copy)
        opt_paste = QAction(
            parent=self,
            text="Coller dans le Presse-papier",
            icon=self.icons["Clipboard"],
        )
        opt_paste.triggered.connect(self.paste_to_clipboard)
        menu.addAction(opt_paste)
        show_clipboard = QAction(
            parent=self, text="Apperçu du presse-papier", icon=self.icons["Loupe"]
        )
        show_clipboard.triggered.connect(self.show_clipboard)
        menu.addAction(show_clipboard)
        menu.addSeparator()
        quit_app = QAction(parent=self, text="Quitter")
        quit_app.triggered.connect(app.quit)
        menu.addAction(quit_app)
        self.tray.setContextMenu(menu)

    def show_clipboard(self):
        """Affichage du presse-papier"""
        if self.clipboard.mimeData().formats():
            if self.clipboard.mimeData().hasImage():
                pixmap = self.clipboard.pixmap().scaledToWidth(
                    500, Qt.SmoothTransformation  # type: ignore
                )
                self.tool_tip.setPixmap(pixmap)
            else:
                self.tool_tip.setText(self.clipboard.text())
            self.tool_tip.show()
        else:
            self.show_message(
                "Le Presse-papier est vide !!!.",
                QSystemTrayIcon.Warning,  # type: ignore
            )

    def show_message(self, message: str, icon: QIcon, duration: int = 3000):
        """Affichage de la notification avec une durée de 3 secondes par défaut"""
        self.tray.showMessage(TITLE, message, icon, duration)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = ClipboardToCloudManager()
    sys.exit(app.exec_())