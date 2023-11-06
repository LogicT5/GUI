import os
import sys

dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, dir_path)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from ManageCamData import ManageCamData
infomation = ["ESP32-CAM", "TP-LINK", "URL接入设备"]
ComboBox_Button_path = os.path.join(os.path.join(os.path.abspath(os.path.dirname(dir_path) + os.path.sep + "."),
                                 'img'), 'Camlist_atom.png')

class addCam(QDialog):
    def __init__(self, CamData):
        super(addCam, self).__init__(None)
        self.setWindowTitle('添加监控设备')
        # self.resize(300,500)
        self.CamData = CamData
        self.CamDataList = self.CamData.CamDataList
        qss_path = os.path.join(os.path.join(os.path.abspath(os.path.dirname(dir_path) + os.path.sep + "."), 'qss'),
                                'CamDataWindow.qss')
        with open(qss_path, 'r', encoding='utf-8') as f:
            Widget_Style = f.read()
        self.setStyleSheet(Widget_Style)

        FormLayout = QFormLayout(self)
        FormLayout.setVerticalSpacing(20)
        FormLayout.setHorizontalSpacing(15)
        FormLayout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        FormLayout.setLabelAlignment(Qt.AlignBottom | Qt.AlignHCenter)

        self.label0 = QLabel()
        label1 = QLabel(str('品牌  :'))
        label2 = QLabel(str('IP地址:'))
        label3 = QLabel(str('用户名:'))
        label4 = QLabel(str('密码  :'))
        label5 = QLabel(str('URL   :'))
        label6 = QLabel(str('位置  :'))
        label7 = QLabel(str('提示：输入URL时，从URL获取视频流，屏蔽除URL外的所有信息'))
        label7.setStyleSheet('color:red;font-size:16px;')

        self.ComboBox = QComboBox(self)
        self.ComboBox.addItems(infomation)
        self.ComboBox.view().window().setFixedHeight(150)
        self.ComboBox.setView(QListView())  # 设置此项后item样式才起作用
        self.ComboBox.setMaxVisibleItems(5)
        self.LineText0 = QLineEdit(self)
        self.LineText0.setCursorPosition(100)
        self.LineText0.setInputMask('000.000.000.000;_')
        self.LineText0.setCursorPosition(1)
        self.LineText0.setPlaceholderText('请输入IP地址')
        self.LineText1 = QLineEdit(self)
        self.LineText1.setPlaceholderText('请输入用户名')
        self.LineText2 = QLineEdit(self)
        self.LineText2.setPlaceholderText('请输入密码')
        self.LineText3 = QLineEdit(self)
        self.LineText3.setPlaceholderText('请输入URL(可为空)')
        self.LineText4 = QLineEdit(self)
        self.LineText4.setPlaceholderText('摄像头位置(可为空)')

        ButtonWidget = QWidget(self)
        HBoxLay = QHBoxLayout()
        HBoxLay.setSpacing(20)
        ButtonWidget.setLayout(HBoxLay)
        self.button0 = QPushButton(ButtonWidget)
        self.button0.setText('确定')
        self.button0.clicked.connect(self.InputDetermine)
        HBoxLay.addWidget(self.button0)
        button1 = QPushButton(ButtonWidget)
        button1.setText('取消')
        button1.clicked.connect(self.InputCancel)
        HBoxLay.addWidget(button1)

        FormLayout.addRow(self.label0)
        FormLayout.addRow(label1, self.ComboBox)
        FormLayout.addRow(label2, self.LineText0)
        FormLayout.addRow(label3, self.LineText1)
        FormLayout.addRow(label4, self.LineText2)
        FormLayout.addRow(label5, self.LineText3)
        FormLayout.addRow(label6, self.LineText4)
        FormLayout.addRow(label7)
        FormLayout.addRow(ButtonWidget)
        self.show()

    def InputDetermine(self):
        Type = self.ComboBox.currentText()
        CameraIPAddress = self.LineText0.text()
        Username = self.LineText1.text()
        Password = self.LineText2.text()
        URL = self.LineText3.text()
        Position = self.LineText4.text()
        if CameraIPAddress == '...':
            CameraIPAddress = None
        if Username == '':
            Username = None
        if Password == '':
            Password = None
        if URL == '':
            URL = None
        if Position == '':
            Position = None
        if Type == 'URL接入设备':
            if URL is None:
                MsgBox = QMessageBox(QMessageBox.Warning, 'Warning', '此设备URL不能为空')
                MsgBox.exec_()
                print('IP地址和URL同时为空，非法输入')
            else:
                CameraIPAddress = None
                Username = None
                Password = None
                self.close()
                print(Type, CameraIPAddress, Username, Password, URL, Position)
                self.AddCamData(Type, CameraIPAddress, Username, Password, URL, Position)
        else:
            if CameraIPAddress is None:
                MsgBox = QMessageBox(QMessageBox.Warning, 'Warning', '此设备IP地址不能为空')
                MsgBox.exec_()
                print('此设备IP地址不能为空')
            else:
                if Type != 'ESP32-CAM':
                    if Username is None or Password is None:
                        MsgBox = QMessageBox(QMessageBox.Warning, 'Warning', '此设备需要输入用户名和密码')
                        MsgBox.exec_()
                        print('此设备需要输入用户名和密码')
                else:
                    self.close()
                print(Type, CameraIPAddress, Username, Password, URL, Position)
                self.AddCamData(Type, CameraIPAddress, Username, Password, URL, Position)
                self.close()

    def AddCamData(self, Type, CameraIPAddress, Username, Password, URL, Position):
        if self.CamData.addCamera(Type, CameraIPAddress, Username, Password, URL, Position):
            MsgBox = QMessageBox(QMessageBox.Warning, 'Determine', '添加完成')
            MsgBox.exec_()
        else:
            MsgBox = QMessageBox(QMessageBox.Warning, 'Warning', '添加失败')
            MsgBox.exec_()

    def InputCancel(self):
        self.close()


