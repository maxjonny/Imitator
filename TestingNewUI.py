from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5 import uic
from PyQt5.QtCore import QThread, QObject, pyqtSignal
import sys
import time


class Workers(QObject):
    finishSignal = pyqtSignal()
    timer = pyqtSignal(int)
    def __init__(self):
        super(Workers, self).__init__()

    def start(self):
        print("старт")
        for i in range(10):
            self.timer.emit(i)
            time.sleep(1)
        self.finishSignal.emit()
        # self.UI.lineEdit.setText("Ok")
        # self.finishSignal.emit()








class GraficUI(QWidget):
    count = 0
    def __init__(self):
        QWidget.__init__(self)
        self.setUI()

    def setUI(self):
        self.UI = uic.loadUi("UITest.ui")
        self.UI.pushButton.clicked.connect(self.click_btn)
        self.UI.pushButton_2.clicked.connect(self.click_btn1)
        self.UI.pushButton_3.clicked.connect(self.click_btn2)
        self.UI.show()



    def click_btn(self):
        self.count += 1
        self.UI.lcdNumber.display(self.count)


    def click_btn1(self):
        self.obj = Workers()
        self.t = QThread()
        self.obj.moveToThread(self.t)
        self.t.started.connect(self.obj.start)
        print("----")
        self.obj.finishSignal.connect(self.t.quit)
        self.obj.timer.connect(self.outSignal)
        self.t.start()


    def outSignal(self, res):
        self.UI.lineEdit.setText(str(res))


    def click_btn2(self):
        self.UI.lineEdit_2.setText("Работаю")
        time.sleep(5)
        self.UI.lineEdit_2.setText("Ok")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraficUI()
    sys.exit(app.exec())