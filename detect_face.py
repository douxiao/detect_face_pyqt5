#!/usr/bin/python3
#-*-coding:utf-8-*-
# @Time    : 18-3-6 下午4:56
# @Author  : sunshine.dxiao
# @FileName: detect_face.py
# @Blog    : www.douxiao.org



import sys
import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.timer_camera = QTimer()  # 需要定时器刷新摄像头界面
        self.cap = cv2.VideoCapture()
        self.cap_num = 0
        self.set_ui()  # 初始化UI界面
        self.slot_init()  # 初始化信号槽
        self.detect_flag = 0  # 人脸检测开关变量
    def set_ui(self):
        # 布局设置
        self.layout_main = QHBoxLayout()  # 整体框架是水平布局
        self.layout_button = QVBoxLayout()

        # 按钮设置
        self.btn_open_cam = QPushButton(u'打开相机')
        # self.btn_open_cam.move(10, 10)

        self.btn_detection_face = QPushButton('人脸检测')


        self.quit = QPushButton('退出')
        # self.btn_close_cam.move(10, 30)

        # 显示视频
        self.label_show_camera = QLabel()
        self.label_move = QLabel()
        self.label_move.setFixedSize(100, 200)

        self.label_show_camera.setFixedSize(641, 481)
        self.label_show_camera.setAutoFillBackground(False)

        # 布局
        self.layout_button.addWidget(self.btn_open_cam)
        self.layout_button.addWidget(self.btn_detection_face)
        self.layout_button.addWidget(self.quit)
        self.layout_button.addWidget(self.label_move)

        self.layout_main.addLayout(self.layout_button)
        self.layout_main.addWidget(self.label_show_camera)

        self.setLayout(self.layout_main)
        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle("视频图像处理软件")


    # 信号槽设置
    def slot_init(self):
        self.btn_open_cam.clicked.connect(self.btn_open_cam_click)
        self.btn_detection_face.clicked.connect(self.detect_face)
        self.timer_camera.timeout.connect(self.show_camera)
        self.quit.clicked.connect(self.close)

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
        if self.detect_flag == 0:
            ret, self.image = self.cap.read()
            show = cv2.resize(self.image, (640, 480))
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 这里指的是显示原图
            # opencv 读取图片的样式，不能通过Qlabel进行显示，需要转换为Qimage QImage(uchar * data, int width,
            # int height, Format format, QImageCleanupFunction cleanupFunction = 0, void *cleanupInfo = 0)
            showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
            self.label_show_camera.setPixmap(QPixmap.fromImage(showImage))
        else:
            ret_1, self.image_1 = self.cap.read()
            show_0 = cv2.resize(self.image_1, (640, 480))
            show_1 = cv2.cvtColor(show_0, cv2.COLOR_BGR2RGB )
            gray_image = cv2.cvtColor(show_0, cv2.COLOR_BGR2GRAY)
            faces = classifier.detectMultiScale(gray_image, 1.3, 5)  # 1.3和5是特征的最小、最大检测窗口，它改变检测结果也会改变
            for (x, y, w, h) in faces:
                cv2.rectangle(show_1, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 画出人脸
            detect_image = QImage(show_1.data, show_1.shape[1], show_1.shape[0],
                                  QImage.Format_RGB888)
            self.label_show_camera.setPixmap(QPixmap.fromImage(detect_image))

    def detect_face(self):

        if self.detect_flag == 0:
            self.detect_flag = 1
            self.btn_detection_face.setText(u'关闭人脸检测')
        else:
            self.detect_flag = 0
            self.btn_detection_face.setText(u'人脸检测')






    def closeEvent(self, QCloseEvent):

        reply = QMessageBox.question(self, u"Warning", "Are you sure quit ?", QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.cap.release()
            self.timer_camera.stop()
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())


