from PyQt5.QtWidgets import QWidget, QApplication, QGroupBox, QHBoxLayout, QLineEdit, QLayout
from PyQt5 import uic
from PyQt5.QtCore import QThread, QObject, pyqtSignal, QSize
import sys
import time
from pyModbusTCP.client import ModbusClient
import random
import re
import json





class GraficUI(QWidget):
    count = 0
    threads = []
    workers = []
    last_updates = []

    def __init__(self):
        QWidget.__init__(self)
        self.setUI()
        self.data = []

    def setUI(self):
        self.UI = uic.loadUi("UITest.ui")
        self.UI.pushButton.clicked.connect(self.click_btn)
        self.UI.pushButton_2.clicked.connect(self.btn1)
        self.UI.pushButton_3.clicked.connect(lambda: self.update_par("USO3_1",))
        self.UI.pushButton_4.clicked.connect(self.take_data)
        self.UI.pushButton_5.clicked.connect(self.deactivate)
        self.UI.pushButton_6.clicked.connect(self.activate)
        self.UI.pushButton_8.clicked.connect(lambda: self.click_btn1("USO3_1"))
        self.scroll_widget()
        self.UI.show()
        self.UI.pushButton_4.setEnabled(False)


    def get_info(self, USO_name: str):
        pass





    def scroll_widget(self, USO: str = "USO3_1", type_signal: str = "AI"):
        data = _ADR_DATA[USO][type_signal]
        data_modbus = self.preparation_data(USO, "UI")
        for i in range(data[0]):
            params_in_line = [USO, type_signal, data[i+1]["name"], str(data_modbus[data[i+1]["adress"]])]
            print(params_in_line)
            groupBox = QGroupBox(self.UI.scrollAreaWidgetContents)
            groupBox.setTitle("")
            groupBox.setObjectName("groupBox_n{}".format(i))
            horizontalLayout = QHBoxLayout(groupBox)
            horizontalLayout.setSizeConstraint(QLayout.SetMinimumSize)
            horizontalLayout.setContentsMargins(5, 5, 5, 5)
            horizontalLayout.setSpacing(5)
            horizontalLayout.setObjectName("horizontalLayout_n{}".format(i))
            for j in range(4):
                line = QLineEdit(groupBox)
                line.setReadOnly(True)
                if j != 2:
                    line.setMaximumSize(QSize(50, 20))
                if j == 3:
                    line.setMaximumSize(QSize(70, 20))
                    line.setReadOnly(False)
                line.setObjectName("lineEdit_n{}".format(i))
                line.setText(params_in_line[j])
                line.returnPressed.connect(lambda: self.insert_data(USO, type_signal,self.sender().text(), self.sender().objectName()))
                #line.textChanged[str].connect(lambda: self.insert_data(USO, type_signal, i))
                horizontalLayout.addWidget(line)
            self.UI.verticalLayout.addWidget(groupBox)

    # def last_update(self, text="12", name="ewr"):
    #     print(text, name)
    #     text = text.replace(",", ".")
    #     self.last_updates.clear()
    #     self.last_updates.append(text)

    #lambda: self.insert_data(USO, type_signal, i)
    def insert_data(self, USO: str,type_signal: str, par_for_wtite:str, obj_name: str):
        par_num = int(obj_name.split("_n")[1])
        print(self.last_updates, par_num)
        adr = _ADR_DATA[USO][type_signal][par_num+1]['adress']
        Modbas_data.modbas_data[USO][adr//2] = Parameter_proc.anpar_to_write(int(par_for_wtite))
        Workers.need_update = True
        print(Modbas_data.modbas_data[USO], Workers.need_update)


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
        print(Workers.status)
        self.UI.lcdNumber.display(self.count)

    def deactivate(self):
        Workers.status = False
        self.UI.pushButton_2.setEnabled(True)

    def activate(self):
        Workers.status = True


    def click_btn1(self, USO: str):
        print(USO)
        params, modbus_zone, address = self.preparation_data(USO)
        print(modbus_zone)
        print('==========1')
        obj = Workers()
       # print(obj)
        t = QThread()
        self.workers.append(obj)
        print('------------------2')
        self.threads.append(t)
        print('------------------')
        obj = self.workers[-1]
        t = self.threads[-1]
        print('==========')
        obj.data_read = modbus_zone[0]
        obj.data_write = modbus_zone[1]
        obj.USO_name = USO
        obj.work = obj
        obj.thread = t
        print("ooooooooooo")
        obj.addr = address
        obj.moveToThread(t)
        t.started.connect(obj.start)
        obj.finishSignal.connect(t.quit)
        obj.finishSignal.connect(lambda: self.UI.pushButton_8.setEnabled(False))
        t.start()
    #
    #
    #
    #     #obj.finishSignal.connect(lambda: self.UI.pushButton_3.setEnabled(True))
    #     #obj.read.connect(self.outSignal)
    #     #obj.write.connect(self.outSignal)




    def outSignal(self, res):
        self.UI.lineEdit.setText(str(res))


    def take_data(self):
        text_data = self.UI.lineEdit_2.text()
        data = re.findall('\d+', text_data)
        Workers.data = list(map(lambda x: int(x), data)) if len(data) > 0 else [0]

    @classmethod
    def preparation_data(cls, USO_name: str, flug:str = "beck", type_param: str = "all") -> list:
        data = _ADR_DATA[USO_name]
        data_AI = data["AI"]
        data_DI = data["DI"]
        data_AO = data["AO"]
        data_DO = data["DO"]
        max_in_param = max(data["MaxAddrAI"], data["MaxAddrDI"])
        max_out_param = max(data["MaxAddrAO"], data["MaxAddrDO"])
        in_zone_data = [0 for i in range(max_in_param)]
        out_zone_data = [0 for i in range(max_out_param)]
        Modbas_data.modbas_data[USO_name] = in_zone_data
        address = data['Address']
        if flug == 'UI':
            return in_zone_data
        if flug == "beck":
            pass
        return [data_AI, data_DI, data_AO, data_DO], [in_zone_data, out_zone_data], address

    @classmethod
    def update_par(self, par_name: str):
        pass

class Workers(QObject):
    finishSignal = pyqtSignal()
    timer = pyqtSignal()
    read = pyqtSignal(list)
    write = pyqtSignal(list)
    data = []
    status = True
    need_update = False
    def __init__(self):
        super(Workers, self).__init__()
        self.work = 0
        self.thread = 0
        self.USO_name = ''
        self.addr = "0"
        self.data_write = 0
        self.data_read = 0

        self.repeat = False
        self.random_data = False

    def start(self):
        self.client = ModbusClient(debug=False, auto_open=True, host=self.addr)
        print("1")
        while self.status:
            for operation in ["read", "write"]:
                if operation == "read":
                    pass
                    #read = self.client.read_holding_registers(0, len(self.data_write))
                    #print(read)
                    #self.read.emit(read)
                else:
                    if self.need_update:
                        print("=====================================================================")
                        self.data_read = Modbas_data.modbas_data[self.USO_name]
                        self.need_update = False
                        print(self.data_read)
                    if len(self.data_read) > 122:
                        print("++")
                        self.client.write_multiple_registers(0, self.data_read[0:100])
                        self.client.write_multiple_registers(100, self.data_read[100::])
                    elif len(self.data_read) < 122:
                        print("-+-")
                        print(self.data_read)
                        self.client.write_multiple_registers(0, self.data_read)
                        print("00000")
                    #self.status = self.repeat and Workers.status
                    #print(self.data_read)
            # if self.need_update == True:
            #     print("-----------------------------------------------------------------------------------")
            #     self.data_read = Modbas_data.modbas_data(self.name)
            #     print(self.data_read)
                #self.write.emit(write)
            time.sleep(1)
        self.finishSignal.emit()

        GraficUI.threads.pop(GraficUI.threads.index(self.thread))
        GraficUI.workers.pop(GraficUI.workers.index(self.work))

class Modbas_data():
    modbas_data = {}

class Parameter_proc():
    @classmethod
    def anpar_to_write(cls, dec):
        hex = str(format(dec*1000, 'x')).rjust(4, "0")
        hex_swap = hex[2::]+hex[0:2]
        hex_swap = int(hex_swap, 16)
        return hex_swap

    @classmethod
    def descr_to_write(cls, USO: str, par_num: int, bit: int):
         in_zone_data = Modbas_data.modbas_data(USO)






if __name__ == "__main__":
    json_file = open("Addr_reg.json", encoding="utf-8").read()
    _ADR_DATA = json.loads(json_file)
    app = QApplication(sys.argv)
    window = GraficUI()
    sys.exit(app.exec())