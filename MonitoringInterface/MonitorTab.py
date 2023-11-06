# -*- coding: utf-8 -*-
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import cv2
import requests
from PyQt5.QtCore import QRect, Qt, QTimer
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Camera import Camera
from ManageCamData import ManageCamData

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, dir_path)
ERROR1_path = os.path.join(os.path.join(os.path.abspath(os.path.dirname(dir_path) + os.path.sep + "."), 'img'),
                    '../img/ERROR1.jpg')
ERROR2_path = os.path.join(os.path.join(os.path.abspath(os.path.dirname(dir_path) + os.path.sep + "."), 'img'),
                    '../img/ERROR2.jpg')
ERROR3_path = os.path.join(os.path.join(os.path.abspath(os.path.dirname(dir_path) + os.path.sep + "."), 'img'),
                    '../img/ERROR3.jpg')
ERROR1_img = cv2.imread(ERROR1_path, cv2.IMREAD_UNCHANGED)
ERROR2_img = cv2.imread(ERROR2_path, cv2.IMREAD_UNCHANGED)
ERROR3_img = cv2.imread(ERROR3_path, cv2.IMREAD_UNCHANGED)

class MonitorTab(QTabWidget):
    def __init__(self, CamData, parent=None, Width=1200, Height=800):
        super(MonitorTab, self).__init__(parent)
        self.CamData = CamData
        self.CamDataList = CamData.CamDataList
        self.times = 0
        self.Width = Width
        self.Height = Height
        self.imgsize = (self.Width, self.Height)
        self.tabIndex = 0
        self.ToolType = None
        self.MsgBox = WarningBox(self)
        self.AlarmBoxFlage = False
        self.AlarmText = " "
        # 创建一个包含5条线程的线程池
        self.pool = ThreadPoolExecutor(max_workers=5)
        self.ThreadFlag = True
        self.UrlCheckData = []
        self.CamUrlList, self.TabNameList = self.LoadCameraData()
        self.DetectionArea = [0, 0, 0, 0, False, False]  # X0 Y0 X1 Y1 flag move
        Flage, CamOtherData, self.ServoPos = self.CamData.ReadCamOtherData(0)
        if Flage is True:
            for i in range(4):
                self.DetectionArea[i] = CamOtherData[i]
        else:
            self.ServoPos = [0, 0]
        print(CamOtherData, self.DetectionArea, self.ServoPos)
        # self.TabNameList = ['0', '1']  # 添加摄像头信息导入接口
        self.LabList = list()  # 视频界面列表
        self.CamList = list()  # 摄像头列表
        # self.setServoPos(0,90,-641)
        # self.resize(self.Width, self.Height)
        self.WidgetResize(self.Width, self.Height)
        qss_path = os.path.join(os.path.join(os.path.abspath(os.path.dirname(dir_path) + os.path.sep + "."), 'qss'),
                                'MonitorTab.qss')
        print(qss_path)
        with open(qss_path, 'r', encoding='utf-8') as f:
            Widget_Style = f.read()
        self.setStyleSheet(Widget_Style)
        self.usesScrollButtons()  # 启用滚动条
        self.tabBarClicked.connect(self.tabBarClick)
        self.Len = len(self.TabNameList)
        if self.Len != 0:
            for i in range(self.Len):
                self.LabList.append(QLabel(self))
                self.addTab(self.LabList[i], self.TabNameList[i])
            self.CamInIt()
            self.startTimer(6000)
        else:
            Lab = QLabel()
            self.addTab(Lab, '无摄像头')
            show = cv2.resize(ERROR3_img, self.imgsize)
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
            img = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
            Lab.setPixmap(QPixmap.fromImage(img))


    def WidgetResize(self, Width, Height):
        self.resize(Width, Height)
        print('MonitorTab', self.size())
        for Lab in self.LabList:
            Lab.resize(Width, Height - self.tabBar().height())
            print('Lab', Lab, Lab.size().width(), Lab.size().height(), self.tabBar().height())
        self.imgsize = (Width, Height - self.tabBar().height())

    def LoadCameraData(self):
        CamUrlList = list()
        TabNameList = list()
        for i in range(len(self.CamDataList)):
            CamUrlList.append(self.CamDataList[i][-3])
            if self.CamDataList[i][-2] is None:
                TabNameList.append(self.CamDataList[i][1])
            else:
                TabNameList.append(self.CamDataList[i][-2])
        return CamUrlList, TabNameList

    def CamInIt(self):
        # 向线程池提交视频流处理任务
        for i in range(self.Len):
            print(self.CamUrlList[i])
            Flag = CheckURl(self.CamUrlList[i])
            if Flag is True:
                self.UrlCheckData.append(True)
                self.CamList.append(Camera(str(self.CamUrlList[i])))
            else:
                self.UrlCheckData.append(False)
                self.CamList.append(None)
                # self.pool.submit(self.DriverDetection, self.CamList[i], self.LabList[i], self.UrlCheckData[i])
        print(self.CamList)
        for i in range(len(self.CamList)):
            if self.CamList[i] is not None:
                self.CamList[i].start()
                print(self.CamList[i], " start")
            self.pool.submit(self.DriverDetection, self.CamList[i], self.LabList[i], self.UrlCheckData[i])


    def tabBarClick(self, tabIndex):
        self.ToolType = self.CamDataList[tabIndex][1]
        self.tabIndex = tabIndex
        Flage, CamOtherData, ServoPos = self.CamData.ReadCamOtherData(tabIndex)
        if Flage is True:
            for i in range(4):
                self.DetectionArea[i] = CamOtherData[i]
        else:
            for i in range(4):
                self.DetectionArea[i] = 0
        self.DetectionArea[4] = False
        self.DetectionArea[5] = False
        print(tabIndex, self.ToolType, self.DetectionArea)

    def timerEvent(self, event):
        self.Alarm()
        self.times += 1
        if self.times == 50:
            for i in range(self.Len):
                Flag = CheckURl(self.CamUrlList[i])
                if Flag is True:
                    if Flag != self.UrlCheckData[i]:
                        del self.UrlCheckData[i]
                        self.UrlCheckData.insert(i, True)
                        del self.CamList[i]
                        self.CamList.insert(i, Camera(str(self.CamUrlList[i])))
                        self.CamList[i].start()

                else:
                    del self.UrlCheckData[i]
                    self.UrlCheckData.insert(i, False)
                    self.CamList[i].stop()
                    del self.CamList[i]
                    self.CamList.insert(i, None)
                time.sleep(0.05)

    def closeEvent(self, event):
        self.ThreadFlag = False
        for Cam in self.CamList:
            if Cam is not None:
                Cam.stop()
        if self.pool is not None:
            self.pool.shutdown()

    def SetDetectionArea(self):
        self.DetectionArea[-2] = True
        self.setCursor(Qt.CrossCursor)

    def DriverDetection(self, Cam, Lab, UrlCheckData):
        while self.ThreadFlag:
            if self.DetectionArea[-2] is False:
                if UrlCheckData is True:
                    Cam.setDetectionArea(self.DetectionArea)
                    img, IntrusionFlage, FireAlarmFlage = Cam.get_img()
                    img = cv2.resize(img, (self.Width, self.Height))
                    img = cv2.rectangle(img, (int(self.DetectionArea[0]), int(self.DetectionArea[1])),
                                        (int(self.DetectionArea[2]), int(self.DetectionArea[3])), (255, 191, 0), 2)
                    if Cam.AlarmFlage is True and self.AlarmBoxFlage is False:
                        self.AlarmBoxFlage = True
                        if IntrusionFlage is True and FireAlarmFlage is True:
                            print('检测到入侵和火焰')
                            self.AlarmText = '检测到入侵和火焰!!!'
                        elif IntrusionFlage is True:
                            print('检测到入侵')
                            self.AlarmText = '检测到入侵!!!'
                        elif FireAlarmFlage is True:
                            print('检测到火焰')
                            self.AlarmText = '检测到火焰!!!'
                        Cam.AlarmFlageInit()
                else:
                    img = cv2.resize(ERROR2_img, self.imgsize)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
                Lab.setPixmap(QPixmap.fromImage(img))
                time.sleep(0.04)


    def setServoPos(self, index, LEV_POS, VER_POS):
        # http: // 192.168.3.234 / control?var = level & val = 45
        LEV_POS = 0 if LEV_POS < 0 else LEV_POS
        LEV_POS = 180 if LEV_POS > 180 else LEV_POS
        VER_POS = 0 if VER_POS < 0 else VER_POS
        VER_POS = 180 if VER_POS > 180 else VER_POS
        LEVUrl = 'http://{0}/control?var=level&val={1}'.format(self.CamDataList[index][2], LEV_POS)
        VERUrl = 'http://{0}/control?var=vertical&val={1}'.format(self.CamDataList[index][2], VER_POS)
        self.ServoPos[0] = LEV_POS
        self.ServoPos[1] = VER_POS
        CamOtherData = self.DetectionArea
        CamOtherData[-2] = self.ServoPos[0]
        CamOtherData[-1] = self.ServoPos[1]
        self.CamData.WriteCamOtherData(CamOtherData, self.tabIndex)
        requests.get(LEVUrl)
        requests.get(VERUrl)
        print(LEVUrl)
        print(VERUrl)

    def Alarm(self):
        self.MsgBox.setAlarmText(self.AlarmText)
        if self.AlarmBoxFlage is True:
            print('警报开')
            self.MsgBox.show()
            self.MsgBox.finished.connect(self.setAlarmBoxFlage2False)

    def setAlarmBoxFlage2False(self):
        self.AlarmBoxFlage = False

    # 单击鼠标触发事件
    def mousePressEvent(self, event):
        if self.DetectionArea[-2] is True:
            self.DetectionArea[0] = event.pos().x()
            self.DetectionArea[1] = event.pos().y() - self.tabBar().height()

    # 鼠标移动事件
    def mouseMoveEvent(self, event):
        self.DetectionArea[-1] = True
        if self.DetectionArea[-2]:
            self.DetectionArea[2] = event.pos().x()
            self.DetectionArea[3] = event.pos().y() - self.tabBar().height()
            self.update()

    # 鼠标释放事件
    def mouseReleaseEvent(self, event):
        if self.DetectionArea[-2] is True:
            self.DetectionArea[-1] = False
            self.DetectionArea[-2] = False
            CamOtherData = self.DetectionArea[:-2]
            print('self.DetectionArea1', self.DetectionArea)
            print('self.ServoPos', self.ServoPos)
            CamOtherData.append(self.ServoPos[0])
            CamOtherData.append(self.ServoPos[1])
            print('CamOtherData', CamOtherData)
            self.setCursor(Qt.ArrowCursor)
            self.CamData.WriteCamOtherData(CamOtherData, self.tabIndex)


