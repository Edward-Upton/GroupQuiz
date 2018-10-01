import sys

import mido
import mido
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QStyleFactory
from math import floor
from Ui_lighting_control import Ui_MainWindow

APP = QApplication([])
APP.setStyle(QStyleFactory.create('GTK+'))
WINDOW = QMainWindow()
UI = Ui_MainWindow()
UI.setupUi(WINDOW)

class LightingDesk:

    def __init__(self):
        ports = mido.get_output_names()
        print(ports[-1])
        self.outport = mido.open_output(name=ports[-1])

#   reference for midi code that will work
#   https://spotlightkid.github.io/python-rtmidi/rtmidi.html
    def updateLight(self, slider_name):
        slider_letter, slider_number = slider_name.split('_')[1], slider_name.split('_')[2]
        slider_object = getattr(UI, slider_name)
        slider_number = int(slider_number)
        value = slider_object.value()
        msg = None
        if slider_letter == "a":
            msg = mido.Message("control_change", control=(slider_number-1), value=value, time=1)
        elif slider_letter == "b":
            msg = mido.Message("control_change", control=(slider_number+11), value=value, time=1)
        print(str(msg))
        self.outport.send(msg)

DESK = LightingDesk()

class Sequencer:

    def __init__(self):
        self.sequence = []
        self.play_step = 0
        self.loop_step = 0
        self.loop_count = 0
        self.timer = QtCore.QTimer()
        self.loop_timer = QtCore.QTimer()

        step = {}
        step["fade_time"] = 5
        step["hold_time"] = 0.1
        for slider in range(1, 13):
            slider_object = getattr(UI, "verticalSlider_a_"+str(slider))
            step["verticalSlider_a_"+str(slider)] = slider_object.value()
        for slider in range(1, 13):
            slider_object = getattr(UI, "verticalSlider_b_"+str(slider))
            step["verticalSlider_b_"+str(slider)] = slider_object.value()
        self.sequence.append(step)
        UI.listWidget.setCurrentRow(0)


    def add_step(self):
        step = {}
        step["fade_time"] = UI.doubleSpinBox_fadetime.value()
        step["hold_time"] = UI.doubleSpinBox_holdtime.value()
        for slider in range(1, 13):
            slider_object = getattr(UI, "verticalSlider_a_"+str(slider))
            step["verticalSlider_a_"+str(slider)] = slider_object.value()
        for slider in range(1, 13):
            slider_object = getattr(UI, "verticalSlider_b_"+str(slider))
            step["verticalSlider_b_"+str(slider)] = slider_object.value()

        new_step = QtWidgets.QListWidgetItem()
        new_step.setText(str(UI.listWidget.count()+1))
        UI.listWidget.addItem(new_step)
        self.sequence.append(step)
        UI.listWidget.setCurrentRow(len(self.sequence)-1)

    def delete_step(self):
        if not self.sequence:
            return

        row = UI.listWidget.currentRow()
        del self.sequence[row]
        UI.listWidget.takeItem(row)
        for step in range(len(self.sequence)):
            UI.listWidget.item(step).setText(str(step+1))

    def click_step(self, item_clicked):
        row = UI.listWidget.currentRow()
        step = self.sequence[row]
        for slider in range(1, 13):
            slider_object = getattr(UI, "verticalSlider_a_"+str(slider))
            slider_object.setValue(step["verticalSlider_a_"+str(slider)])
        for slider in range(1, 13):
            slider_object = getattr(UI, "verticalSlider_b_"+str(slider))
            slider_object.setValue(step["verticalSlider_b_"+str(slider)])
        UI.doubleSpinBox_fadetime.setValue(step["fade_time"])
        UI.doubleSpinBox_holdtime.setValue(step["hold_time"])

class SequenceThread(QtCore.QThread):
    def __init__(self, sequencer: Sequencer):
        QtCore.QThread.__init__(self)
        self.sequencer = sequencer
        self.sequence = self.sequencer.sequence

    def run(self):
        for index, step in enumerate(self.sequence):
            for update in range(0, int(step["time"]*10), 1):
                for slider in range(1, 13):
                    slider_object_a = getattr(UI, "verticalSlider_a_"+str(slider))
                    slider_object_b = getattr(UI, "verticalSlider_b_"+str(slider))
                    if index:
                        begin_a = step["verticalSlider_a_"+str(slider)]
                        begin_b = step["verticalSlider_b_"+str(slider)]
                    else:
                        begin_a = 0
                        begin_b = 0

                    if index >= len(self.sequence)-1:
                        break
                    else:
                        end_a = self.sequence[index+1]["verticalSlider_a_"+str(slider)]
                        end_b = self.sequence[index+1]["verticalSlider_b_"+str(slider)]

                    gradient_a = (end_a-begin_a)/step["fade_time"]
                    gradient_b = (end_b-begin_b)/step["fade_time"]
                    change_value_a = int(floor((gradient_a*update*0.1)+begin_a))
                    change_value_b = int(floor((gradient_b*update*0.1)+begin_b))
                    slider_object_a.setValue(change_value_a)
                    slider_object_b.setValue(change_value_b)
                self.msleep(100)
        self.msleep(step["hold_time"]*1000)

SEQUENCE = Sequencer()

SEQUENCE_THREAD = SequenceThread(SEQUENCE)


def toggle_play(thread):
    if UI.pushButton_main_sequencerplay.isChecked():
        thread = SequenceThread(SEQUENCE)
        thread.start()
    else:
        thread.terminate()
        del thread

UI.pushButton_main_sequencerplay.clicked.connect(lambda: toggle_play(SEQUENCE_THREAD))

UI.pushButton_addStep.clicked.connect(SEQUENCE.add_step)
UI.pushButton_deleteStep.clicked.connect(SEQUENCE.delete_step)
UI.listWidget.itemClicked.connect(SEQUENCE.click_step)

UI.verticalSlider_a_1.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_a_1"))
UI.verticalSlider_a_2.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_a_2"))
UI.verticalSlider_a_3.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_a_3"))
UI.verticalSlider_a_4.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_a_4"))
UI.verticalSlider_a_5.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_a_5"))
UI.verticalSlider_a_6.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_a_6"))
UI.verticalSlider_a_7.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_a_7"))
UI.verticalSlider_a_8.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_a_8"))
UI.verticalSlider_a_9.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_a_9"))
UI.verticalSlider_a_10.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_a_10"))
UI.verticalSlider_a_11.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_a_11"))
UI.verticalSlider_a_12.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_a_12"))
UI.verticalSlider_b_1.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_b_1"))
UI.verticalSlider_b_2.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_b_2"))
UI.verticalSlider_b_3.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_b_3"))
UI.verticalSlider_b_4.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_b_4"))
UI.verticalSlider_b_5.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_b_5"))
UI.verticalSlider_b_6.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_b_6"))
UI.verticalSlider_b_7.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_b_7"))
UI.verticalSlider_b_8.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_b_8"))
UI.verticalSlider_b_9.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_b_9"))
UI.verticalSlider_b_10.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_b_10"))
UI.verticalSlider_b_11.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_b_11"))
UI.verticalSlider_b_12.valueChanged.connect(lambda: DESK.updateLight("verticalSlider_b_12"))

WINDOW.show()
APP.exec_()
