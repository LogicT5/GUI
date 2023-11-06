import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QScrollArea, QVBoxLayout, QLabel

app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("QScrollArea 示例")
window.setGeometry(100, 100, 400, 300)

scroll_area = QScrollArea()
scroll_area.setWidgetResizable(True)  # 允许小部件自适应滚动区域

content = QWidget()
layout = QVBoxLayout(content)

for i in range(20):
    label = QLabel(f"这是标签 {i}")
    layout.addWidget(label)

scroll_area.setWidget(content)  # 设置滚动区域的内容小部件

window.setCentralWidget(scroll_area)
window.show()

app.exec_()
