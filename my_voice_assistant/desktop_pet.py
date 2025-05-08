
# python my_voice_assistant\desktop_pet.py启动


import sys, os
from PyQt5.QtCore import Qt, QUrl, QObject, QEvent
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings

class TransparentWebView(QWebEngineView):
    """
    自定义 QWebEngineView，使背景透明并向父窗口传递拖动事件
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # 使Web内容背景透明
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.page().setBackgroundColor(Qt.transparent)
        # 安装事件过滤器，拦截鼠标事件传给父窗口
        self.installEventFilter(parent)

class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()
        # 窗口无边框、透明且置顶
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 中央嵌入透明WebView
        self.view = TransparentWebView(self)
        settings = self.view.settings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.view.load(QUrl("http://localhost:8000/index.html"))
        self.setCentralWidget(self.view)

        # 设置窗口为全屏大小以支持模型拖动到屏幕边缘
        screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        self.setGeometry(geometry)

        # 拖动偏移
        self._drag_pos = None

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        # 捕捉子控件（WebView）的鼠标事件
        if obj is self.view and isinstance(event, QEvent):
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                # 记录起始拖动点
                self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
                return True
            elif event.type() == QEvent.MouseMove and self._drag_pos is not None:
                # 移动窗口
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


