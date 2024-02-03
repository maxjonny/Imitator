from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5 import uic
from PyQt5.QtCore import QThread, QObject, pyqtSignal
import sys
import time





class GraficUI(QWidget):
    count = 0
    threads =[]
    workers =[]
    def __init__(self):
        QWidget.__init__(self)
        self.setUI()

    def setUI(self):
        self.UI = uic.loadUi("UITest.ui")
        self.UI.pushButton.clicked.connect(self.click_btn)
        self.UI.pushButton_2.clicked.connect(self.click_btn1)
        self.UI.pushButton_3.clicked.connect(self.click_btn1)
        self.UI.show()



    def click_btn(self):
        self.count += 1
        print(self.threads)
        self.UI.lcdNumber.display(self.count)


    def click_btn1(self):
        self.workers.append(Workers())
        self.threads.append(QThread())
        index_thread = len(self.threads)-1
        print(self.workers)
        obj = self.workers[-1]

        t = self.threads[-1]
        obj.work = obj
        obj.thread = t
        obj.moveToThread(t)
        t.started.connect(obj.start)
        print("----")
        obj.finishSignal.connect(t.quit)
        obj.timer.connect(self.outSignal)
        t.start()
        print("====")


    def outSignal(self, res):
        self.UI.lineEdit.setText(str(res))



    def click_btn2(self):
        self.UI.lineEdit_2.setText("Работаю")
        time.sleep(5)
        self.UI.lineEdit_2.setText("Ok")

class Workers(QObject):
    finishSignal = pyqtSignal()
    timer = pyqtSignal(int)
    status = pyqtSignal(bool)
    def __init__(self):
        super(Workers, self).__init__()
        self.work = 0
        self.thread = 0
    def start(self):
        self.status.emit(True)
        print("старт")
        for i in range(10):
            self.timer.emit(i)
            time.sleep(1)
        self.status.emit(False)
        self.finishSignal.emit()
        GraficUI.threads.pop(GraficUI.threads.index(self.thread))
        GraficUI.workers.pop(GraficUI.workers.index(self.work))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraficUI()
    sys.exit(app.exec())