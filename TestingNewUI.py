from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QGroupBox, QHBoxLayout, QLineEdit, QLayout, QPushButton
from PyQt5 import uic
from PyQt5.QtCore import QThread, QObject, pyqtSignal, QSize, QRect, QStringListModel
from PyQt5.QtGui import QIcon
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
    link_for_read = []
    USO_in_window = []

    def __init__(self):
        QWidget.__init__(self)
        self.setUI()
        self.data = []


    def setUI(self):
        self.UI = uic.loadUi("UITest.ui")
        self.used_USO = "USO3_1"
        self.UI.pushButton.clicked.connect(self.click_btn)
        self.UI.pushButton_2.clicked.connect(self.btn1)
        self.UI.pushButton_3.clicked.connect(lambda: self.update_par("USO3_1",))
        #self.UI.pushButton_4.clicked.connect(self.take_data)
        self.UI.pushButton_5.clicked.connect(self.deactivate)
        self.UI.pushButton_6.clicked.connect(self.activate)
        self.UI.pushButton_8.clicked.connect(lambda: self.click_btn1("SAR_1"))
        self.scroll_widget()
        self.scroll_widget_USO()
        self.UI.show()
        self.UI.pushButton_4.setEnabled(False)
        self.UI.pushButton_9.clicked.connect(lambda: self.get_object_name(self.sender()))
        self.UI.pushButton_9.setObjectName("pushButton_AI")
        self.UI.pushButton_10.clicked.connect(lambda: self.get_object_name(self.sender()))
        self.UI.pushButton_10.setObjectName("pushButton_DI")
        self.UI.pushButton_11.clicked.connect(lambda: self.get_object_name(self.sender()))
        self.UI.pushButton_11.setObjectName("pushButton_AO")
        self.UI.pushButton_12.clicked.connect(lambda: self.get_object_name(self.sender()))
        self.UI.pushButton_12.setObjectName("pushButton_DO")


    def scroll_widget_USO(self):
        USO_list = _ADR_DATA.keys()
        for USO in USO_list:
            btn = QPushButton(self.UI.scrollAreaWidgetContents_2)
            btn.setObjectName(USO)
            btn.setText(USO)
            btn.setMaximumSize(QSize(60, 20))
            btn.clicked.connect(lambda: self.scroll_widget(self.sender().objectName()))
            self.UI.verticalLayout_2.addWidget(btn)
        self.UI.scrollArea_2.setWidget(self.UI.scrollAreaWidgetContents_2)


    def get_object_name(self, obj):
        name = obj.objectName()
        _ = name.split("_")
        self.scroll_widget(self.used_USO,type_signal = _[1])


    def scroll_widget(self, USO: str = "USO3_1", type_signal: str = "DI"):
        self.used_USO = USO
        self.USO_in_window.clear()
        self.USO_in_window.append(USO)
        self.link_for_read.clear()
        self.UI.scrollAreaWidgetContents.deleteLater()
        self.UI.scrollAreaWidgetContents = QWidget()
        self.UI.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 979, 379))
        self.UI.scrollAreaWidgetContents.setMinimumSize(QSize(889, 0))
        self.UI.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.UI.verticalLayout = QVBoxLayout(self.UI.scrollAreaWidgetContents)
        self.UI.verticalLayout.setObjectName("verticalLayout")

        data = _ADR_DATA[USO][type_signal]
        #data_modbus = Modbas_data.modbas_data[USO]
        data_modbus_UI = Modbas_data.modbus_data_UI[USO]

        for i in range(data[0]):
            groupBox = QGroupBox(self.UI.scrollAreaWidgetContents)
            groupBox.setTitle("")
            groupBox.setObjectName("groupBox_n{}".format(i))
            horizontalLayout = QHBoxLayout(groupBox)
            horizontalLayout.setSizeConstraint(QLayout.SetMinimumSize)
            horizontalLayout.setContentsMargins(5, 5, 5, 5)
            horizontalLayout.setSpacing(5)
            horizontalLayout.setObjectName("horizontalLayout_n{}".format(i))
            if type_signal in ["AO", "AI"]:
                params_in_line = [USO, type_signal, data[i + 1]["name"], str(data_modbus_UI[data[i + 1]["adress"]//2])]
                for j in range(4):
                    line = QLineEdit(groupBox)
                    line.setReadOnly(True)
                    if j != 2:
                        line.setMaximumSize(QSize(50, 20))
                    if j == 3:
                        line.setMaximumSize(QSize(70, 20))
                        if type_signal == "AO":
                            line.setReadOnly(True)
                        else:
                            line.setReadOnly(False)
                    line.setObjectName("lineEdit_n{}".format(i))
                    line.setText(params_in_line[j])
                    if type_signal == "AI" and j == 3:
                        line.returnPressed.connect(lambda: self.insert_data(USO, type_signal, self.sender().text(), self.sender().objectName()))
                    if type_signal == "AO" and j == 3:
                        self.link_for_read.append(line)
                    horizontalLayout.addWidget(line)
                self.UI.verticalLayout.addWidget(groupBox)
            if type_signal in ["DO", "DI"]:
                bit = data_modbus_UI[data[i + 1]["adress"]//2][data[i + 1]["adress"]&1][data[i + 1]["bit"]]
                descr_in_line = [USO, type_signal, data[i + 1]["name"], bit]
                for j in range(3):
                    line = QLineEdit(groupBox)
                    line.setReadOnly(True)
                    if j != 2:
                        line.setMaximumSize(QSize(50, 20))
                    if j == 3:
                        line.setMaximumSize(QSize(70, 20))
                        line.setReadOnly(False)
                    line.setObjectName("lineEdit_n{}".format(i))
                    line.setText(descr_in_line[j])
                    line.returnPressed.connect(lambda: self.insert_data(USO, type_signal,self.sender().text(), self.sender().objectName()))
                    horizontalLayout.addWidget(line)
                btn = QPushButton(groupBox)
                btn.setIconSize(QSize(58, 30))
                btn.setMaximumSize(QSize(58, 30))
                if bit == 1:
                    btn.setObjectName("pushButton_1_n{}".format(i))
                    btn.setIcon(QIcon('ON.png'))
                if bit == 0:
                    btn.setObjectName("pushButton_0_n{}".format(i))
                    btn.setIcon(QIcon('OFF.png'))
                if type_signal == "DI":
                    btn.clicked.connect(lambda: self.state_btn(self.sender()))
                    btn.clicked.connect(lambda: self.insert_data(USO, type_signal, obj_name = self.sender().objectName()))
                horizontalLayout.addWidget(btn)
                self.UI.verticalLayout.addWidget(groupBox)
            self.UI.scrollArea.setWidget(self.UI.scrollAreaWidgetContents)

    def state_btn(self, obj):
        print(obj.objectName())
        if "_1" in obj.objectName():
            _ = obj.objectName().split("_1")
            new_name = _[0]+"_0"+_[1]
            obj.setObjectName(new_name)
            print("new_name", new_name)
            obj.setIcon(QIcon('OFF.png'))
        else:
            _ = obj.objectName().split("_0")
            new_name = _[0] + "_1" + _[1]
            obj.setObjectName(new_name)
            print("new_name", new_name)
            obj.setIcon(QIcon('ON.png'))



    def insert_data(self, USO: str,type_signal: str, par_for_wtite:str = '', obj_name: str = ""):
        par_num = int(obj_name.split("_n")[1])
        param = _ADR_DATA[USO][type_signal][par_num+1]
        if type_signal == "AI":
            Modbas_data.modbas_data[USO][param['adress']//2] = Modbas_data.anpar_to_write(int(par_for_wtite))
            Modbas_data.modbus_data_UI[USO][param['adress']//2] = int(par_for_wtite)
        else:
            print("]]]]]]")
            Modbas_data.modbas_data[USO][param['adress']// 2] = Modbas_data.descr_to_write(USO,par_num,param['adress'], param['bit'])
            param_addr_modbus = Modbas_data.modbus_data_UI[USO][param['adress'] // 2]
            if param["adress"] & 1 == 1:
                if param_addr_modbus[1][param['bit']] == 0:
                    param_addr_modbus[1][param['bit']] = 1
                else:
                    param_addr_modbus[1][param['bit']] = 0
            else:
                if param_addr_modbus[0][param['bit']] == 0:
                    param_addr_modbus[0][param['bit']] = 1
                else:
                    param_addr_modbus[0][param['bit']] = 0
        Workers.need_update = True
        print(Modbas_data.modbas_data[USO],"конец функции")
        print(Modbas_data.modbus_data_UI[USO],"конец функции")



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
        obj = Workers()
        t = QThread()
        self.workers.append(obj)
        self.threads.append(t)
        obj = self.workers[-1]
        t = self.threads[-1]
        obj.data_read = Modbas_data.modbas_data[USO]
        obj.data_write = Modbas_data.modbas_data[USO+"out"]
        obj.USO_name = USO
        obj.work = obj
        obj.thread = t
        obj.addr = Modbas_data.modbas_addr[USO]
        obj.moveToThread(t)
        t.started.connect(obj.start)
        obj.finishSignal.connect(t.quit)
        obj.finishSignal.connect(lambda: self.UI.pushButton_8.setEnabled(False))
        obj.read.connect(self.update_par)
        t.start()
    #
    #
    #
    #     #obj.finishSignal.connect(lambda: self.UI.pushButton_3.setEnabled(True))
    #     #obj.read.connect(self.outSignal)
    #     #obj.write.connect(self.outSignal)




    def take_data(self):
        text_data = self.UI.lineEdit_2.text()
        data = re.findall('\d+', text_data)
        Workers.data = list(map(lambda x: int(x), data)) if len(data) > 0 else [0]


    @classmethod
    def update_par(cls, name: str):
        print("++++++++++++++++++++++++++++")
        if name == cls.USO_in_window[0] and len(cls.link_for_read) > 0:
            params_AO = _ADR_DATA[name]['AO']
            for i in range(0, params_AO[0]):
                cls.link_for_read[i].setText(Modbas_data.anpar_to_UI(Modbas_data.modbas_data[name + "out"][params_AO[i+1]['adress'] // 2]))



class Workers(QObject):
    finishSignal = pyqtSignal()
    timer = pyqtSignal()
    read = pyqtSignal(str)
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
                    read = self.client.read_holding_registers(0, len(self.data_write))
                    Modbas_data.modbas_data[self.USO_name+"out"] = read
                    print(read)
                    self.read.emit(self.USO_name)
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
                        #print ("-+-")
                        #print(self.data_read)
                        self.client.write_multiple_registers(0, self.data_read)
                        #print("00000")
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
    modbas_addr = {}
    modbus_data_UI ={}

    def __init__(self, _ADR_DATA):
        self.modbas_data = self.create_modbus_zone(_ADR_DATA)

    def create_modbus_zone(self, full_data: dict):
        for USO in full_data.keys():
            data = _ADR_DATA[USO]
            max_in_param = max(data["MaxAddrAI"], data["MaxAddrDI"])
            max_out_param = max(data["MaxAddrAO"], data["MaxAddrDO"])
            in_zone_data = [0 for i in range(max_in_param+1)]
            out_zone_data = [0 for i in range(max_out_param+1)]
            in_zone_data_UI = [0 for i in range(max_in_param+1)]
            print(USO, len(in_zone_data_UI))
            for descr in range(1, data["DI"][0]):
                in_zone_data_UI[data["DI"][descr]['adress']//2] = [[0 for i in range(8)], [0 for i in range(8)]]
            self.modbas_data[USO] = in_zone_data
            self.modbas_data[USO+"out"] = out_zone_data
            self.modbus_data_UI[USO] = in_zone_data_UI
            self.modbas_addr[USO] = data['Address']


    @classmethod
    def anpar_to_write(cls, dec):
        _hex = str(format(dec*1000, 'x')).rjust(4, "0")
        print(_hex)
        hex_swap = _hex[2::]+_hex[0:2]
        hex_swap = int(hex_swap, 16)
        return hex_swap

    @classmethod
    def anpar_to_UI(cls, dec):
        _hex = format(dec, 'x')
        hex_swap = _hex[2::] + _hex[0:2]
        mA = int(hex_swap, 16) // 1000
        return str(mA)

    @classmethod
    def descr_to_write(cls, USO: str, par_num:int, registr: int, bit: int):
        if registr & 1 == 1:
            bit = bit + 8
            registr -= 1
        descr = Modbas_data.modbas_data[USO][registr//2]
        print(descr,par_num, "------------------4514514--------------------")
        print(Modbas_data.modbas_data[USO], "вх зона")
        pred = bin(descr)[2:].rjust(16, "0")
        print(pred, "pred start")
        if pred[-bit - 1] == "1":
            pred = pred[0:15 - bit] + "0" + pred[14 - bit + 2::]
            return int(pred, 2)
        else:
            pred = pred[0:15 - bit] + "1" + pred[14 - bit + 2::]
            print(pred, "pred stop")
            return int(pred, 2)


if __name__ == "__main__":
    json_file = open("Addr_reg.json", encoding="utf-8").read()
    _ADR_DATA = json.loads(json_file)
    app = QApplication(sys.argv)
    Modbas_data(_ADR_DATA)
    # print(Modbas_data.modbus_data_UI["USO3_1"])
    # print(len(Modbas_data.modbus_data_UI["USO3_1"][10]))
    window = GraficUI()
    sys.exit(app.exec())