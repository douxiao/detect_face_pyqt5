#!/usr/bin/python3
# -*-coding:utf-8-*-
# @Time    : 18-3-6 下午7:01
# @Author  : sunshine.dxiao
# @FileName: recognition_face.py
# @Blog    : www.douxiao.org
import sys
import os
import dlib
import glob
import cv2
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from skimage import io
from datetime import datetime
import threading


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.timer_camera = QTimer()  # 需要定时器刷新摄像头界面
        self.cap = cv2.VideoCapture()
        self.cap_num = 0
        self.set_ui()  # 初始化UI界面
        self.slot_init()  # 初始化信号槽
        self.dlib_para_init()
        self.btn_flag = 0  # 开关变量
        self.local_data = []

    def set_ui(self):
        # 布局设置
        self.layout_main = QHBoxLayout()  # 整体框架是水平布局
        self.layout_button = QVBoxLayout()

        # 按钮设置
        self.btn_open_cam = QPushButton('打开相机')
        self.btn_photo = QPushButton('拍照')
        self.btn_detection_face = QPushButton('人脸检测')
        self.btn_recognition_face = QPushButton('人脸识别')

        self.btn_quit = QPushButton('退出')

        # 显示视频
        self.label_show_camera = QLabel()
        self.label_move = QLabel()
        self.label_move.setFixedSize(100, 200)

        self.label_show_camera.setFixedSize(641, 481)
        self.label_show_camera.setAutoFillBackground(False)

        # 布局
        self.layout_button.addWidget(self.btn_open_cam)
        self.layout_button.addWidget(self.btn_photo)
        self.layout_button.addWidget(self.btn_detection_face)
        self.layout_button.addWidget(self.btn_recognition_face)
        self.layout_button.addWidget(self.btn_quit)
        self.layout_button.addWidget(self.label_move)

        self.layout_main.addLayout(self.layout_button)
        self.layout_main.addWidget(self.label_show_camera)

        self.setLayout(self.layout_main)
        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle("视频图像处理软件")

    # 信号槽设置
    def slot_init(self):
        self.btn_open_cam.clicked.connect(self.btn_open_cam_click)
        self.btn_photo.clicked.connect(self.photo_face)
        self.btn_detection_face.clicked.connect(self.detect_face)
        self.btn_recognition_face.clicked.connect(self.recognize_face)
        self.timer_camera.timeout.connect(self.show_camera)
        self.btn_quit.clicked.connect(self.close)

    def btn_open_cam_click(self):
        if self.timer_camera.isActive() == False:
            flag = self.cap.open(self.cap_num)
            if flag == False:
                msg = QMessageBox.warning(self, u"Warning", u"请检测相机与电脑是否连接正确", buttons=QMessageBox.Ok,
                                          defaultButton=QMessageBox.Ok)
            # if msg==QtGui.QMessageBox.Cancel:
            #                     pass
            else:
                self.timer_camera.start(30)

                self.btn_open_cam.setText(u'关闭相机')
        else:
            self.timer_camera.stop()
            self.cap.release()
            self.label_show_camera.clear()
            self.btn_open_cam.setText(u'打开相机')

    def show_camera(self):
        harr_filepath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"  # 系统安装的是opencv-contrib-python
        classifier = cv2.CascadeClassifier(harr_filepath)  # 加载人脸特征分类器
        if self.btn_flag == 0:
            ret, self.image = self.cap.read()
            show = cv2.resize(self.image, (640, 480))
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 这里指的是显示原图
            # opencv 读取图片的样式，不能通过Qlabel进行显示，需要转换为Qimage QImage(uchar * data, int width,
            # int height, Format format, QImageCleanupFunction cleanupFunction = 0, void *cleanupInfo = 0)
            self.showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
            self.label_show_camera.setPixmap(QPixmap.fromImage(self.showImage))
        elif self.btn_flag == 1:  # 人脸检测
            ret_1, self.image_1 = self.cap.read()
            show_0 = cv2.resize(self.image_1, (640, 480))
            show_1 = cv2.cvtColor(show_0, cv2.COLOR_BGR2RGB)
            gray_image = cv2.cvtColor(show_0, cv2.COLOR_BGR2GRAY)
            faces = classifier.detectMultiScale(gray_image, 1.3, 5)  # 1.3和5是特征的最小、最大检测窗口，它改变检测结果也会改变
            for (x, y, w, h) in faces:
                cv2.rectangle(show_1, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 画出人脸
            detect_image = QImage(show_1.data, show_1.shape[1], show_1.shape[0],
                                  QImage.Format_RGB888)
            self.label_show_camera.setPixmap(QPixmap.fromImage(detect_image))

        elif self.btn_flag == 2:  # 人脸识别

            ret_2, self.image_2 = self.cap.read()
            show_2 = cv2.resize(self.image_2, (640, 480))
            self.show_3 = cv2.cvtColor(show_2, cv2.COLOR_BGR2RGB)
            gray_image = cv2.cvtColor(show_2, cv2.COLOR_BGR2GRAY)
            self.dets = self.detector(gray_image, 1)  # 对视频中的人脸进行标定
            self.dist = []  # 声明一个数组
            if not len(self.dets):
                # print('Can`t get face.')
                detect_image = QImage(self.show_3.data, self.show_3.shape[1], self.show_3.shape[0],
                                      QImage.Format_RGB888)
                self.label_show_camera.setPixmap(QPixmap.fromImage(detect_image))
            # 这里开启了一个人脸识别的线程，会自动为for循环分配线程，这里为进一步在同一个视频中，识别不同的人脸准备
            t = threading.Thread(target=self.face_thread, name='Face_Thread')
            t.start()
            t.join()

    def face_thread(self):  # 这里多线程是解决，同时识别不同人脸的关键

        print('thread %s is running...' % threading.current_thread().name)
        for k, face in enumerate(self.dets):  # 遍历视频中所有人脸 ，

            print('thread %s >>> %s' % (threading.current_thread().name, k))
            shape = self.landmark(self.show_3, face)  # 检测人脸特征点
            face_descriptor = self.facerec.compute_face_descriptor(self.show_3, shape)  # 计算人脸的128D向量
            d_test = np.array(face_descriptor)
            x1 = face.top() if face.top() > 0 else 0
            y1 = face.bottom() if face.bottom() > 0 else 0
            x2 = face.left() if face.left() > 0 else 0
            y2 = face.right() if face.right() > 0 else 0
            cv2.rectangle(self.show_3, (x2, x1), (y2, y1), (255, 0, 0), 3)
            # print(x2, x1, y2, y1)
            # 计算欧式距离
            for i in self.descriptors:  # 遍历之前提取的候选人的128D向量
                dist_ = np.linalg.norm(i - d_test)  # 计算欧式距离，有多少个候选人就有多少个距离,放到dist数组中。
                self.dist.append(dist_)
                # 候选人和距离组成一个dict字典
            # print(self.dist)
            c_d = dict(zip(self.candidate, self.dist))
            for i in range(0, len(self.candidate)):  # 注意这里必须把dist[]之前的数据pop出去，才能确保每次不同线程计算的不同人的向量。
                self.dist.pop()
            # sorted将dict字典中数排序，按key顺序（第二个关键字）
            cd_sorted = sorted(c_d.items(), key=lambda d: d[1])
            cv2.putText(self.show_3, cd_sorted[0][0], (x2, x1), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                        (0, 255, 255), 2)
            # 各参数依次是：照片/添加的文字/左上角坐标/字体/字体大小/颜色/字体粗细
            print("\n The person is: ", cd_sorted[0][0])
            detect_image = QImage(self.show_3.data, self.show_3.shape[1], self.show_3.shape[0],
                                  QImage.Format_RGB888)
            self.label_show_camera.setPixmap(QPixmap.fromImage(detect_image))

    def detect_face(self):

        if self.btn_flag == 0:
            self.btn_flag = 1
            self.btn_detection_face.setText(u'关闭人脸检测')
        elif self.btn_flag == 1:
            self.btn_flag = 0
            self.btn_detection_face.setText(u'人脸检测')

    def recognize_face(self):

        if self.btn_flag == 0:
            self.btn_flag = 2
            self.btn_recognition_face.setText(u'关闭人脸识别')
        elif self.btn_flag == 2:
            self.btn_flag = 0
            self.btn_recognition_face.setText(u'人脸识别')

    def photo_face(self):

        #   photo_save_path = '/home/dx/Desktop/detect_face_pyqt5/candidate-faces'

        photo_save_path = os.path.join(os.path.dirname(os.path.abspath('__file__')),
                                       'candidate-faces/')
        self.showImage.save(photo_save_path + datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg")

    def closeEvent(self, QCloseEvent):

        reply = QMessageBox.question(self,u"Warning", "Are you sure quit ?", QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.cap.release()
            self.timer_camera.stop()
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()

    def dlib_para_init(self):

        # 人脸关键点检测器
        #  face_landmark_path    = '/home/dx/Desktop/detect_face_pyqt5/shape_predictor_68_face_landmarks.dat'
        face_landmark_path = os.path.join(os.path.dirname(os.path.abspath('__file__')),
                                          'shape_predictor_68_face_landmarks.dat')

        # 人脸识别模型
        #  face_recognize_path   = '/home/dx/Desktop/detect_face_pyqt5/dlib_face_recognition_resnet_model_v1.dat'
        face_recognize_path = os.path.join(os.path.dirname(os.path.abspath('__file__')),
                                           'dlib_face_recognition_resnet_model_v1.dat')

        # 候选人文件夹
        #  faces_folder_path     = '/home/dx/Desktop/detect_face_pyqt5/candidate-faces'
        faces_folder_path = os.path.join(os.path.dirname(os.path.abspath('__file__')),
                                         'candidate-faces')
        # 1.加载正脸检测器
        self.detector = dlib.get_frontal_face_detector()
        # 2.加载人脸关键点检测器
        self.landmark = dlib.shape_predictor(face_landmark_path)
        # 3. 加载人脸识别模型
        self.facerec = dlib.face_recognition_model_v1(face_recognize_path)

        # 候选人脸描述子list
        self.descriptors = []
        # 对文件夹下的每一个人脸进行:

        # 1.人脸检测
        # 2.关键点检测
        # 3.描述子提取

        for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):

            print("Processing file: {}".format(f))
            self.img = io.imread(f)
            # win.clear_overlay()
            # win.set_image(img)

            # 1.人脸检测
            dets = self.detector(self.img, 1)  # 人脸标定
            print("Number of faces detected: {}".format(len(dets)))

            for k, d in enumerate(dets):
                # 2.关键点检测
                shape = self.landmark(self.img, d)
                # 画出人脸区域和和关键点
                # win.clear_overlay()
                # win.add_overlay(d)
                # win.add_overlay(shape)

                # 3.描述子提取，128D向量
                face_descriptor = self.facerec.compute_face_descriptor(self.img, shape)

                # 转换为numpy array
                v = np.array(face_descriptor)
                self.descriptors.append(v)

        # 对需识别人脸进行同样处理

        # 提取描述子，不再注释

        # 候选人名单

        self.candidate = ['dwh', 'whr', 'zjr', 'whr', 'dx', 'dx']


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
