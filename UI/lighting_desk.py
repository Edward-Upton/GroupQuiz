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
            print("control_change ", slider_number-1, " value: ", value)
#            self.output.send_message([CONTROL_CHANGE, (slider_number-1), value])
        elif slider_letter == "b":
            print("control_change ", slider_number+11, " value: ", value)
#            self.output.send_message([CONTROL_CHANGE, (slider_number+11), value])

DESK = LightingDesk()
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
