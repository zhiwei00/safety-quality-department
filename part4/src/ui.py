import io
import os
import sys
import threading
import time
import winreg
from traceback import print_exc
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QDesktopWidget, QFileDialog, QMessageBox
from .main_process import MainProcess
from .config import YamlConfig


def msgBox(box_type: int, box_title: str, box_text: str):
    time.sleep(0.1)
    type_list = [QMessageBox.Information, QMessageBox.Warning, QMessageBox.Critical]
    # 创建 QMessageBox 对象
    msg_box = QMessageBox()
    msg_box.setWindowTitle(box_title)
    msg_box.setIcon(type_list[box_type])
    msg_box.setText(box_text)
    # 设置窗口标志，使其总是置顶
    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
    # 显示提示窗口
    msg_box.exec()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(300, 200)
        MainWindow.setWindowFlags(Qt.WindowStaysOnTopHint)
        MainWindow.move(200, 0)
        # MainWindow.setStyleSheet('#MainWindow{backgroud-color:white}')

        btLayout = QVBoxLayout()
        self.scan = QtWidgets.QPushButton(MainWindow)
        self.scan.setObjectName("scan")
        self.config = QtWidgets.QPushButton(MainWindow)
        self.config.setObjectName("config")
        self.last_task = QtWidgets.QPushButton(MainWindow)
        self.last_task.setObjectName("last_task")
        self.submit = QtWidgets.QPushButton(MainWindow)
        self.submit.setObjectName("submit")

        btLayout.addWidget(self.scan)
        btLayout.addWidget(self.config)
        btLayout.addWidget(self.last_task)
        btLayout.addWidget(self.submit)

        MainWindow.setLayout(btLayout)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "RPA小工具"))
        self.scan.setText(_translate("MainWindow", "选择扫描文件夹"))
        self.config.setText(_translate("MainWindow", "打开配置文件"))
        self.last_task.setText(_translate("MainWindow", "运行结果"))
        self.submit.setText(_translate("MainWindow", "执行"))


class WorkerThread(QThread):
    task_finished = pyqtSignal(list)

    def __init__(self, scan_dir, debug, parent=None):
        super().__init__(parent)
        self.scan_dir = scan_dir
        self.task_dir = None
        self.debug = debug

    def get_exception_info(self, exception):
        output_buffer = io.StringIO()
        print_exc(file=output_buffer)
        exception_info = output_buffer.getvalue()
        output_buffer.close()
        return exception_info

    def run(self):
        try:
            if not self.scan_dir:
                return self.task_finished.emit([1, "警告", f"未选择扫描文件夹"])
            yaml_config = YamlConfig('config.yaml')
            config = yaml_config.read_yaml()
            input_dir = self.scan_dir
            ocr_ip = config['ocr']['ip']
            text_port = config['ocr']['port']
            nari_base = config['nari']['url']
            nari_user = config['nari']['user']
            nari_pwd = config['nari']['pwd']
            if not ocr_ip or not text_port or not nari_base or not nari_user or not nari_pwd:
                return self.task_finished.emit([1, "警告", f"请检查配置文件！"])
            main_process = MainProcess(input_dir, ocr_ip, text_port, nari_base, nari_user, nari_pwd)
            self.task_dir = main_process.run()
            return self.task_finished.emit([0, "提示", "任务处理完成"])
        except Exception as e:
            print_exc()
            exception_info = self.get_exception_info(e) if self.debug else e.__str__()
            return self.task_finished.emit([2, "错误",  exception_info])


class Main(QtWidgets.QWidget, Ui_MainWindow):
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self, debug=False, parent=None):
        super(Main, self).__init__(parent)
        self.setupUi(self)
        self.center()
        self.scan.clicked.connect(self.select_scan_dir)
        self.config.clicked.connect(self.open_config)
        self.last_task.clicked.connect(self.open_last_task)
        self.submit.clicked.connect(self.start_thread)
        self.thread = WorkerThread(None, debug)
        self.thread.task_finished.connect(self.task_finished)

    def center(self):
        # 获得屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获得窗口坐标系
        size = self.geometry()
        # 获得窗口相关坐标
        newLeft = (screen.width() - size.width()) // 2 + 700
        newTop = (screen.height() - size.height()) // 2
        # 移动窗口使其居中
        self.move(newLeft, newTop)

    def select_scan_dir(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        print("选择的文件夹路径：" + folder_path)
        self.thread.scan_dir = folder_path

    def open_config(self):
        os.startfile('config.yaml')

    def open_last_task(self):
        if self.thread.task_dir:
            os.startfile(self.thread.task_dir)
        else:
            msgBox(0, "提示", f"没有运行任务！")

    def start_thread(self):
        self.setEnabled(False)
        self.thread.start()

    def task_finished(self, result):
        self.setEnabled(True)
        msgBox(*result)


if __name__ == '__main__':
    pass
