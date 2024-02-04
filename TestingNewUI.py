from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5 import uic
from PyQt5.QtCore import QThread, QObject, pyqtSignal
import sys
import time
from pyModbusTCP.client import ModbusClient
import random
import re





class GraficUI(QWidget):
    count = 0
    threads =[]
    workers =[]

    def __init__(self):
        QWidget.__init__(self)
        self.setUI()
        self.data = []

    def setUI(self):
        self.UI = uic.loadUi("UITest.ui")
        self.UI.pushButton.clicked.connect(self.click_btn)
        self.UI.pushButton_2.clicked.connect(self.btn1)
        self.UI.pushButton_3.clicked.connect(self.btn2)
        self.UI.pushButton_4.clicked.connect(self.take_data)
        self.UI.show()
        self.UI.pushButton_4.setEnabled(False)



    def btn1(self):
        self.UI.pushButton_2.setEnabled(False)
        self.click_btn1("btn1")

    def btn2(self):
        self.take_data()
        self.UI.pushButton_3.setEnabled(False)
        self.click_btn1("btn2")


    def click_btn(self):
        self.count += 1
        print(Workers.data)
        print(self.threads)
        self.UI.lcdNumber.display(self.count)



    def click_btn1(self, btn):
        self.workers.append(Workers())
        self.threads.append(QThread())
        obj = self.workers[-1]
        t = self.threads[-1]
        obj.work = obj
        obj.thread = t
        obj.btn = btn
        obj.random_data = True if self.UI.checkBox_2.checkState() == 2 else False
        obj.repeat = True if self.UI.checkBox.checkState() == 2 else False
        if not self.UI.pushButton_3.isEnabled():
            self.UI.pushButton_4.setEnabled(True)
        #obj.data = self.data
        print("o")
        obj.moveToThread(t)
        t.started.connect(obj.start)
        print("----")
        obj.finishSignal.connect(t.quit)
        obj.finishSignal.connect(lambda: self.UI.pushButton_4.setEnabled(False))
        obj.finishSignal.connect(lambda: self.UI.pushButton_3.setEnabled(True))
        obj.read.connect(self.outSignal)
        #obj.write.connect(self.outSignal)
        t.start()
        print("====")


    def outSignal(self, res):
        self.UI.lineEdit.setText(str(res))


    def take_data(self):
        text_data = self.UI.lineEdit_2.text()
        data = re.findall('\d+', text_data)
        Workers.data = list(map(lambda x: int(x), data)) if len(data) > 0 else [0]

class Workers(QObject):
    finishSignal = pyqtSignal()
    timer = pyqtSignal()
    read = pyqtSignal(list)
    write = pyqtSignal(list)
    data = []
    def __init__(self):
        super(Workers, self).__init__()
        self.work = 0
        self.thread = 0
        self.btn = 0
        self.client = ModbusClient(debug=False, auto_open=True)
        self.repeat = False
        self.random_data = False
        self.status = True

    def start(self):
        while self.status:
            if self.btn == "btn1":
                read = self.client.read_holding_registers(1, 10)
                self.read.emit(read)
            else:
                if self.random_data:
                    self.data = [random.randint(0, 100) for i in range(10)]
                self.client.write_multiple_registers(1, self.data)
                self.status = self.repeat
                #self.write.emit(write)
            time.sleep(0.1)
        self.finishSignal.emit()

        GraficUI.threads.pop(GraficUI.threads.index(self.thread))
        GraficUI.workers.pop(GraficUI.workers.index(self.work))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraficUI()
    sys.exit(app.exec())