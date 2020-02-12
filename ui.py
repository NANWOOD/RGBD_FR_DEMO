from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import cv2


class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()  # 父类的构造函数

        self.timer_camera = QtCore.QTimer()  # 定义定时器，用于控制显示视频的帧率
        self.cap = cv2.VideoCapture()  # 视频流
        self.cap_depth = cv2.VideoCapture()
        self.CAM_NUM = 0  # 为0时表示视频流来自笔记本内置摄像头
        self.CAM_DEPTH_NUM = 0
        self.modeFlag = 0
        self.isRoot = 0
        self.isinit = 1
        self.set_ui()  # 初始化程序界面
        self.slot_init()  # 初始化槽函数
    '''程序界面布局'''

    def set_ui(self):
        self.__layout_main = QtWidgets.QHBoxLayout()  # 总布局
        self.__layout_fun_button = QtWidgets.QVBoxLayout()  # 按键布局
        self.__layout_data_show = QtWidgets.QVBoxLayout()  # 数据(视频)显示布局
        self.button_open_camera = QtWidgets.QPushButton('打开相机')  # 建立用于打开摄像头的按键
        self.button_get_image = QtWidgets.QPushButton('录入')
        self.button_test_image = QtWidgets.QPushButton('检测')
        self.button_close = QtWidgets.QPushButton('退出')  # 建立用于退出程序的按键
        self.button_open_camera.setMinimumHeight(50)  # 设置按键大小
        self.button_close.setMinimumHeight(50)
        self.button_get_image.setMinimumHeight(50)
        self.button_test_image.setMinimumHeight(50)

        menubar = self.menuBar()
        funMenu = menubar.addMenu('Mode')
        self.RGBAct = QtWidgets.QAction('RGB', self, checkable=True)
        self.DAct = QtWidgets.QAction('D', self, checkable=True)
        self.RGBDAct = QtWidgets.QAction('RGBD', self, checkable=True)
        self.rootAct = QtWidgets.QAction('Authority', self, checkable=True)

        self.RGBAct.setChecked(True)

        funMenu.addAction(self.RGBAct)
        funMenu.addAction(self.DAct)
        funMenu.addAction(self.RGBDAct)
        funMenu.addAction(self.rootAct)

        self.RGBAct.setToolTip('Face Recognition with only RGD image')
        self.DAct.setToolTip('Face Recognition with only Depth image')
        self.RGBDAct.setToolTip('Face Recognition with both RGD image and Depth image')
        self.rootAct.setToolTip('The authority mode to register information')

        self.button_close.move(10, 100)  # 移动按键
        '''信息显示'''
        self.label_show_camera = QtWidgets.QLabel()  # 定义显示视频的Label
        self.label_show_camera.setFixedSize(321, 241)  # 给显示视频的Label设置大小为641x481
        self.label_show_camera_depth = QtWidgets.QLabel()
        self.label_show_camera_depth.setFixedSize(321, 241)

        '''把按键加入到按键布局中'''
        self.__layout_fun_button.addWidget(self.button_open_camera)  # 把打开摄像头的按键放到按键布局中
        self.__layout_fun_button.addWidget(self.button_get_image)
        self.__layout_fun_button.addWidget(self.button_test_image)
        self.__layout_fun_button.addWidget(self.button_close)  # 把退出程序的按键放到按键布局中

        self.__layout_data_show.addWidget(self.label_show_camera)
        self.__layout_data_show.addWidget(self.label_show_camera_depth)
        '''把某些控件加入到总布局中'''
        self.__layout_main.addLayout(self.__layout_fun_button)  # 把按键布局加入到总布局中
        self.__layout_main.addLayout(self.__layout_data_show)
        # self.__layout_main.addWidget(self.label_show_camera)  # 把用于显示视频的Label加入到总布局中
        # self.__layout_main.addWidget(self.label_show_camera_depth)
        '''总布局布置好后就可以把总布局作为参数传入下面函数'''
        # self.setLayout(self.__layout_main)  # 到这步才会显示所有控件
        widget = QtWidgets.QWidget()
        widget.setLayout(self.__layout_main)
        self.setCentralWidget(widget)

        self.setWindowTitle('RGBD_FR_V0')
        self.button_get_image.hide()


    '''初始化所有槽函数'''

    def slot_init(self):
        self.button_open_camera.clicked.connect(
            self.button_open_camera_clicked)  # 若该按键被点击，则调用button_open_camera_clicked()
        self.timer_camera.timeout.connect(self.show_camera)  # 若定时器结束，则调用show_camera()
        self.button_close.clicked.connect(self.close)  # 若该按键被点击，则调用close()，注意这个close是父类QtWidgets.QWidget自带的，会关闭程序
        self.button_get_image.clicked.connect(self.capture)
        self.button_test_image.clicked.connect(self.test)
        self.RGBAct.triggered.connect(self.selectRGBMode)
        self.DAct.triggered.connect(self.selectDMode)
        self.RGBDAct.triggered.connect(self.selectRGBDMode)
        self.rootAct.triggered.connect(self.selectRootMode)

    '''槽函数之一'''

    def button_open_camera_clicked(self):
        if(self.modeFlag == 0):
            if(self.isinit == 1):
                self.label_show_camera_depth.hide()
                self.isinit = 0
            if self.timer_camera.isActive() == False:  # 若定时器未启动
                flag = self.cap.open(self.CAM_NUM)  # 参数是0，表示打开笔记本的内置摄像头，参数是视频文件路径则打开视频
                if flag == False:  # flag表示open()成不成功
                    msg = QtWidgets.QMessageBox.warning(self, 'warning', "请检查相机于电脑是否连接正确", buttons=QtWidgets.QMessageBox.Ok)
                else:
                    self.timer_camera.start(30)  # 定时器开始计时30ms，结果是每过30ms从摄像头中取一帧显示
                    self.button_open_camera.setText('关闭相机')
            else:
                self.timer_camera.stop()  # 关闭定时器
                self.cap.release()  # 释放视频流
                self.label_show_camera.clear()  # 清空视频显示区域
                self.button_open_camera.setText('打开相机')
        elif(self.modeFlag == 1):
            if self.timer_camera.isActive() == False:  # 若定时器未启动
                flag = self.cap_depth.open(self.CAM_DEPTH_NUM)  # 参数是0，表示打开笔记本的内置摄像头，参数是视频文件路径则打开视频
                if flag == False:  # flag表示open()成不成功
                    msg = QtWidgets.QMessageBox.warning(self, 'warning', "请检查深度相机于电脑是否连接正确", buttons=QtWidgets.QMessageBox.Ok)
                else:
                    self.timer_camera.start(30)  # 定时器开始计时30ms，结果是每过30ms从摄像头中取一帧显示
                    self.button_open_camera.setText('关闭相机')
            else:
                self.timer_camera.stop()  # 关闭定时器
                self.cap_depth.release()  # 释放视频流
                self.label_show_camera_depth.clear()  # 清空视频显示区域
                self.button_open_camera.setText('打开相机')
        else:
            if self.timer_camera.isActive() == False:  # 若定时器未启动
                flag = self.cap.open(self.CAM_NUM)  # 参数是0，表示打开笔记本的内置摄像头，参数是视频文件路径则打开视频
                flag1 = self.cap_depth.open(self.CAM_DEPTH_NUM)
                flag2 = 0
                if(flag == False):
                    msg = QtWidgets.QMessageBox.warning(self, 'warning', "请检查相机于电脑是否连接正确",
                                                        buttons=QtWidgets.QMessageBox.Ok)
                    flag2 = 1
                if(flag1 == False):
                    msg1 = QtWidgets.QMessageBox.warning(self, 'warning', "请检查深度相机于电脑是否连接正确",
                                                        buttons=QtWidgets.QMessageBox.Ok)
                    flag2 = 1
                if(flag2 == 0):
                    self.timer_camera.start(30)  # 定时器开始计时30ms，结果是每过30ms从摄像头中取一帧显示
                    self.button_open_camera.setText('关闭相机')
            else:
                self.timer_camera.stop()  # 关闭定时器
                self.cap.release()  # 释放视频流
                self.cap_depth.release()
                self.label_show_camera.clear()  # 清空视频显示区域
                self.label_show_camera_depth.clear()
                self.button_open_camera.setText('打开相机')

    def show_camera(self):
        if(self.modeFlag == 0):
            flag, self.image = self.cap.read()  # 从视频流中读取
            show = cv2.resize(self.image, (320, 240))  # 把读到的帧的大小重新设置为 640x480
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0],
                                     QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
            self.label_show_camera.setPixmap(QtGui.QPixmap.fromImage(showImage))  # 往显示视频的Label里 显示QImage
        elif(self.modeFlag == 1):
            flag, self.image_depth = self.cap_depth.read()  # 从视频流中读取
            show = cv2.resize(self.image_depth, (320, 240))  # 把读到的帧的大小重新设置为 640x480
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0],
                                     QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
            self.label_show_camera_depth.setPixmap(QtGui.QPixmap.fromImage(showImage))  # 往显示视频的Label里 显示QImage
        else:
            flag, self.image = self.cap.read()  # 从视频流中读取
            flag1, self.image_depth = self.cap_depth.read()
            show = cv2.resize(self.image, (320, 240))  # 把读到的帧的大小重新设置为 640x480
            show1 = cv2.resize(self.image_depth, (320, 240))
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
            show1 = cv2.cvtColor(show1, cv2.COLOR_BGR2RGB)
            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0],
                                     QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
            showImage1 = QtGui.QImage(show1.data, show1.shape[1], show1.shape[0], QtGui.QImage.Format_RGB888)
            self.label_show_camera.setPixmap(QtGui.QPixmap.fromImage(showImage))  # 往显示视频的Label里 显示QImage
            self.label_show_camera_depth.setPixmap(QtGui.QPixmap.fromImage(showImage1))

    def capture(self):
        if(self.modeFlag == 0):
            flag, self.image = self.cap.read()  # 从视频流中读取
            print(self.image)
        elif(self.modeFlag == 1):
            flag, self.image_depth = self.cap_depth.read()
            print(self.image_depth)
        else:
            flag, self.image = self.cap.read()
            flag1, self.image_depth = self.cap_depth.read()
            print(self.image)
            print(self.image_depth)

    def test(self):
        if (self.modeFlag == 0):
            flag, self.image = self.cap.read()  # 从视频流中读取
            print(self.image)
        elif (self.modeFlag == 1):
            flag, self.image_depth = self.cap_depth.read()
            print(self.image_depth)
        else:
            flag, self.image = self.cap.read()
            flag1, self.image_depth = self.cap_depth.read()
            print(self.image)
            print(self.image_depth)

    def selectRGBMode(self):
        if(self.modeFlag == 1):
            self.label_show_camera.show()
            self.modeFlag = 0
            self.DAct.setChecked(False)
            self.RGBDAct.setChecked(False)
            self.timer_camera.stop()  # 关闭定时器
            self.cap_depth.release()
            self.label_show_camera_depth.clear()
            self.button_open_camera.setText('打开相机')
            print('RGB')
        elif(self.modeFlag == 2):
            self.label_show_camera_depth.hide()
            self.modeFlag = 0
            self.DAct.setChecked(False)
            self.RGBDAct.setChecked(False)
            self.timer_camera.stop()  # 关闭定时器
            self.cap.release()  # 释放视频流
            self.cap_depth.release()
            self.label_show_camera.clear()  # 清空视频显示区域
            self.label_show_camera_depth.clear()
            self.button_open_camera.setText('打开相机')
            print('RGB')
        else:
            self.RGBAct.setChecked(True)

    def selectDMode(self):
        if(self.modeFlag == 0):
            self.label_show_camera.hide()
            self.label_show_camera_depth.show()
            self.modeFlag = 1
            self.RGBAct.setChecked(False)
            self.RGBDAct.setChecked(False)
            self.timer_camera.stop()  # 关闭定时器
            self.cap.release()  # 释放视频流
            self.label_show_camera.clear()  # 清空视频显示区域
            self.button_open_camera.setText('打开相机')
            print('D')
        elif(self.modeFlag == 2):
            self.label_show_camera.hide()
            self.modeFlag = 1
            self.RGBAct.setChecked(False)
            self.RGBDAct.setChecked(False)
            self.timer_camera.stop()  # 关闭定时器
            self.cap.release()  # 释放视频流
            self.cap_depth.release()
            self.label_show_camera.clear()  # 清空视频显示区域
            self.label_show_camera_depth.clear()
            self.button_open_camera.setText('打开相机')
            print('D')
        else:
            self.DAct.setChecked(True)

    def selectRGBDMode(self):
        if(self.modeFlag == 0):
            self.label_show_camera_depth.show()
            self.modeFlag = 2
            self.DAct.setChecked(False)
            self.RGBAct.setChecked(False)
            self.timer_camera.stop()  # 关闭定时器
            self.cap.release()  # 释放视频流
            self.label_show_camera.clear()  # 清空视频显示区域
            self.button_open_camera.setText('打开相机')
            print('RGBD')
        elif(self.modeFlag == 1):
            self.label_show_camera.show()
            self.modeFlag = 2
            self.DAct.setChecked(False)
            self.RGBAct.setChecked(False)
            self.timer_camera.stop()
            self.cap_depth.release()
            self.label_show_camera_depth.clear()
            self.button_open_camera.setText('打开相机')
            print('RGBD')
        else:
            self.RGBDAct.setChecked(True)

    def selectRootMode(self):
        if(self.isRoot == 0):
            self.showDialog()
        else:
            self.isRoot = 0
            self.button_get_image.hide()

    def showDialog(self):

        # text, ok = QtWidgets.QInputDialog.getText(self, 'Login',
        #                                 'Enter password:', QtWidgets.QLineEdit.Password)
        self.passwdinput = QtWidgets.QDialog()
        self.passwdinput.setWindowTitle('Login')
        self.passwdinput.setFixedSize(220, 110)
        self.passwdinput.setWindowModality(QtCore.Qt.ApplicationModal)
        self.btn_ok = QtWidgets.QPushButton('Login', self.passwdinput)
        self.btn_cancel = QtWidgets.QPushButton('Cancel', self.passwdinput)
        self.passwdlabel = QtWidgets.QLabel(parent=self.passwdinput)
        self.passwdlabel.setText('Enter your password:')
        self.passwdedit = QtWidgets.QLineEdit(parent=self.passwdinput)
        self.passwdedit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.wrongpasswd = QtWidgets.QLabel(parent=self.passwdinput)
        self.wrongpasswd.setText("Wrong Password!")
        self.wrongpasswd.setStyleSheet("color:red")
        self.wrongpasswd.hide()
        self.wrongpasswd.move(45, 60)
        self.passwdedit.move(45, 35)
        self.passwdlabel.move(45, 10)
        self.btn_ok.move(120, 75)
        self.btn_cancel.move(30, 75)
        self.btn_cancel.clicked.connect(self.loginCancel)
        self.btn_ok.clicked.connect(self.checkPasswd)
        self.passwdinput.exec_()

    def loginCancel(self):
        self.rootAct.setChecked(False)
        self.passwdinput.close()

    def checkPasswd(self):
        passwd = self.passwdedit.text()
        if(passwd == 'scubrlabs'):
            self.isRoot = 1
            self.button_get_image.show()
            self.passwdinput.close()
        else:
            self.wrongpasswd.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)  # 固定的，表示程序应用
    ui = Ui_MainWindow()  # 实例化Ui_MainWindow
    ui.show()  # 调用ui的show()以显示。同样show()是源于父类QtWidgets.QWidget的
    sys.exit(app.exec_())

