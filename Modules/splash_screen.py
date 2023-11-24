import time
from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from Modules.service_directory_file import ServiceDirectoryAndFile


class SplashScreen(QSplashScreen):
    def __init__(self, title: str) -> None:
        super().__init__()
        self.setFont(QFont("Times", 30))
        self.pixmap = QPixmap(
            ServiceDirectoryAndFile.resource_path("Assets/Clipboard.png")
        )
        self.setPixmap(self.pixmap)
        self.show()
        self.showMessage(title, Qt.AlignCenter | Qt.AlignBottom, Qt.white)  # type: ignore
        time.sleep(1)