def CheckURl(URL):
    if 'rtsp' in URL:
        IP = URL[26:-12]
    elif 'http' in URL:
        IP = URL[7:-10]
    return_news = os.system('ping -n 1 -w 1 %s' % IP)
    if return_news == 1:
        return False
    else:
        return True


class WarningBox(QDialog):
    def __init__(self,parent=None):
        super(WarningBox, self).__init__(parent)
        self.resize(300, 200)
        self.setWindowTitle('警报')
        self.text = QLabel(self)
        self.text.resize(300, 30)
        self.text.move(50,50)
        self.text.setStyleSheet('color:red;font-size:22px;')
        self.Button = QPushButton('ok', self)
        self.Button.resize(100,30)
        self.Button.move(150-50,150 - 15)
        self.Button.clicked.connect(self.close)
        # self.text.setText("self.AlarmText")
        self.setWindowModality(Qt.ApplicationModal)
        # self.show()

    def setAlarmText(self,AlarmText):
        self.text.setText(AlarmText)


if __name__ == '__main__':
    OutCamData = ManageCamData("OutdoorCamData")
    app = QApplication(sys.argv)
    demo = MonitorTab(OutCamData)
    print(demo.CamDataList)
    demo.show()
    sys.exit(app.exec_())
# 没有可用摄像头时，界面不启动
