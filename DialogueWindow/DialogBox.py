from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont, QKeyEvent
from PyQt5.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout, QPlainTextEdit
from PyQt5.QtCore import Qt


class PlainTextEdit(QPlainTextEdit):  #父类为QPlainTextEdit
    enterPressEvent = QtCore.pyqtSignal(bool)
    def __init__(self,parent=None):
        super(PlainTextEdit, self).__init__(parent)
        # self.setAcceptRichText(False)

    def keyPressEvent(self, event: QKeyEvent): #重写keyPressEvent方法
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:#ctrl+回车
            self.insertPlainText('\n')                                              #添加换行
        elif self.toPlainText() and event.key() == Qt.Key_Return:                   #回车
            self.enterPressEvent.emit(True)
        else:
            super().keyPressEvent(event)


class DialogBox(QWidget):
    send_message_signal = QtCore.pyqtSignal(str)

    def __init__(self,parent=None):
        super(DialogBox,self).__init__(parent)
        self.VerticalLayout = QtWidgets.QVBoxLayout()
        self.VerticalLayout.setContentsMargins(5, 5, 5, 5)
        self.VerticalLayout.setSpacing(5)

        self.TextInput = PlainTextEdit()
        self.TextInput.setFont(QFont("Arial", 16))
        self.TextInput.enterPressEvent.connect(self.clickedEnter)
        self.TextInput.setStyleSheet("""
                                    QPlainTextEdit {
                                        background-color: #f0f0f0;
                                        color: #333333;
                                        border: 2px solid #d0d0d0;
                                        border-radius: 10px;
                                        padding: 10px;
                                    }
                                """)
        self.VerticalLayout.addWidget(self.TextInput)

        self.SendButton = QPushButton("发送")
        self.SendButton.setFont(QFont("黑体", 24))
        self.SendButton.setMinimumHeight(80)
        # self.SendButton.setMinimumSize(QSize(100,self.TextInput.size().height()))
        self.SendButton.clicked.connect(self.sendMessage)
        self.SendButton.setStyleSheet("""
                                          QPushButton {
                                              background-color: #50FAC9;
                                              color: #000000;
                                              border-radius: 20px;
                                          }
                                          QPushButton:pressed {
                                              border: 5px solid #CFCFCF;
                                              border-radius: 20px;
                                          }
                                          QPushButton:hover {
                                              background-color: #C9FAEF;
                                              color: #B0B0B0;
                                              border-radius: 20px;
                                          }
                                      """
                                      )
        self.VerticalLayout.addWidget(self.SendButton)

        self.VerticalLayout.setStretch(0,7)
        self.VerticalLayout.setStretch(1,3)
        self.setLayout(self.VerticalLayout)


    def clickedEnter(self,event):
        if event:
            message = self.TextInput.toPlainText().replace('\n', '')
            print(message)
            self.send_message_signal.emit(message)
            self.TextInput.clear()
            # print(event)
    def sendMessage(self):
        message = self.TextInput.toPlainText()
        print(message)
        self.send_message_signal.emit(message)
        self.TextInput.clear()

    def resizeEvent(self, event):
        # 当窗口大小发生改变时调用此方法
        super().resizeEvent(event)
        # print(self.size())
        self.resize(self.size())