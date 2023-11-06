
import os
import sys
import threading
import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDateTime, QTimer, QSize, Qt, QPoint
from PyQt5.QtWidgets import QWidget, QListWidget, QStackedWidget, QLabel, QAbstractItemView, QListWidgetItem, \
    QDesktopWidget, QApplication, QMainWindow, QPushButton, QHBoxLayout, QSizePolicy, QLayout

from InterfaceTabs.InterfaceTab import LeftInterfaceTab
from DialogueWindow.ChatWindow import ChatWindow

# from MonitoringInterface.MonitoringInterface import ManageCamData, MonitoringInterface
# from MonitoringInterface.NodeDataPage import NodeDataPage


dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, dir_path)


class MainWindow(QMainWindow):
    def __init__(self,parent=None,Width = 1680,Height = 1050):
        super(MainWindow, self).__init__(parent)
        # 创建类内变量
        self.Width = Width
        self.Height = Height
        self.resize(self.Width, self.Height)

        self.setMinimumSize(QSize(1024,768))
        # self.setMaximumSize(QSize(2560,1600))
        # self.showMaximized()

        self.MainWidget = QWidget()
        self.setCentralWidget(self.MainWidget)
        self.MainWidget.resize(self.Width,self.Height)
        self.MainWidget.setStyleSheet("background-color: rgba(188,249,122,0.4) ;")

        self.HorizontalLayout = QtWidgets.QHBoxLayout()
        self.HorizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.HorizontalLayout.setSpacing(0)

        self.LeftInterfaceTab = LeftInterfaceTab(self.MainWidget)
        self.LeftInterfaceTab.retract_right_part_signal.connect(self.retractShowWindow)
        self.LeftInterfaceTab.setStyleSheet("background-color: rgba(0,0,255,1) ;")
        self.HorizontalLayout.addWidget(self.LeftInterfaceTab)

        self.RightChatWindow = ChatWindow(self.MainWidget)
        self.RightChatWindow.setMinimumWidth(500)
        self.RightChatWindow.setStyleSheet("background-color: lightblue ;")
        self.HorizontalLayout.addWidget(self.RightChatWindow)

        self.HorizontalLayout.setStretch(0, 7)
        self.HorizontalLayout.setStretch(1, 3)
        self.MainWidget.setLayout(self.HorizontalLayout)

    def retractShowWindow(self,signal):
        print(signal)
        if signal:
            self.HorizontalLayout.setStretch(0, 1)
            self.HorizontalLayout.setStretch(1, 9)
        else:
            # self.RightChatWindow.resize(self.RightChatWindow.size())
            self.HorizontalLayout.setStretch(0, 7)
            self.HorizontalLayout.setStretch(1, 3)

    # def mousePressEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         if event.y() < self.menuWidget().height():
    #             self.draggable = True
    #             self.oldPos = event.globalPos()
    #         else:
    #             self.draggable = False
    #             self.oldPos = event.globalPos()
    #
    # def mouseMoveEvent(self, event):
    #     if hasattr(self, 'draggable') and self.draggable:
    #         delta = event.globalPos() - self.oldPos
    #         self.move(self.x() + delta.x(), self.y() + delta.y())
    #         self.oldPos = event.globalPos()
    #
    # def mouseReleaseEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self.draggable = False
    #
    # def resizeEvent(self, event):
    #     super().resizeEvent(event)
        # 此处可以添加适应调整大小的代码

if __name__ == "__main__":
    app = QApplication([])
    desktop = QApplication.desktop()
    # print("屏幕宽:" + str(desktop.width()))
    # print("屏幕高:" + str(desktop.height()))
    window = MainWindow()
    # window.showFullScreen()
    window.show()
    sys.exit(app.exec_())

