import os
import sqlite3

dir_path = os.path.dirname(os.path.abspath(__file__))

def SpliceURL(Type, CameraIPAddress, Username, Password):
    if Type == 'TP-LINK':
        return '\'rtsp://' + Username + ':' + Password + '@' + CameraIPAddress + ':554/stream1\''
    if Type == 'ESP32-CAM':
        return '\'http://' + CameraIPAddress + ':81/stream\''

def RepeatCheck(CameraList, Type, CamIPAddress, Username, Password, URL):
    for i in range(len(CameraList)):
        if CameraList[i][2] == CamIPAddress and CamIPAddress is not None:
            print('重复IP(' + str(CamIPAddress) + ')', end='')
            return False
        else:
            if( CameraList[i][-3] == URL or CameraList[i][-3] == SpliceURL(Type, CamIPAddress, Username,Password) )and URL is not None:
                print('重复URL(' + str(URL) + ')', end='')
                return False
    return True


def Py2SQgrammar(Type, CamIPAddress, Username, Password, URL, Position):
    if URL is not None:
        if URL[0] != "'":
            URL = "'" + URL + "'"
    else:
        URL = SpliceURL(Type, CamIPAddress, Username, Password)
    Type = "NULL" if Type is None else "'" + Type + "'"
    CamIPAddress = "NULL" if CamIPAddress is None else "'" + CamIPAddress + "'"
    Username = "NULL" if Username is None else "'" + Username + "'"
    Password = "NULL" if Password is None else "'" + Password + "'"
    Position = "NULL" if Position is None else "'" + Position + "'"
    return Type, CamIPAddress, Username, Password, URL, Position


class ManageCamData:
    def __init__(self, Table):
        self.Table = Table
        print(self.Table)
        dbPath = os.path.join(os.path.join(os.path.abspath(os.path.dirname(dir_path) + os.path.sep + "."),
                                           'CameraData'), 'CamData')
        self.db = sqlite3.connect(dbPath)
        self.dbTable = self.db.cursor()
        self.CamDataList = self.ReadCameraData()

    def ReadCameraData(self):
        select = "SELECT * FROM {0};" .format(self.Table)
        CamData = self.db.execute(select)
        CamList = list()
        for row in CamData:
            CamList.append(row)
        print(CamList)
        return CamList

    def ReadCamOtherData(self, index):
        select = "SELECT Other FROM {0} WHERE Num ={1} ;" .format(self.Table,index)
        CamOtherData = list()
        OtherData = list()
        ServoPos = list()
        for row in self.db.execute(select):
            CamOtherData.append(row)
        print(len(CamOtherData),CamOtherData,type(CamOtherData))
        if CamOtherData == []:
            return False, None, None
        else:
            # print(len(CamOtherData))
            if CamOtherData == [(None,)]:
                return False, None, None
            print(CamOtherData[0][0].split(','))
            for data in CamOtherData[0][0].split(','):
                if data != '':
                    OtherData.append(int(data))
                else:
                    return False ,None ,None
            ServoPos.append(OtherData.pop())
            ServoPos.append(OtherData.pop())
            print(OtherData,ServoPos)
            return True,OtherData ,ServoPos

    def WriteCamOtherData(self, OtherData, index):
        date = ''
        for i in OtherData:
            date += str(i) + ','
        date = '\'' + date[:-1] + '\''
        update = "UPDATE {0} SET Other = {1} WHERE Num = {2};".format(self.Table,date,index)
        print(update)
        self.dbTable.execute(update)
        self.db.commit()

    def addCamera(self, Type, CamIPAddress, Username, Password, URL, Position):
        # 本地数据库存储摄像头信息，@编号；类型、摄像头ip地址、用户名、密码、URl、部署位置
        if CamIPAddress is None and URL is None:
            print('IP地址和URL同时为空，非法输入')
            return False
        CamDataList = self.ReadCameraData()
        Num = len(CamDataList)
        if RepeatCheck(CamDataList, Type, CamIPAddress, Username, Password, URL):
            Type, CamIPAddress, Username, Password, URL, Position = Py2SQgrammar(Type, CamIPAddress, Username, Password,
                                                                                 URL, Position)
            insert = "INSERT INTO {0} (Num,Type,CamIPAddress,Username,Password,URL,Position) VALUES ({1},{2},{3},{4},{5},{6},{7});".format( self.Table, Num, Type, CamIPAddress, Username, Password, URL, Position)
            print(insert)
            self.dbTable.execute(insert)
            self.db.commit()
            self.CamDataList = self.ReadCameraData()
            return True
        else:
            return False

    def EditCamera(self, index, Type, CamIPAddress, Username, Password, URL, Position):
        if RepeatCheck(self.CamDataList, Type, CamIPAddress, Username, Password, URL):
            Type, CamIPAddress, Username, Password, URL, Position = Py2SQgrammar(Type, CamIPAddress, Username, Password,
                                                                                 URL, Position)
            print(Type, CamIPAddress, Username, Password, URL, Position)
            update = "UPDATE {0} SET Type ={1},CamIPAddress ={2},Username={3},Password={4},URL={5},Position={6} WHERE Num = {7};".format(self.Table, Type, CamIPAddress, Username, Password, URL, Position, index)
            self.dbTable.execute(update)
            self.db.commit()
            self.CamDataList = self.ReadCameraData()
            return True
        else:
            return False

    def RemoveCamera(self, index):
        self.CamDataList = self.ReadCameraData()
        self.CamDataList.pop(index)
        delete = "DELETE FROM {0} WHERE Num={1};".format(self.Table,index)
        self.dbTable.execute(delete)
        if len(self.CamDataList) != 0:
            for i in range(index ,len(self.CamDataList)):
                update = "UPDATE {0} SET Num={1} WHERE Num={2};".format(self.Table,i , i + 1)
                self.dbTable.execute(update)
        self.db.commit()


if __name__ == '__main__':
    CamData = ManageCamData("OutdoorCamData")
    otherdata = [255,255,255,255,255,255]
    # CamData.addCamera('ESP32-CAM', '192.168.0.233', None, None, None, None)
    # CamData.addCamera('TP-LINK', '192.168.0.234', '123', '258', None, None)
    CamData.addCamera('URL接入设备', None, None, None, 'http://192.168.0.235:81/stream', None)
    # CamData.addCamera('ESP32-CAM', '192.168.0.225:81', None, None, None, "室内")
    # CamData.ReadCameraData()
    # CamData.RemoveCamera(1)
    # CamData.WriteCamOtherData(otherdata,0)
    # CamData.ReadCamOtherData(0)
