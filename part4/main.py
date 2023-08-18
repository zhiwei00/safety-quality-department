import sys
from PyQt5.QtWidgets import QApplication
from src.ui import Main
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
