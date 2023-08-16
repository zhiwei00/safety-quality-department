import os
import sys
import threading
import time
import winreg
from traceback import print_exc
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QDesktopWidget, QFileDialog, QMessageBox


# from verificationTime import VerificationTime
# from storehouse import CommercialContractGenerate, msgBox, handle_documents
def msgBox(box_type: int, box_title: str, box_text: str):
    time.sleep(0.1)
    # 创建 QMessageBox 对象
    msg_box = QMessageBox()
    msg_box.setWindowTitle("提示")
    msg_box.setText("这是一个置顶的提示窗口。")
    msg_box.setIcon(QMessageBox.Information)
    # 设置窗口标志，使其总是置顶
    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
    # 显示提示窗口
    msg_box.exec()


class MyQMainWindow(QtWidgets.QWidget):
    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)

        def Thread():
            for i in reversed(range(0, 11)):
                self.setWindowOpacity(i / 10)
                time.sleep(0.03)
            sys.exit()

        Thread = threading.Thread(target=Thread)
        Thread.start()


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
        self.source = QtWidgets.QPushButton(MainWindow)
        self.source.setObjectName("source")
        self.reset = QtWidgets.QPushButton(MainWindow)
        self.reset.setObjectName("reset")
        self.rule = QtWidgets.QPushButton(MainWindow)
        self.rule.setObjectName("open")
        self.template = QtWidgets.QPushButton(MainWindow)
        self.template.setObjectName("template")
        self.submit = QtWidgets.QPushButton(MainWindow)
        self.submit.setObjectName("submit")
        self.doc = QtWidgets.QPushButton(MainWindow)
        self.doc.setObjectName("doc")
        self.copy = QtWidgets.QPushButton(MainWindow)
        self.copy.setObjectName("copy")

        btLayout.addWidget(self.scan)
        btLayout.addWidget(self.source)
        btLayout.addWidget(self.reset)
        btLayout.addWidget(self.rule)
        btLayout.addWidget(self.template)
        btLayout.addWidget(self.submit)
        btLayout.addWidget(self.doc)
        btLayout.addWidget(self.copy)

        MainWindow.setLayout(btLayout)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "RPA小工具"))
        self.scan.setText(_translate("MainWindow", "选择扫描文件夹"))
        self.source.setText(_translate("MainWindow", "生成源数据"))
        self.reset.setText(_translate("MainWindow", "生成模板表"))
        self.rule.setText(_translate("MainWindow", "打开规则表"))
        self.template.setText(_translate("MainWindow", "打开模板表"))
        self.submit.setText(_translate("MainWindow", "执行"))
        self.doc.setText(_translate("MainWindow", "打开Word文件夹"))
        self.copy.setText(_translate("MainWindow", "批量复制"))


class Main(MyQMainWindow, Ui_MainWindow):
    switch_window = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.setupUi(self)
        self.scan_dir = None
        self.scan.clicked.connect(self.select_folder)
        # self.source.clicked.connect(self.create_source)
        # self.reset.clicked.connect(self.create_template)
        # self.template.clicked.connect(lambda: self.open_excel(0))
        # self.rule.clicked.connect(lambda: self.open_excel(1))
        # self.submit.clicked.connect(self.task_run)
        # self.doc.clicked.connect(lambda: self.open_dir(self.doc_path))
        # self.copy.clicked.connect(self.bulk_copy)
        self.center()

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
        self.scan_dir = folder_path

    def create_source(self):
        self.setEnabled(False)

        def Task():
            try:
                is_success, result = self.commercialContractGenerate.update_pdf_data()
                # print(len(self.commercialContractGenerate.pdf_json_data))
                if is_success:
                    return msgBox(0, "PDF数据", f"DPF数据识别完成")
                elif is_success and result:
                    return msgBox(1, "PDF数据", f"DPF数据识别中出现部分错误\n{result}")
                else:
                    return msgBox(2, "PDF数据", f"PDF数据识别失败\n{result}")
            except Exception as e:
                msgBox(2, "PDF数据", f"DPF数据识别失败，错误为：{e}")
            finally:
                self.setEnabled(True)

        Thread = threading.Thread(target=Task)
        Thread.start()

    def create_template(self):
        self.commercialContractGenerate.create_excel()

    def open_excel(self, is_rule: int):
        self.commercialContractGenerate.open_excel(is_rule)

    def open_dir(self, dir_name):
        if os.path.exists(dir_name):
            os.startfile(dir_name)
        else:
            self.commercialContractGenerate.open_dir(dir_name)

    def task_run(self):
        self.setEnabled(False)

        def Task():
            try:
                rule_data = self.commercialContractGenerate.get_excel_data(1)
                if not rule_data:
                    return msgBox(1, "配置表", f"规则表为空")
                print(rule_data)
                template_data = self.commercialContractGenerate.get_excel_data(0)
                if not template_data:
                    return msgBox(1, "配置表", f"模板表为空")
                print(template_data)
                print(111)
                is_success, handle_data = self.commercialContractGenerate.handle_center(template_data, rule_data)
                if is_success:
                    self.doc_path = handle_data
                    return msgBox(0, "执行", f"执行成功，文件生成在{handle_data}目录下")
                else:
                    return msgBox(2, "执行", f"执行失败，错误为：{handle_data}")
            except Exception as e:
                print_exc()
                msgBox(2, "执行", f"执行失败，错误为：{e}")

            finally:
                self.setEnabled(True)

        Thread = threading.Thread(target=Task)
        Thread.start()

    def bulk_copy(self):
        dir_choose = QFileDialog.getExistingDirectory(self, "选取文件夹",
                                                      os.path.dirname(os.path.realpath(sys.argv[0])))
        if os.path.exists(dir_choose):
            old_list, new_list = self.commercialContractGenerate.get_file_path(dir_choose)
            # handle_documents(old_list, new_list)
            time.sleep(0.2)
            msgBox(0, "复制", "批量复制完成")
            self.commercialContractGenerate.open_dir("copy")
        else:
            msgBox(1, "文件夹", "文件路径读取错误")


if __name__ == '__main__':
    # verify_result = VerificationTime.verification()
    verify_result = False
    app = QApplication(sys.argv)
    if not verify_result:
        buyUi = Main()
        buyUi.show()
    else:
        # MyMsg.QMessageBox(QMessageBox.Warning, '警告', '系统已经过了试用期,请联系管理员', True)
        pass
    sys.exit(app.exec_())
