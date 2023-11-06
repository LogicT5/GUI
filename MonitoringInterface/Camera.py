import os
import time

import PIL
import cv2
import numpy as np
# from yolov5 import YOLOv5_service
# from MonitoringInterface.yolov5 import YOLOv5_service
from multiprocessing import Queue
import threading

dir_path = os.path.dirname(os.path.abspath(__file__))
ERROR1_path = os.path.join(os.path.join(os.path.abspath(os.path.dirname(dir_path) + os.path.sep + "."),
                                        'img'), 'ERROR1.jpg')
# model, device = YOLOv5_service.LoadModel()
# name = model.names


class Camera():
    pass
    def __init__(self, CameraId):
        super(Camera, self).__init__()
        self.camera_id = CameraId
        self.queue = Queue()
        self.IntrusionTimes = 2
        self.DetectionArea = [208, 203, 816, 763]  # X0 Y0 X1 Y1
        self.FireAlarmFlage = False
        self.IntrusionFlage = False
        self.AlarmFlage = False
        self.ThreadFlag = False
        self.cap = cv2.VideoCapture(self.camera_id)
        self.img = cv2.imread(ERROR1_path, cv2.IMREAD_UNCHANGED)
        # if self.CheckVideo():
        #     threading.Thread(target=self.VideoStreamImg).start()
        #     threading.Thread(target=self.Detection).start()
        self.getImg_thread = threading.Thread(target=self.VideoStreamImg)
        # self.detImg_thread = threading.Thread(target=self.Detection)
        self.getImg_thread.setDaemon(True)
        # self.detImg_thread.setDaemon(True)


    def start(self):
        self.ThreadFlag = True
        self.getImg_thread.start()
        # self.detImg_thread.start()

    def stop(self):
        self.ThreadFlag = False

    def CheckVideo(self):
        if self.cap.isOpened():
            return True
        else:
            return False

    def setDetectionArea(self, DetectionArea):
        for i in range(4):
            self.DetectionArea[i] = DetectionArea[i]

    def get_img(self):
        if self.IntrusionTimes <= 0 and self.AlarmFlage is False:
            self.IntrusionTimes = 2
            self.IntrusionFlage = True
            self.AlarmFlage = True
            print('有人')
        return self.queue.get(), self.IntrusionFlage, self.FireAlarmFlage

    def VideoStreamImg(self):
        timeF = 15  # 视频帧计数间隔频率
        c = 0
        while self.ThreadFlag:
            ret, img_cv0 = self.cap.read()
            if ret:
                print(c)
                if (c % timeF == 0):  # 每隔timeF帧进行检测操作
                    #self.queue.put(img_cv0)
                    imgList = YOLOv5_service.run_test(img_cv0, model, device)
                    self.queue.put(imgList[0])
                    # self.img = imgList[0]
                    if imgList[1] == 0:
                        self.IntrusionDetection(imgList[2])
                    elif imgList[1] == 1 and self.AlarmFlage is False:
                        self.FireAlarm()
                    print('检测')
                    c = 1
                else:
                    self.queue.put(img_cv0)
                    c += 1
            time.sleep(0.05)


    def Detection(self):
        while self.ThreadFlag:
            if not self.queue.empty():
                # imgList = self.queue.get()
                img = self.queue.get()
                # self.img = img
                imgList = YOLOv5_service.run_test(img, model, device)
                self.img = imgList[0]
                if imgList[1] == 0:
                    self.IntrusionDetection(imgList[2])
                elif imgList[1] == 1 and self.AlarmFlage is False:
                    self.FireAlarm()
                print('检测')
                # print(self.name[imgList[1]])

    def IntrusionDetection(self, P):
        if P[0] > self.DetectionArea[0] and P[0] < self.DetectionArea[2] and P[1] > self.DetectionArea[1] and P[1] < \
                self.DetectionArea[3]:
            self.IntrusionTimes -= 1

    def FireAlarm(self):
        self.FireAlarmFlage = True
        self.AlarmFlage = True

    def AlarmFlageInit(self):
        self.FireAlarmFlage = False
        self.IntrusionFlage = False
        self.AlarmFlage = False
        print("检测重置")

    def setAlarmFlage(self, Flage):
        self.AlarmFlage = Flage

    def setAlarmFales(self):
        self.AlarmFlage = False


if __name__ == '__main__':
    # cam = Camera('rtsp://admin:Tianhuan0122@192.168.3.21:554/stream1')
    cam = Camera('http://192.168.3.234:81/stream')
    cam.start()
    while True:
        img, IntrusionFlage, FireAlarmFlage = cam.get_img()
        cv2.imshow('cs', img)
        if cv2.waitKey(1) == 27:
            break
