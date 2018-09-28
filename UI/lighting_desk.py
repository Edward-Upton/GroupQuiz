import sys

import mido
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import CONTROL_CHANGE
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QStyleFactory

from Ui_lighting_control import Ui_MainWindow

APP = QApplication([])
APP.setStyle(QStyleFactory.create('GTK+'))
WINDOW = QMainWindow()
UI = Ui_MainWindow()
UI.setupUi(WINDOW)

class LightingDesk:

    #def __init__(self):
        #self.ports, self.port_name = open_midioutput(port_name="output")
        #self.output = self.ports[1]

#   reference for midi code that will work
#   https://spotlightkid.github.io/python-rtmidi/rtmidi.html
    def updateLight(self, slider_name):
        slider_letter, slider_number = slider_name.split('_')[1], slider_name.split('_')[2]
        slider_object = getattr(UI, "verticalSlider_"+slider_letter+"_"+slider_number)
        slider_number = int(slider_number)
        value = slider_object.value()
        if slider_letter == "a":
            pass
#            print("control_change ", slider_number-1, " value: ", value)
#            self.output.send_message([CONTROL_CHANGE, (slider_number-1), value])
        elif slider_letter == "b":
            pass
#            print("control_change ", slider_number+11, " value: ", value)
#            self.output.send_message([CONTROL_CHANGE, (slider_number+11), value])

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
        step["time"] = 5
        for slider in range(1, 13):
            slider_object = getattr(UI, "verticalSlider_a_"+str(slider))
            step["verticalSlider_a_"+str(slider)] = slider_object.value()
        for slider in range(1, 13):
            slider_object = getattr(UI, "verticalSlider_b_"+str(slider))
            step["verticalSlider_b_"+str(slider)] = slider_object.value()
        self.sequence.append(step)


    def add_step(self):
        step = {}
        step["time"] = 5
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

    def play_sequence(self):
        if not UI.pushButton_main_sequencerplay.isChecked():
            self.timer.stop()
            self.play_step = 0
            self.loop_step = 0
            self.loop_count = 0
            UI.pushButton_main_sequencerplay.toggle()
        else:
            UI.pushButton_main_sequencerplay.toggle()
            self.timer = QtCore.QTimer()
            for steps in range(len(self.sequence)):
                self.loop_step = 0
                fade_time = self.sequence[steps]["time"]
                self.loop_timer.timeout.connect(self.next_step)
                self.loop_timer.start(fade_time)


    def next_step(self):
        self.play_step = 0
        fade_time = self.sequence[self.loop_step]["time"]
        self.loop_count = int(fade_time / 0.1)
        self.timer.timeout.connect(lambda: self.animate_slider_step(self.loop_step))
        self.timer.start(100)
        self.loop_step += 1
        if self.loop_step >= len(self.sequence)-1:
            self.loop_timer.stop()


    def animate_slider_step(self, step):
        for slider in range(1, 13):
            slider_object = getattr(UI, "verticalSlider_a_"+str(slider))
            if step != 0:
                begin = self.sequence[step-1]["verticalSlider_a_"+str(slider)]
            else:
                begin = 0

            if step != len(self.sequence)-1:
                end = self.sequence[step]["verticalSlider_a_"+str(slider)]
            else:
                end = 0

            gradient = (end-begin)/self.sequence[step]["time"]
            change_value = int(gradient*(self.play_step*0.1) + begin)

            slider_object.setValue(change_value)


        for slider in range(1, 13):
            slider_object = getattr(UI, "verticalSlider_b_"+str(slider))
            if step != 0:
                begin = self.sequence[step-1]["verticalSlider_b_"+str(slider)]
            else:
                begin = 0

            if step != len(self.sequence)-1:
                end = self.sequence[step]["verticalSlider_b_"+str(slider)]
            else:
                end = 0

            gradient = (end-begin)/self.sequence[step]["time"]
            change_value = int(gradient*(self.play_step*0.1) + begin)

            slider_object.setValue(change_value)

        self.play_step += 1
        if self.play_step >= self.loop_count:
            self.timer.stop()


    def click_step(self, item_clicked):
        row = UI.listWidget.currentRow()
        step = self.sequence[row]
        for slider in range(1, 13):
            slider_object = getattr(UI, "verticalSlider_a_"+str(slider))
            slider_object.setValue(step["verticalSlider_a_"+str(slider)])
        for slider in range(1, 13):
            slider_object = getattr(UI, "verticalSlider_b_"+str(slider))
            slider_object.setValue(step["verticalSlider_b_"+str(slider)])

SEQUENCE = Sequencer()

UI.pushButton_addStep.clicked.connect(SEQUENCE.add_step)
UI.pushButton_deleteStep.clicked.connect(SEQUENCE.delete_step)
UI.listWidget.itemClicked.connect(SEQUENCE.click_step)

UI.pushButton_main_sequencerplay.clicked.connect(SEQUENCE.play_sequence)

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
sys.exit(APP.exec_())
