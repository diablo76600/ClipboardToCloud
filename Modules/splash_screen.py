import time
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from Modules.service_directory_file import ServiceDirectoryAndFile


class SplashScreen(QSplashScreen):
    def __init__(self, app: QApplication, title: str) -> None:
        self.app = app
        super().__init__()
        self.setFont(QFont("Times", 30))
        self.pixmap = QPixmap(
            ServiceDirectoryAndFile.resource_path("Assets/Clipboard.png")
        )
        self.setPixmap(self.pixmap)
        self.show()
        txt = ""
        for letter in title:
            txt += letter
            self.showMessage(txt, Qt.AlignCenter | Qt.AlignBottom, Qt.white)  # type: ignore
            time.sleep(0.01)
