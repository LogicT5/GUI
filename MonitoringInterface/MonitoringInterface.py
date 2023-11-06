import os
import sys
import time

from PyQt5.QtCore import QRect
from PyQt5.QtGui import QIcon

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, dir_path)

from CamDataWindow import *
from MonitorTab import *
from ManageCamData import *

class MonitoringInterface(QWidget):
    def __init__(self, CamData, parent=None, Width=1200, Height=800):
        super(MonitoringInterface, self).__init__(parent)
        self.CamData = CamData
        self.CamDataList = CamData.CamDataList
        self.ToolButtonNum = 0
        self.ButtonList = list()
        self.DetectionArea = [0,0,0,0,False,False] # X0 Y0 X1 Y1 flag move
        self.Width = Width
        self.Height = Height
        self.MonitorTab = MonitorTab(self.CamData, self, self.Width - 100, self.Height)
        qss_path = os.path.join(os.path.join(os.path.abspath(os.path.dirname(dir_path) + os.path.sep + "."), 'qss'),
                                'MonitoringInterface.qss')
        with open(qss_path, 'r', encoding='utf-8') as f:
            Widget_Style = f.read()
        self.setStyleSheet(Widget_Style)

        Icon_path = os.path.join(os.path.join(os.path.abspath(os.path.dirname(dir_path) + os.path.sep + "."), 'img'),
                                 '../img/addCam.png')
        action0 = QAction(QIcon(Icon_path), "添加摄像头", self)
        self.ButtonList.append(self.newToolButton(action0))
        self.ButtonList[-1].clicked.connect(self.addCam)

        Icon_path = os.path.join(os.path.join(os.path.abspath(os.path.dirname(dir_path) + os.path.sep + "."), 'img'),
                                 '../img/ManageCam.png')
        action1 = QAction(QIcon(Icon_path), "编辑摄像头", self)
        self.ButtonList.append(self.newToolButton(action1))
        self.ButtonList[-1].clicked.connect(self.ManageCam)

        Icon_path = os.path.join(os.path.join(os.path.abspath(os.path.dirname(dir_path) + os.path.sep + "."), 'img'),
                                 '../img/SetDetectionArea.png')
        action2 = QAction(QIcon(Icon_path), "设置检测区域", self)
        self.ButtonList.append(self.newToolButton(action2))
        self.ButtonList[-1].clicked.connect(self.SetDetectionArea)

        self.WidgetResize(self.Width, self.Height)

    def WidgetResize(self, Width, Height):
        print('MonitoringInterface',Width, Height)
        self.Width = Width
        self.Height = Height
        self.resize(Width, Height)
        self.MonitorTab.WidgetResize(Width - 100, Height)
        for i in range(len(self.ButtonList)):
            self.moveToolButton(self.ButtonList[i], i)

    def newToolButton(self, action):
        ToolButton = QToolButton(self)
        ToolButton.resize(100, 100)
        ToolButton.setDefaultAction(action)
        ToolButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.ToolButtonNum += 1
        ToolButton.move(self.ToolButtonNum * 100, 0)
        return ToolButton

    def addButton(self, ToolButton):
        self.ButtonList.append(ToolButton)
        for i in range(len(self.ButtonList)):
            self.moveToolButton(self.ButtonList[i], i)

    def moveToolButton(self, ToolButton, Num):
        ToolButton.move(self.geometry().width() - 100, Num * 100)

    def addCam(self):
        self.addCam = addCam(self.CamData)
        self.addCam.finished.connect(self.RefreshMonitorTab)

    def ManageCam(self):
        self.ManageCam = ManageCam(self.CamData)
        self.ManageCam.finished.connect(self.RefreshMonitorTab)

    def SetDetectionArea(self):
        self.MonitorTab.SetDetectionArea()

    def RefreshMonitorTab(self):
        W = self.MonitorTab.size().width()
        H = self.MonitorTab.size().height()
        self.MonitorTab.close()
        self.MonitorTab = MonitorTab(self.CamData, self, self.Width - 100, self.Height)
        self.MonitorTab.WidgetResize(W, H)
        self.MonitorTab.show()
        self.show()

if __name__ == '__main__':
    OutCamData = ManageCamData("OutdoorCamData")
    app = QApplication(sys.argv)
    demo = MonitoringInterface(OutCamData,None,1200,800)
    demo.show()
    sys.exit(app.exec_())
