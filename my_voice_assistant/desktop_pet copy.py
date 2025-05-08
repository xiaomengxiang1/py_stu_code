
# python my_voice_assistant\desktop_pet.py启动


import sys, os
from PyQt5.QtCore import Qt, QUrl, QObject, QEvent, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWebChannel import QWebChannel

class TransparentWebView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.page().setBackgroundColor(Qt.transparent)
        self.installEventFilter(parent)

class Bridge(QObject):
    def __init__(self, view):
        super().__init__()
        self._view = view

    @pyqtSlot(bool)
    def setMouseTransparent(self, transparent):
        self._view.setAttribute(Qt.WA_TransparentForMouseEvents, transparent)

class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.view = TransparentWebView(self)
        settings = self.view.settings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.view.load(QUrl("http://localhost:8000/index.html"))
        self.setCentralWidget(self.view)

        # 设置窗口为全屏
        screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        self.setGeometry(geometry)

        # 开启默认鼠标穿透
        self.view.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        # WebChannel 通信桥接
        channel = QWebChannel(self.view.page())
        self.bridge = Bridge(self.view)
        channel.registerObject('bridge', self.bridge)
        self.view.page().setWebChannel(channel)

        self._drag_pos = None

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj is self.view:
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
                return True
            elif event.type() == QEvent.MouseMove and self._drag_pos is not None:
                self.move(event.globalPos() - self._drag_pos)
                return True
            elif event.type() == QEvent.MouseButtonRelease:
                self._drag_pos = None
                return True
        return super().eventFilter(obj, event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec_())



