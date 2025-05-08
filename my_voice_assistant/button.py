import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt

class TestWindow(QMainWindow):
    """创建一个测试窗口，用于验证桌面宠物的穿透功能"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("透明穿透测试")
        self.setGeometry(300, 300, 400, 300)
        
        # 创建中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 添加说明标签
        label = QLabel("如果您能点击下面的按钮，说明穿透功能正常工作")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # 添加测试按钮
        self.test_button = QPushButton("点击我测试穿透")
        self.test_button.clicked.connect(self.on_button_clicked)
        layout.addWidget(self.test_button)
        
        # 添加计数器标签
        self.counter_label = QLabel("点击次数: 0")
        self.counter_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.counter_label)
        
        self.click_count = 0
    
    def on_button_clicked(self):
        """按钮点击事件处理"""
        self.click_count += 1
        self.counter_label.setText(f"点击次数: {self.click_count}")
        print(f"按钮被点击，当前计数: {self.click_count}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())