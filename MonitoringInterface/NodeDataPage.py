import ctypes
import inspect
import threading
import socket
import time
from ssl import SOL_SOCKET

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from math import *
import sys

from _socket import SO_REUSEADDR


class GaugePanel(QWidget):
    def __init__(self, parent=None, Width=300, Height=300):
        super().__init__(parent)
        self.setWindowTitle("GaugePanel")
        self.setMinimumWidth(Width)
        self.setMinimumHeight(Height)

        self.timer = QTimer()  # 窗口重绘定时器
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

        # self.testTimer = QTimer()
        # self.testTimer.timeout.connect(self.testTimer_timeout_handle)

        self.lcdDisplay = QLCDNumber(self)
        self.lcdDisplay.setDigitCount(4)
        self.lcdDisplay.setMode(QLCDNumber.Dec)
        self.lcdDisplay.setSegmentStyle(QLCDNumber.Flat)
        self.lcdDisplay.setStyleSheet('border:2px solid green;color:green;background:silver')

        self._startAngle = 120  # 以QPainter坐标方向为准,建议画个草图看看
        self._endAngle = 60  # 以以QPainter坐标方向为准
        self._scaleMainNum = 10  # 主刻度数
        self._scaleSubNum = 10  # 主刻度被分割份数
        self._minValue = 0
        self._maxValue = 20000
        self._title = 'X10_WH'
        self._value = 100
        self._minRadio = 100  # 缩小比例,用于计算刻度数字
        self._decimals = 0  # 小数位数

    @pyqtSlot()
    # def testTimer_timeout_handle(self):
    #     self._value = self._value + 1
    #     if self._value > self._maxValue:
    #         self._value = self._minValue

    # def setTestTimer(self, flag):
    #     if flag is True:
    #         self.testTimer.start(10)
    #     else:
    #         self.testTimer.stop()

    def setMinMaxValue(self, min, max):
        self._minValue = min
        self._maxValue = max

    def setTitle(self, title):
        self._title = title

    def setValue(self, value):
        self._value = value

    def setMinRadio(self, minRadio):
        self._minRadio = minRadio

    def setDecimals(self, decimals):
        self._decimals = decimals

    def paintEvent(self, event):
        side = min(self.width(), self.height())

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)  # painter坐标系原点移至widget中央
        painter.scale(side / 200, side / 200)  # 缩放painterwidget坐标系，使绘制的时钟位于widge中央,即钟表支持缩放

        self.drawPanel(painter)  # 画外框表盘
        self.drawScaleNum(painter)  # 画刻度数字
        self.drawScaleLine(painter)  # 画刻度线
        self.drawTitle(painter)  # 画标题备注
        self.drawValue(painter)  # 画数显
        self.drawIndicator(painter)  # 画指针

    def drawPanel(self, p):
        p.save()
        radius = 100
        lg = QLinearGradient(-radius, -radius, radius, radius)
        lg.setColorAt(0, Qt.white)
        lg.setColorAt(1, Qt.black)
        p.setBrush(lg)
        p.setPen(Qt.NoPen)
        p.drawEllipse(-radius, -radius, radius * 2, radius * 2)

        p.setBrush(Qt.black)
        p.drawEllipse(-92, -92, 92 * 2, 92 * 2)
        p.restore()

    def drawScaleNum(self, p):
        p.save()
        p.setPen(Qt.white)
        startRad = self._startAngle * (3.14 / 180)
        stepRad = (360 - (self._startAngle - self._endAngle)) * (3.14 / 180) / self._scaleMainNum

        fm = QFontMetricsF(p.font())
        for i in range(0, self._scaleMainNum + 1):
            sina = sin(startRad + i * stepRad)
            cosa = cos(startRad + i * stepRad)

            tmpVal = i * ((self._maxValue - self._minValue) / self._scaleMainNum) + self._minValue
            tmpVal = tmpVal / self._minRadio
            s = '{:.0f}'.format(tmpVal)
            w = fm.size(Qt.TextSingleLine, s).width()
            h = fm.size(Qt.TextSingleLine, s).height()
            x = 80 * cosa - w / 2
            y = 80 * sina - h / 2
            p.drawText(QRectF(x, y, w, h), s)

        p.restore()

    def drawScaleLine(self, p):
        p.save()
        p.rotate(self._startAngle)
        scaleNums = self._scaleMainNum * self._scaleSubNum
        angleStep = (360 - (self._startAngle - self._endAngle)) / scaleNums
        p.setPen(Qt.white)

        pen = QPen(Qt.white)
        for i in range(0, scaleNums + 1):
            if i >= 0.8 * scaleNums:
                pen.setColor(Qt.red)

            if i % self._scaleMainNum is 0:
                pen.setWidth(2)
                p.setPen(pen)
                p.drawLine(64, 0, 72, 0)
            else:
                pen.setWidth(1)
                p.setPen(pen)
                p.drawLine(67, 0, 72, 0)
            p.rotate(angleStep)

        p.restore()

    def drawTitle(self, p):
        p.save()
        p.setPen(Qt.white)
        fm = QFontMetrics(p.font())
        w = fm.size(Qt.TextSingleLine, self._title).width()
        p.drawText(-w / 2, -45, self._title)
        p.restore()

    def drawValue(self, p):
        side = min(self.width(), self.height())
        w, h = side / 2 * 0.4, side / 2 * 0.2
        x, y = self.width() / 2 - w / 2, self.height() / 2 + side / 2 * 0.55
        self.lcdDisplay.setGeometry(x, y, w, h)

        ss = '{:.' + str(self._decimals) + 'f}'
        self.lcdDisplay.display(ss.format(self._value))

    def drawIndicator(self, p):
        p.save()
        polygon = QPolygon([QPoint(0, -2), QPoint(0, 2), QPoint(60, 0)])
        degRotate = self._startAngle + (360 - (self._startAngle - self._endAngle)) / (
                self._maxValue - self._minValue) * (self._value - self._minValue)
        # 画指针
        p.rotate(degRotate)
        halogd = QRadialGradient(0, 0, 60, 0, 0)
        halogd.setColorAt(0, QColor(60, 60, 60))
        halogd.setColorAt(1, QColor(160, 160, 160))
        p.setPen(Qt.white)
        p.setBrush(halogd)
        p.drawConvexPolygon(polygon)
        p.restore()

        # 画中心点
        p.save()
        radGradient = QRadialGradient(0, 0, 10)
        radGradient = QConicalGradient(0, 0, -90)
        radGradient.setColorAt(0.0, Qt.darkGray)
        radGradient.setColorAt(0.5, Qt.white)
        radGradient.setColorAt(1.0, Qt.darkGray)
        p.setPen(Qt.NoPen)
        p.setBrush(radGradient)
        p.drawEllipse(-5, -5, 10, 10)
        p.restore()


