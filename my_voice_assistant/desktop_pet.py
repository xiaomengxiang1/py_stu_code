
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
        
        # 不再安装事件过滤器，我们将使用专门的方法处理事件
        # self.installEventFilter(parent)

class Bridge(QObject):
    def __init__(self, view):
        super().__init__()
        self._view = view

    @pyqtSlot(bool)
    def setMouseTransparent(self, transparent):
        """设置鼠标穿透状态"""
        print(f"设置鼠标穿透: {transparent}")
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
        
        # 尝试两种加载方式，取决于你的文件组织方式
        try:
            # 方式1: 使用本地文件直接加载
            current_dir = os.path.dirname(os.path.abspath(__file__))
            frontend_path = os.path.join(current_dir, "frontend", "index.html")
            if os.path.exists(frontend_path):
                self.view.load(QUrl.fromLocalFile(frontend_path))
                print(f"从本地文件加载: {frontend_path}")
            else:
                # 方式2: 使用HTTP服务器
                self.view.load(QUrl("http://localhost:8000/index.html"))
                print("从HTTP服务器加载")
        except Exception as e:
            print(f"加载页面失败: {e}")
            
        self.setCentralWidget(self.view)

        # 设置窗口为全屏
        screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        self.setGeometry(geometry)

        # 初始状态不启用鼠标穿透，以便可以与模型互动
        self.view.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        # WebChannel 通信桥接
        channel = QWebChannel(self.view.page())
        self.bridge = Bridge(self.view)
        channel.registerObject('bridge', self.bridge)
        self.view.page().setWebChannel(channel)
        
        # 调试输出
        self.view.loadFinished.connect(self.onLoadFinished)

    def onLoadFinished(self, success):
        if success:
            print("页面加载成功!")
        else:
            print("页面加载失败!")

    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        # 仅当点击在窗口边缘时用于拖动整个窗口
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if hasattr(self, '_drag_pos') and self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self._drag_pos = None
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec_())


