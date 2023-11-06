import os
import sys

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout

from DialogueWindow.MessageBag import MessageBag,Role

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, dir_path)


class MessageBubble(QWidget):
    def __init__(self, message: MessageBag, parent=None):
        super(MessageBubble,self).__init__(parent)

        # self.setMaximumWidth(self.parent().width())
        self.setStyleSheet("background-color: rgba(71,121,32,255);")

        self.HorizontalLayout = QHBoxLayout()
        self.HorizontalLayout.setContentsMargins(2, 2, 2, 2)
        self.HorizontalLayout.setSpacing(5)

        self.Icon = QLabel(self)
        self.Icon.setMaximumSize(QtCore.QSize(60, 60))
        self.Icon.setScaledContents(True)
        Vlayout = QVBoxLayout()
        Vlayout.addWidget(self.Icon)
        Vlayout.addStretch(1)

        self.textFont = QFont("Arial",16)
        self.textBrowser = QtWidgets.QTextBrowser(self)
        self.textBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textBrowser.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textBrowser.setFont(self.textFont)
        self.textBrowser.setStyleSheet("padding:10px;\n"
                                       "background-color: rgba(71,121,214,255);\n"
                                       "border-radius: 20px;")
        self.textBrowser.setMinimumSize(QtCore.QSize(0, self.Icon.size().height() + 10))

        self.textBrowser.setText(message.text)

        if message.role == Role.User:
            userIcon = QtGui.QPixmap(os.path.join(os.path.join(os.path.dirname(dir_path), 'Icon'), 'User.jpg'))
            self.Icon.setPixmap(userIcon)
            self.textBrowser.setLayoutDirection(QtCore.Qt.LeftToRight)
            self.HorizontalLayout.addLayout(Vlayout)
            self.HorizontalLayout.addWidget(self.textBrowser)
            self.HorizontalLayout.addStretch(2)
            self.HorizontalLayout.addSpacing(self.Icon.size().width())
        else:
            gptIcon = QtGui.QPixmap(os.path.join(os.path.join(os.path.dirname(dir_path), 'Icon'), 'OpenAi.jpg'))
            self.Icon.setPixmap(gptIcon)
            self.textBrowser.setLayoutDirection(QtCore.Qt.RightToLeft)
            self.HorizontalLayout.addSpacing(self.Icon.size().width())
            self.HorizontalLayout.addStretch(2)
            self.HorizontalLayout.addWidget(self.textBrowser)
            self.HorizontalLayout.addLayout(Vlayout)

        self.setLayout(self.HorizontalLayout)

    def resizeEvent(self, event):
        # 当窗口大小发生改变时调用此方法
        super().resizeEvent(event)
        self.resize(self.size())

        # self.setMinimumSize()
        # self.textBrowser.resize(self.textBrowser.size())
        # print('buble',self.size().width())
        MaxWidth = self.size().width()
        brower_width = (MaxWidth - (self.Icon.size().width() * 2) - 20)
        font_metrics = QFontMetrics(self.textFont)
        bounding_rect = font_metrics.boundingRect(self.textBrowser.toPlainText())

        if bounding_rect.width() < brower_width :
            text_width = bounding_rect.width() + bounding_rect.height()
            text_height = (self.textFont.pointSize() + 10) + 40
        else:
            text_width = brower_width
            text_height = int(bounding_rect.width() / brower_width + 1) * bounding_rect.height() * 1.1 + 40

        # print(bounding_rect)
        # text_len = fm.width(self.textBrowser.toPlainText()) # 根据字体大小生成适合的气泡宽度
        # print(text_len)

        # rect = bounding_rect
        # rect = QRect(0, 0, text_width, text_height)
        # layout_rect = font_metrics.tightBoundingRect(self.textBrowser.toPlainText(), rect)
        # print(layout_rect)
        # text_width = bounding_rect.width()
        # text_height = bounding_rect.height()
        # if text_len < brower_width :
        #     text_width = text_len + self.textFont.pointSize() * 2
        #     text_height = (self.textFont.pointSize() + 10) + 40
        # else:
        #     text_width = brower_width
        #     text_height = int(text_len / text_width + 1) * (self.textFont.pointSize() + 10) + 40
        print("width", text_width)
        print("height", text_height)
        # self.textBrowser.setMinimumWidth(text_width)
        # self.textBrowser.setMaximumWidth(text_width)
        self.textBrowser.setMinimumSize(QtCore.QSize(text_width , text_height))
        self.textBrowser.setMaximumSize(QtCore.QSize(text_width , text_height))