class TCPServer:
    Theardflag = True
    recv_data = None
    # 1 创建服务端套接字对象
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 设置端口复用，使程序退出后端口马上释放
    tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    # 2 绑定端口
    tcp_server.bind(("", 8888))
    # 3 设置监听
    tcp_server.listen(128)
    # 4 循环等待客户端连接请求（也就是最多可以同时有128个用户连接到服务器进行通信）

    def get_recv_data(self):
        return self.recv_data

    def start_monitor(self):
        print('TCP服务器监听启动')
        while self.Theardflag:
            tcp_client_1, tcp_client_address = self.tcp_server.accept()
            self.dispose_client_request( tcp_client_1, tcp_client_address)
            time.sleep(0.05)
            # # 创建多线程对象
            # thd = threading.Thread(target=self.dispose_client_request, args=(tcp_client_1, tcp_client_address))
            # # 设置守护主线程  即如果主线程结束了 那子线程中也都销毁了  防止主线程无法退出
            # thd.setDaemon(True)
            # # 启动子线程对象
            # thd.start()

    # 定义个函数,使其专门重复处理客户的请求数据（也就是重复接受一个用户的消息并且重复回答，直到用户选择下线）
    def dispose_client_request(self, tcp_client_1, tcp_client_address):
        # 5 循环接收和发送数据
        while True:
            recv_data = tcp_client_1.recv(4096)
            # 6 有消息就回复数据，消息长度为0就是说明客户端下线了
            if recv_data:
                print("客户端是:", tcp_client_address)
                print("客户端发来的消息是:", recv_data.decode())
                self.recv_data = recv_data.decode()
                # send_data = "消息已收到，正在处理中...".encode()
                # tcp_client_1.send(send_data)
            else:
                print("%s 客户端下线了..." % tcp_client_address[1])
                tcp_client_1.close()
                break

    def stop(self):
        self.Theardflag = False


