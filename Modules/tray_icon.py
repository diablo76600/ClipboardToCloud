import sys
from PyQt5.QtWidgets import QAction, QWidget, QMenu, QSystemTrayIcon, QApplication
from PyQt5.QtGui import QCursor


class TrayIcon(QSystemTrayIcon):
    """Création du TrayIcon"""

    def __init__(self, app: QApplication, manager, title: str, cloud: str) -> None:
        """Constructeur

        Args:
            app (QApplication): Instance de l'application
            manager (ClipboardToCloudManager): Instance de ClipboardToCloudManager
            title (str): Titre de l'application
            cloud (str): Nom du cloud
        """

        super().__init__()
        self.widget_messagebox = QWidget()
        self.app = app
        self.manager = manager
        self.title = title
        self.cloud = cloud
        self.platform = sys.platform
        self._icons = self.manager.clipboard._icons
        self.messageClicked.connect(self.manager.show_clipboard)
        self._create_trayicon()

    def _create_trayicon(self) -> None:

        # Set up tray icon
        self.setIcon(self._icons["Clipboard"])
        self.setVisible(True)
        self.setToolTip(self.title)

        if self.platform == "win32":
            self.activated.connect(self._tray_reason)

        # Create menu
        menu = QMenu()
        self._add_copy_option(menu)
        self._add_paste_option(menu)
        self._add_show_clipboard_option(menu)
        menu.addSeparator()
        self._add_quit_option(menu)

        self.setContextMenu(menu)

    def _add_copy_option(self, menu):
        opt_copy = QAction(
            parent=self,
            text=f"Transférer sur {self.cloud}",
            icon=self._icons[self.cloud],
        )
        opt_copy.triggered.connect(self.manager.copy_to_cloud)
        menu.addAction(opt_copy)

    def _add_paste_option(self, menu):
        opt_paste = QAction(
            parent=self,
            text="Coller dans le Presse-papier",
            icon=self._icons["Clipboard"],
        )
        opt_paste.triggered.connect(self.manager.paste_to_clipboard)
        menu.addAction(opt_paste)

    def _add_show_clipboard_option(self, menu):
        show_clipboard = QAction(
            parent=self,
            text="Apperçu du presse-papier",
            icon=self._icons["Loupe"],
        )
        show_clipboard.triggered.connect(self.manager.show_clipboard)
        menu.addAction(show_clipboard)

    def _add_quit_option(self, menu):
        quit_app = QAction(parent=self, text="Quitter")
        quit_app.triggered.connect(self.app.exit)
        menu.addAction(quit_app)

    def _tray_reason(self, reason: int):
        """Affichage du menu (Windows) avec le clic gauche."""

        if reason == self.Trigger:  # type: ignore
            self.contextMenu().popup(QCursor.pos())
