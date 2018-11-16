# coding=utf-8
import configparser
import os

#rootdir = os.getcwd()  # 获取配置文件的绝对路径
#rootconf = os.path.join(rootdir, r'config.ini')  # 连接路径和相应文件
#print(rootconf)
# 自己在这里犯了一个错误，config.ini应该放在总工程目录下



user = 'admin'
password = '520douxiao'
host = '192.168.199.64'
port = 8000


def get_rtsp():
    # 海康威视摄像头的RSTP地址
    # 海康威视摄像头采用的是RTSP协议 RTSP 实时串流协议(Real time stream protocol,RTSP)
    # 是一种网络应用协议，专为娱乐和通信系统使用，以控制流媒体服务器。
    rtsp = "rtsp://%s:%s@%s/Streaming/Channels/1" % (user, password, host)
    print(rtsp)
    return rtsp


def get_ip():
    return host

def get_port():
    return port

def cam_link():
    ip = get_ip()
    cmd = "ping -c 1 %s" % ip
    response = os.system(cmd)  # 如果连接成功会返回0
    if response == 0:
        print("HIKCam is connected !")
        return 0
    else:
        print("HIKCam is not connected !")
        return 1

if __name__ == "__main__":
    get_rtsp()
    get_ip()
    get_port()