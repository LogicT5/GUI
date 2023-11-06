from PyQt5.QtWidgets import QWidget, QVBoxLayout

from DialogueWindow.MessageBox import MessageBox
from DialogueWindow.DialogBox import DialogBox
from DialogueWindow.MessageBag import MessageBag

class ChatWindow(QWidget):
    def __init__(self,parent=None):
        super(ChatWindow,self).__init__(parent)
        # 消息列表  &&  生成气泡
        self.MessageList=[]

        self.VerticalLayout = QVBoxLayout()
        self.VerticalLayout.setContentsMargins(0, 0, 0, 0)
        self.VerticalLayout.setSpacing(0)

        self.MessageBox = MessageBox(self)
        self.VerticalLayout.addWidget(self.MessageBox)

        self.DialogBox = DialogBox(self)
        self.DialogBox.send_message_signal.connect(self.sendMessage)
        self.VerticalLayout.addWidget(self.DialogBox)

        self.VerticalLayout.setStretch(0,7)
        self.VerticalLayout.setStretch(1,3)
        self.setLayout(self.VerticalLayout)

    def sendMessage(self,Message):
        self.MessageList.append(MessageBag('user',Message))
        # self.MessageBox.

    def resizeEvent(self, event):
        # 当窗口大小发生改变时调用此方法
        super().resizeEvent(event)
        # print(self.size())
        self.resize(self.size())
        print("chat windows resize")