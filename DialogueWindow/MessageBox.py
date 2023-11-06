from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel

from DialogueWindow.MessageBag import MessageBag,Role
from DialogueWindow.MessageBubble import MessageBubble


testMessage = ["You are an assistant helping me with the AirSim simulator for drones.",
               "When I ask you to do something, you are supposed to give me Python code that is needed to achieve that task using AirSim and then an explanation of what that code does.",
               "You are only allowed to use the functions I have defined for you.",
               "You are ",
               "You can use simple Python functions from libraries such as math and numpy.",
               "You ",
               "When I ask you to do s.",
               "You are only allowed to use the functions I have defined for you.",
               "Y",
               "You can use simple Python functions from libraries such as math and numpy. When I ask you to do something, you are supposed to give me Python code that is needed to achieve that task using AirSim and then an explanation of what that code does. When I ask you to do something, you are supposed to give me Python code that is needed to achieve that task using AirSim and then an explanation of what that code does."]

class MessageBox(QWidget):
    def __init__(self,parent=None):
        super(MessageBox,self).__init__(parent)
        self.setMinimumSize(self.size())
        # self.MessageBox.setMaximumWidth(self.size().width())

        self.ScrollArea = QScrollArea(self)
        # self.ScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ScrollArea.resize(self.size())
        # self.ScrollArea.setMinimumSize(self.ScrollArea.size())

        self.ScrollArea.setStyleSheet("""
                                QScrollArea{
                                    background-color: rgba(0,0,255,255);
                                    color: white;
                                    border: 2px solid #d0d0d0;
                                    border-radius: 10px;
                                    padding: 10px;
                                }
                            """)

        self.VerticalLayout = QVBoxLayout()
        self.VerticalLayout.setContentsMargins(5, 5, 5, 0)
        self.VerticalLayout.setSpacing(0)
        self.VerticalLayout.addWidget(self.ScrollArea)
        self.setLayout(self.VerticalLayout)

        scrollbar = self.ScrollArea.verticalScrollBar()
        scrollbar.rangeChanged.connect(self.adjustScrollToMaxValue)  # 监听窗口滚动条范围

        # self.VScrollArealayout = QVBoxLayout()
        # self.VScrollArealayout.setContentsMargins(0, 0, 0, 0)
        # self.VScrollArealayout.setSpacing(0)

        self.MessageBox = QWidget()
        # self.MessageBox.setMinimumSize(self.ScrollArea.size())
        self.MessageBox.setStyleSheet("background-color: rgba(0,255,0,255);")
        # self.MessageBox.resize(self.size())

        self.MessageBox.setMinimumWidth(self.size().width())
        self.VMessageBoxlayout = QVBoxLayout()
        self.VMessageBoxlayout.setContentsMargins(0, 0, 0, 0)
        self.VMessageBoxlayout.setSpacing(10)
        # test message bubble
        for i in range(10):
            if i%2 ==0:
                test = MessageBag(Role.User,testMessage[i])
            else:
                test = MessageBag(Role.Other,testMessage[i])
            label = MessageBubble(test,self.MessageBox)
            self.VMessageBoxlayout.addWidget(label)

        self.MessageBox.setLayout(self.VMessageBoxlayout)
        # self.VScrollArealayout.addWidget(self.MessageBox)
        # self.ScrollArea.setLayout(self.VScrollArealayout)
        self.ScrollArea.setWidget(self.MessageBox)


    def addMessgaeBubble(self,MessageBag):
        buble = MessageBubble(MessageBag)
        self.VMessageBoxlayout.addWidget(buble)

    # 窗口滚动到最底部
    def adjustScrollToMaxValue(self):
        scrollbar = self.ScrollArea.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def resizeEvent(self, event):
        # 当窗口大小发生改变时调用此方法
        super().resizeEvent(event)
        # print(self.size())
        # self.resize(self.size())
        self.MessageBox.setMinimumWidth(self.size().width() - 70)
        self.MessageBox.setMaximumWidth(self.size().width() - 70)
        # print(self.MessageBox.size())
        print("message box resize")
