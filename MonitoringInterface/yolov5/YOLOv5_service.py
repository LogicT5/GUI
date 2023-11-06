import argparse
import os
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.backends.cudnn as cudnn

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.common import DetectMultiBackend
from utils.datasets import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, time_sync


def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    # Resize and pad image while meeting stride-multiple constraints
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better val mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return im, ratio, (dw, dh)


def LoadModel(weights=ROOT / 'PersonAndFire.pt',  # model.pt path(s)
              data=ROOT / 'data/SmartHome.yaml',  # dataset.yaml path
              device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
              half=False,  # use FP16 half-precision inference 半精度浮点数
              dnn=False,  # use OpenCV DNN for ONNX inference
              ):
    # Load model 载入模型
    device = select_device(device)  # 选用CPU或GPU 标准处理device
    model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data, fp16=half)
    return model, device


def run_test(img0,
             model,
             device,
             imgsz=(640,640),  # inference size (height, width)
             conf_thres=0.5,  # confidence threshold
             iou_thres=0.45,  # NMS IOU threshold
             max_det=100,  # maximum detections per image
             classes=None,  # filter by class: --class 0, or --class 0 2 3
             agnostic_nms=False,  # class-agnostic NMS
             augment=False,  # augmented inference
             visualize=False,  # visualize features
             line_thickness=2,  # bounding box thickness (pixels)
             ):
    # data对应yml文件中存着分类标签
    returnList = list() # 存储返回信息
    xyxy = [0,0,0,0]
    c = -1
    # names 存储对应的标签
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = check_img_size(imgsz, s=stride)  # check image size
    # # stride = 32?
    bs = 1  # batch_size
    # Run inference
    model.warmup(imgsz=(1 if pt else bs, 3, *imgsz))  # warmup
    dt, seen = [0.0, 0.0, 0.0], 0
    # for path, im, im0s, vid_cap, s in dataset:

    # Padded resize
    img = letterbox(img0, imgsz, stride=stride, auto=pt)[0]

    # Convert
    img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
    img = np.ascontiguousarray(img)

    t1 = time_sync()
    img = torch.from_numpy(img).to(device)
    img = img.half() if model.fp16 else img.float()  # uint8 to fp16/32
    img /= 255  # 0 - 255 to 0.0 - 1.0
    if len(img.shape) == 3:
        img = img[None]  # expand for batch dim
    t2 = time_sync()
    dt[0] += t2 - t1

    # Inference
    # 更新可视化相关地址 visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False
    pred = model(img, augment=augment, visualize=visualize)
    t3 = time_sync()
    dt[1] += t3 - t2

    # NMS
    pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
    dt[2] += time_sync() - t3
    s = ''
    # Process predictions
    for i, det in enumerate(pred):  # per image
        returnList.clear()
        seen += 1
        gn = torch.tensor(img0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
        annotator = Annotator(img0, line_width=line_thickness, example=str(names))
        s += '%gx%g ' % img.shape[2:]  # print string
        if len(det):
            # Rescale boxes from img_size to img0 size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img0.shape).round()

            # Print results
            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum()  # detections per class
                s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

            # Write results  每一类的一个对象循环一次
            for *xyxy, conf, cls in reversed(det):
                # if save_txt:  # Write to file
                xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                line = (cls, *xywh, conf)
                # print(('%g ' * len(line)).rstrip() % line)
                # if view_img:  # Add bbox to image
                c = int(cls)  # integer class
                label = f'{names[c]} {conf:.2f}'
                annotator.box_label(xyxy, label, color=colors(c, True))

        # Stream results
        img0 = annotator.result()
        # print(s)
        P = ((int(xyxy[0]) + int(xyxy[2]))/2 ,(int(xyxy[1]) + int(xyxy[3]))/2)
        # print(c,P)
        returnList.append(img0)
        returnList.append(c)
        returnList.append(P)
        return returnList


def main():
    check_requirements(exclude=('tensorboard', 'thop'))
    path = "D:\WorkSpace\Python_WorkSpace\SmartHome\yolov5\data\images\zidane.jpg"
    model, device = LoadModel()
    img0 = cv2.imread(path)
    img0 = run_test(img0, model, device)
    cv2.imshow('Distracted_Driver_Detection-Droidcam', img0)


if __name__ == "__main__":
    # main()
    check_requirements(exclude=('tensorboard', 'thop'))
    cam = cv2.VideoCapture('rtsp://admin:Tianhuan0122@192.168.3.21:554/stream1')
    model, device = LoadModel()
    while True:
        ret, img_cv0 = cam.read()
        if ret:
            print(img_cv0.shape)
            # img_cv0 = cv2.flip(img_cv0, 0)  # 这里用到的是垂直翻转，因为后面的参数是0
            img_cv2 = run_test(img_cv0, model, device)
            cv2.imshow('Distracted_Driver_Detection-Droidcam', img_cv2)
            if cv2.waitKey(1) == 27:
                break
