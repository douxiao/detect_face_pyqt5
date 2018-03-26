#!/usr/bin/python3
# -*-coding:utf-8-*-
# @Time    : 18-3-26 上午11:40
# @Author  : sunshine.dxiao
# @FileName: read_cam.py
# @Blog    : www.douxiao.org
# coding=utf-8
import cv2
from config import *  # 引入配置文件包

link = cam_link()
while (True):  # 等待摄像头连接
    print("未检测到摄像头，请检查设备连接！")
    link = cam_link()
    if link == 0:
        break
source = get_rtsp()
cam = cv2.VideoCapture(source)

while (True):
    # get a frame
    ret, frame = cam.read()
    # show a frame
    cv2.imshow("window", frame)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
# 释放摄像头对象和窗口
cam.release()
cv2.destroyAllWindows()