class ManageCam(QDialog):
    def __init__(self, CamData):
        super(ManageCam, self).__init__()
        self.setWindowTitle('管理监控设备')
        self.CamData = CamData
        self.CamDataList = CamData.CamDataList
        self.DeleteButton = list()
        self.EditButton = list()
        if len(self.CamDataList) == 0:
            MsgBox = QMessageBox(QMessageBox.Warning, 'Warning', '未找到摄像头信息')
            MsgBox.exec()
        else:
            self.TableWidget = QTableWidget(self)
            # 设置表格行列数
            RowCount = len(self.CamDataList)
            ColumnCount = len(self.CamDataList[0]) - 1
            self.TableWidget.setRowCount(RowCount)
            self.TableWidget.setColumnCount(ColumnCount + 1)
            # 设置行高度为100px，列宽度为200px
            for i in range(RowCount):
                self.DeleteButton.append(QPushButton("删除"))
                self.EditButton.append(QPushButton("编辑"))
                self.DeleteButton[i].resize(100, 40)
                self.DeleteButton[i].clicked.connect(self.Delete)
                self.EditButton[i].resize(100, 40)
                self.EditButton[i].clicked.connect(self.Edit)
                self.TableWidget.setRowHeight(i, 40)
                self.TableWidget.setCellWidget(i, 7, self.DeleteButton[i])
                self.TableWidget.setCellWidget(i, 6, self.EditButton[i])
                for j in range(ColumnCount):
                    self.TableWidget.setItem(i, j - 1, QTableWidgetItem(self.CamDataList[i][j]))
            # 设置表格页面大小
            self.TableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 使表宽度自适应
            self.TableWidget.horizontalHeader().setSectionResizeMode(4, QHeaderView.Interactive)
            self.TableWidget.resizeColumnToContents(4)
            self.TableWidget.resize(900, 300)
            self.TableWidget.setHorizontalHeaderLabels(["类型", "摄像头ip地址", "用户名", "密码", "URl", "位置", "编辑", "删除"])
            self.TableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.show()

    def Delete(self):
        sender = self.sender()
        for i in range(len(self.DeleteButton)):
            if sender == self.DeleteButton[i]:
                Row = i
                break
        print(Row)
        self.CamData.RemoveCamera(Row)
        self.DeleteButton.pop(Row)
        self.EditButton.pop(Row)
        self.TableWidget.removeRow(Row)
        self.CamDataList.pop(Row)

    def Edit(self):
        sender = self.sender()
        for i in range(len(self.EditButton)):
            if sender == self.EditButton[i]:
                Row = i
                break
        print(Row)
        self.EditWindow = self.EditDataWindow(self.CamDataList[Row])
        self.EditWindow.button0.clicked.connect(self.EditData)
        self.EditWindow.show()

    def EditDataWindow(self, CamDataListRow):
        EditWindow = addCam(self.CamData)
        EditWindow.setWindowTitle("编辑摄像头信息")
        EditWindow.button0.clicked.disconnect()
        EditWindow.label0.setText(str("编辑摄像头" + str(CamDataListRow[0] + 1)))
        EditWindow.label0.setStyleSheet("font-family:SimHei;font-size:22px;")
        EditWindow.Row = CamDataListRow[0]
        EditWindow.ComboBox.setCurrentText(CamDataListRow[1])
        EditWindow.LineText0.setText(CamDataListRow[2])
        EditWindow.LineText1.setText(CamDataListRow[3])
        EditWindow.LineText2.setText(CamDataListRow[4])
        if CamDataListRow[1] == 'URL接入设备':
            EditWindow.LineText3.setText(CamDataListRow[5])
        else:
            EditWindow.LineText3.setText(" 此设备URL不可更改 ")
        EditWindow.LineText4.setText(CamDataListRow[6])
        return EditWindow

    def EditData(self):
        EditWindow = self.EditWindow
        Type = EditWindow.ComboBox.currentText()
        CameraIPAddress = EditWindow.LineText0.text()
        Username = EditWindow.LineText1.text()
        Password = EditWindow.LineText2.text()
        # URL = EditWindow.LineText3.text()
        if Type == 'URL接入设备':
            URL = EditWindow.LineText3.text()
        else:
            URL = None
        Position = EditWindow.LineText4.text()
        if CameraIPAddress == '...':
            CameraIPAddress = None
        if Username == '':
            Username = None
        if Password == '':
            Password = None
        if URL == '':
            URL = None
        if Position == '':
            Position = None
        if Type == 'URL接入设备':
            if URL is None:
                MsgBox = QMessageBox(QMessageBox.Warning, 'Warning', '此设备URL不能为空')
                MsgBox.exec_()
                print('IP地址和URL同时为空，非法输入')
            else:
                CameraIPAddress = None
                Username = None
                Password = None
                EditWindow.close()
                print(Type, CameraIPAddress, Username, Password, URL, Position)
                self.UploadData(EditWindow.Row, Type, CameraIPAddress, Username, Password, URL, Position)
        else:
            if CameraIPAddress is None:
                MsgBox = QMessageBox(QMessageBox.Warning, 'Warning', '此设备IP地址不能为空')
                MsgBox.exec_()
                print('此设备IP地址不能为空')
            else:
                if Type != 'ESP32-CAM':
                    if Username is None or Password is None:
                        MsgBox = QMessageBox(QMessageBox.Warning, 'Warning', '此设备需要输入用户名和密码')
                        MsgBox.exec_()
                        print('此设备需要输入用户名和密码')
                    else:
                        EditWindow.close()
                        print(Type, CameraIPAddress, Username, Password, URL, Position)
                        if Type == 'TP-LINK':
                            URL = '\'rtsp://' + Username + ':' + Password + '@' + CameraIPAddress + ':554/stream1\''
                        # URL = ManageCamData.SpliceURL(Type, CameraIPAddress, Username, Password)
                        print(URL)
                else:
                    EditWindow.close()
                print(Type, CameraIPAddress, Username, Password, URL, Position)
                self.UploadData(EditWindow.Row, Type, CameraIPAddress, Username, Password, URL, Position)

    def UploadData(self, Row, Type, CameraIPAddress, Username, Password, URL, Position):
        if self.CamData.EditCamera(Row, Type, CameraIPAddress, Username, Password, URL, Position):
            MsgBox = QMessageBox(QMessageBox.Warning, 'Determine', '编辑完成')
            MsgBox.exec_()
            self.TableWidget.setItem(Row, 0, QTableWidgetItem(Type))
            self.TableWidget.setItem(Row, 1, QTableWidgetItem(CameraIPAddress))
            self.TableWidget.setItem(Row, 2, QTableWidgetItem(Username))
            self.TableWidget.setItem(Row, 3, QTableWidgetItem(Password))
            self.TableWidget.setItem(Row, 4, QTableWidgetItem(URL))
            self.TableWidget.setItem(Row, 5, QTableWidgetItem(Position))
            self.CamDataList = self.CamData.CamDataList


        else:
            MsgBox = QMessageBox(QMessageBox.Warning, 'Warning', '编辑失败')
            MsgBox.exec_()

if __name__ == '__main__':
    Path = os.path.join(
        os.path.join(os.path.abspath(os.path.dirname(dir_path) + os.path.sep + "."),
                     'CameraData'), 'OutdoorMonitoring.txt')
    print(Path)
    OutCamData = ManageCamData("OutdoorCamData")
    app = QApplication(sys.argv)
    demo = ManageCam(OutCamData)
    demo.show()
    sys.exit(app.exec_())
