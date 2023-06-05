from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QTimer


class ToolTip(QLabel):
    """Affichage d'un QLabel d'apparence QToolTip."""

    def __init__(self, app, ms: int = 2500) -> None:
        """Constructeur

        Args:
            app (object): Instance de l'application
            ms (int, optional):Délai en milliseconde. Defaults to 2500.
        """
        super().__init__()
        self.ms = ms
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
        QTimer.singleShot(self.ms, self.hide)
