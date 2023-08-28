import sys
import typer
from PyQt5.QtWidgets import QApplication
from .ui import Main, msgBox
from .verification_time import VerificationTime

Application = typer.Typer()


@Application.command()
def run(debug=0):
    verify_result = VerificationTime.verification('2023-10-01 00:00:00')
    app = QApplication(sys.argv)
    if verify_result:
        buyUi = Main(int(debug))
        buyUi.show()
    else:
        msgBox(1, '警告', '系统已经过了试用期,请联系管理员')
        exit(0)
    sys.exit(app.exec_())