class NodeDataPage(QWidget):
    def __init__(self, parent=None, Width=1200, Height=800):
        super(NodeDataPage, self).__init__(parent)
        self.resize(Width, Height)
        self.HW_Value = 0
        self.CO_Value = 0
        self.LEL_Value = 0
        self.TCPSer = TCPServer()
        self.Thread = threading.Thread(target=self.TCPSer.start_monitor)
        self.Thread.setDaemon(True)
        self.Thread.start()
        self.Lable1 = QLabel(self)
        self.Lable1.setText('  水位高度  ')
        self.Lable1.setStyleSheet('color:black;font-size:34px;')
        self.Lable1.resize(200, 50)
        self.Lable2 = QLabel(self)
        self.Lable2.setText('  烟雾浓度  ')
        self.Lable2.setStyleSheet('color:black;font-size:34px;')
        self.Lable2.resize(200, 50)
        self.Lable3 = QLabel(self)
        self.Lable3.setText('可燃气体浓度')
        self.Lable3.setStyleSheet('color:black;font-size:34px;')
        self.Lable3.resize(200, 50)
        Pan_Width = int(((Width - 60) / 300) * 100)
        Pan_Height = Pan_Width
        self.HW_Panel = GaugePanel(self, Pan_Width, Pan_Height)
        x = Width / 2 - self.HW_Panel.size().width() - self.HW_Panel.size().width() / 2 - 20
        self.HW_Panel.move(x, 10)
        self.HW_Panel.setTitle("X1_HW")
        self.HW_Panel.setMinMaxValue(0, 100)
        self.HW_Panel.setMinRadio(1)
        self.HW_Panel.setValue(self.HW_Value)
        self.Lable1.move(self.HW_Panel.geometry().x()+(self.HW_Panel.size().width() - self.Lable1.size().width()) / 2,
                         self.HW_Panel.geometry().y() + self.HW_Panel.size().height() + 10)
        self.CO_Panel = GaugePanel(self, Pan_Width, Pan_Height)
        self.CO_Panel.move(self.HW_Panel.geometry().x() + self.HW_Panel.size().width() + 20, 10)
        self.CO_Panel.setTitle("X100_CO")
        self.CO_Panel.setMinMaxValue(0, 10000)
        self.CO_Panel.setValue(self.CO_Value)
        self.Lable2.move(self.CO_Panel.geometry().x() + (self.CO_Panel.size().width() - self.Lable2.size().width()) /2 ,
                         self.CO_Panel.geometry().y() + self.CO_Panel.size().height() + 10)
        self.LEL_Panel = GaugePanel(self, Pan_Width, Pan_Height)
        self.LEL_Panel.move(self.CO_Panel.geometry().x() + self.CO_Panel.size().width() + 20, 10)
        self.LEL_Panel.setTitle("X100_LEL")
        self.LEL_Panel.setMinMaxValue(0, 10000)
        self.LEL_Panel.setValue(self.LEL_Value)
        self.Lable3.move(self.LEL_Panel.geometry().x() + (self.LEL_Panel.size().width() - self.Lable3.size().width()) /2,
                         self.LEL_Panel.geometry().y() + self.LEL_Panel.size().height() + 10)
        self.startTimer(3000)

    def timerEvent(self, event):
        datalist = list()
        if self.TCPSer.get_recv_data() is not None:
            # print(self.TCPSer.get_recv_data().split(";"), type(self.TCPSer.get_recv_data()))
            for data in self.TCPSer.get_recv_data().split(";"):
                datalist.append(data.split(":")[-1])
            self.HW_Value = int(datalist[0])
            self.CO_Value = int(datalist[1])
            self.LEL_Value = int(datalist[2])
            # print(self.HW_Value, self.CO_Value, self.LEL_Value)
            self.HW_Panel.setValue(self.HW_Value)
            self.CO_Panel.setValue(self.CO_Value)
            self.LEL_Panel.setValue(self.LEL_Value)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    desktop = QApplication.desktop()
    # print("屏幕宽:" + str(desktop.width()))
    # print("屏幕高:" + str(desktop.height()))
    gp = NodeDataPage()
    gp.show()
    app.exec_()
