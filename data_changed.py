from service_directory_file import ServiceDirectoryAndFile
from PyQt5.QtCore import QTimer


class TimerDataChanged:
    def __init__(self, manager, service: ServiceDirectoryAndFile):
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
