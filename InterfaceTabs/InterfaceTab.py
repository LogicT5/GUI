import os
import sys
import threading
import time

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QDateTime, QTimer, QSize, Qt
from PyQt5.QtWidgets import QWidget, QListWidget, QStackedWidget, QLabel, QAbstractItemView, QListWidgetItem, \
    QDesktopWidget, QVBoxLayout, QSizePolicy, QAbstractScrollArea

# 每个py中确定自己的路径，防止嵌套时路径错误
dir_path = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, dir_path)


class LeftInterfaceTab(QWidget):
    retract_right_part_signal = QtCore.pyqtSignal(bool)
    def __init__(self, parent=None):
        super(LeftInterfaceTab,self).__init__(parent)
        self.time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")

        self.HorizontalLayout = QtWidgets.QHBoxLayout()
        self.HorizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.HorizontalLayout.setSpacing(0)
        # 分割左右窗口
        self.Left_Widget = QWidget(self)
        # print(self.size().width())
        self.Left_Widget.setMaximumWidth(300)
        self.Left_Widget.setMinimumWidth(300)
        self.Left_Widget.setStyleSheet("background-color: rgba(217,136,255,1) ;")
        self.Right_Widget = QStackedWidget(self)
        self.HorizontalLayout.addWidget(self.Left_Widget)
        self.HorizontalLayout.addWidget(self.Right_Widget)
        #
        # # 创建右边部件
        self.stack1 = QWidget(self.Right_Widget)
        self.stack1.setStyleSheet("background-color: rgba(248,231,28,1) ;")
        self.stack2 = QWidget(self.Right_Widget)
        self.stack2.setStyleSheet("background-color: rgba(208,2,27,1) ;")
        self.stack3 = QWidget(self.Right_Widget)
        self.stack3.setStyleSheet("background-color: rgba(144,19,254,1) ;")
        self.stack4 = QWidget(self.Right_Widget)
        self.stack4.setStyleSheet("background-color: rgba(80,227,194,1) ;")
        # 初始化主窗口
        self.Widget_init()  # 初始化左右部件
        self.setMouseTracking(False)  # 设置鼠标移动跟踪是否有效
        self.HorizontalLayout.setStretch(0, 1)
        self.HorizontalLayout.setStretch(1, 3)
        self.setLayout(self.HorizontalLayout)

        # 新建一个QTimer对象
        self.timer = QTimer()
        self.timer.setInterval(1000)
        # 信号连接到槽
        self.timer.timeout.connect(self.UpdateTime)
        threading.Thread(target=self.timer.start())

    def Widget_init(self):
        qss_path = os.path.join(os.path.join(os.path.abspath(dir_path + os.path.sep + "../"), 'qss'),
                                'Left_Widget.qss')
        with open(qss_path, 'r') as f:  # 导入QListWidget的qss样式
            Widget_Style = f.read()
        # 右边部分加入界面
        self.Right_Widget.addWidget(self.stack1)
        self.Right_Widget.addWidget(self.stack2)
        self.Right_Widget.addWidget(self.stack3)
        self.Right_Widget.addWidget(self.stack4)

        # 设置左边部件
        LeftVerticalLayout = QVBoxLayout()
        LeftVerticalLayout.setContentsMargins(0, 0, 0, 0)
        LeftVerticalLayout.setSpacing(0)
        LeftVerticalLayout.addSpacing(5) # 列表上部留空
        ListWidget = QListWidget(self.Left_Widget)
        # ListWidget.setMaximumSize()
        ListWidget.setStyleSheet(Widget_Style)
        ListWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        ListWidget.currentRowChanged.connect(self.Right_Widget.setCurrentIndex)  # list和右侧窗口的index对应绑定
        ListWidget.setFrameShape(QListWidget.NoFrame)  # 去掉边框
        ListWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 隐藏滚动条
        ListWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        ListWidget.itemClicked.connect(self.on_item_clicked)
        ListWidget.itemSelectionChanged.connect(lambda: self.on_item_selection_changed(ListWidget))

        # 左侧子选项
        ListWidget.addItem(self.ListWidgetItemInIt(ListWidget,'设计测试1', ))
        ListWidget.addItem(self.ListWidgetItemInIt(ListWidget,'设计测试2', ))
        ListWidget.addItem(self.ListWidgetItemInIt(ListWidget,'设计测试3', ))
        ListWidget.addItem(self.ListWidgetItemInIt(ListWidget,'对话窗口', ))
        ListWidget.setCurrentRow(0)
        LeftVerticalLayout.addWidget(ListWidget)

        # 左边小部件添加实时时间显示
        self.TimeText = QLabel(ListWidget)
        self.TimeText.setMaximumHeight(80)
        self.TimeText.setText(self.time)
        self.TimeText.setAlignment(Qt.AlignCenter)
        self.TimeText.setStyleSheet("font-size: 28px;")
        LeftVerticalLayout.addWidget(self.TimeText)

        LeftVerticalLayout.setStretch(0,1)
        LeftVerticalLayout.setStretch(1,9)
        LeftVerticalLayout.setStretch(2,1)
        self.Left_Widget.setLayout(LeftVerticalLayout)
        # 设置左边List，size
        # self.Left_Widget.resize(self.L_Width, self.Height)
        # self.Left_Widget.move(0, 0)
        # self.Left_Widget.item0.setSizeHint(QSize(self.L_Width, self.L_Height))
        # self.Left_Widget.item1.setSizeHint(QSize(self.L_Width, self.L_Height))
        # self.Left_Widget.item2.setSizeHint(QSize(self.L_Width, self.L_Height))
        # self.Left_Widget.item3.setSizeHint(QSize(self.L_Width, self.L_Height))
        # self.TimeText.resize(self.L_Width, int(self.Height / 12))
        # self.TimeText.move(5, self.Height - int(self.TimeText.height() - 10))

    def ListWidgetItemInIt(self,ListWidget,name):
        item = QListWidgetItem(name,ListWidget)
        item.setTextAlignment(Qt.AlignCenter)
        item.setSizeHint(QSize(ListWidget.size().width(), 100))
        return item

    def UpdateTime(self):
        # 获取当前日期与时间 QDateTime.currentDateTime()
        self.time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.TimeText.setText(self.time)
        time.sleep(0.5)

    def on_item_clicked(self,item):
        pass
        # print("单击了列表项:", item.text())

    def on_item_selection_changed(self,list_widget):
        if list_widget.currentRow() == 3:
            self.retract_right_part_signal.emit(True)
        else:
            self.retract_right_part_signal.emit(False)

    def resizeEvent(self, event):
        # 当窗口大小发生改变时调用此方法
        super().resizeEvent(event)
        # print(self.size())
        self.resize(self.size())

