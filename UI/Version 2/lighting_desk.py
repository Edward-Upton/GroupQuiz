import sys
import json
import mido
import mido
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QStyleFactory
from math import floor
from Ui_lighting_control import Ui_MainWindow

APP = QApplication([])
#APP.setStyle(QStyleFactory.create('GTK+'))
WINDOW = QMainWindow()
UI = Ui_MainWindow()
UI.setupUi(WINDOW)
#WINDOW.setStyle(QStyleFactory.create('GTK+'))

class LightingDesk:

    def __init__(self):
        self.ports = ["Please Select Device"]
        self.ports += mido.get_output_names()
        self.outport = None
        self.updateDevices()



    def updateDevices(self):
        UI.comboBox_mididevice.clear()
        UI.comboBox_mididevice.addItems(self.ports)
        UI.frame_sequencer.setDisabled(True)
        UI.frame_channels.setDisabled(True)
        UI.frame_3.setDisabled(True)
        UI.frame_channelproperties.setDisabled(True)
        UI.frame_main.setDisabled(True)

    def select_midi_device(self, index):
        if index == 0:
            UI.frame_sequencer.setDisabled(True)
            UI.frame_channels.setDisabled(True)
            UI.frame_3.setDisabled(True)
            UI.frame_channelproperties.setDisabled(True)
            UI.frame_main.setDisabled(True)
            self.outport = None
        else:
            UI.frame_sequencer.setDisabled(False)
            UI.frame_channels.setDisabled(False)
            UI.frame_3.setDisabled(False)
            UI.frame_channelproperties.setDisabled(False)
            UI.frame_main.setDisabled(False)
            try:
                self.outport = mido.open_output(name=self.ports[index])
            except (IOError, OSError) as error:
                err_msg = QtWidgets.QMessageBox()
                err_msg.setIcon(QtWidgets.QMessageBox.Warning)
                err_msg.setWindowTitle("MIDI Device Error")
                err_msg.setText("There has been an error.")
                err_msg.setInformativeText("Could not connect to MIDI Device")
                err_msg.setDetailedText(str(error))
                err_msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                err_msg.exec_()

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
        #print(str(msg))
        self.outport.send(msg)
    
    def blackout(self, value):
        if value:
            for channel in range(0, 12):
                msg = mido.Message("control_change", control=channel, value=0, time=1)
                self.outport.send(msg)
            UI.frame_channels.setDisabled(True)
            UI.frame_sequencer.setDisabled(True)
            UI.frame_channelproperties.setDisabled(True)
            UI.label_qc_blackout.setStyleSheet("color: rgb(255, 0, 0);")
        else:
            UI.frame_channels.setDisabled(False)
            UI.frame_sequencer.setDisabled(False)
            UI.frame_channelproperties.setDisabled(False)
            UI.label_qc_blackout.setStyleSheet("color: rgb(255, 255, 255);")
            for channel in range(1, 13):
                slider = getattr(UI, "verticalSlider_a_"+str(channel))
                msg = mido.Message("control_change", control=(channel-1), value=slider.value(), time=1)
                self.outport.send(msg)



class Channels:

    def __init__(self):
        self.selected_channels = []
        self.channel_info = {}

        self.flash_previous_value = -1

        for channel_index in range(1, 13):
            self.channel_info[getattr(UI, "verticalSlider_a_"+str(channel_index))] = {
                "name": "",
                "color": (255, 255, 255),
                "notes": "",
                "label": getattr(UI, "label_a_"+str(channel_index))
            }
    def toggle_channel(self, channel_num):
        checkbox = getattr(UI, "checkBox_a_"+str(channel_num))
        slider = getattr(UI, "verticalSlider_a_"+str(channel_num))
        if checkbox.checkState() == 2:
            self.selected_channels.append(slider)
        else:
            self.selected_channels.pop(self.selected_channels.index(slider))
        
        if len(self.selected_channels) > 1:
            UI.stackedWidget_channelproperties.setCurrentIndex(2)
            UI.verticalSlider_multiedit.setValue(self.selected_channels[-1].value())
        elif len(self.selected_channels) == 1:
            UI.stackedWidget_channelproperties.setCurrentIndex(1)
            self.get_channel_properties(self.selected_channels[0])
        else:
            UI.stackedWidget_channelproperties.setCurrentIndex(0)
    
    def get_channel_properties(self, channel_object):
        UI.lineEdit_channelname.setText(self.channel_info[channel_object]["name"])
        UI.pushButton_lightcolor.setStyleSheet("background-color: rgb%s;" % str(self.channel_info[channel_object]["color"]))
        UI.plainTextEdit_notes.setPlainText(self.channel_info[channel_object]["notes"])
        UI.spinBox.setValue(self.selected_channels[0].value())
    
    def multi_slide(self, value):
        for slider in self.selected_channels:
            slider.setValue(value)
        UI.verticalSlider_multiedit.setValue(value)
        
    def change_name(self, value):
        self.channel_info[self.selected_channels[0]]["name"] = value
    
    def change_notes(self, value):
        self.channel_info[self.selected_channels[0]]["notes"] = value
    
    def change_color(self):
        color = QtWidgets.QColorDialog.getColor()
        hex_color = color.name()[1:]
        rgb_color = (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))
        self.channel_info[self.selected_channels[0]]["color"] = rgb_color
        UI.pushButton_lightcolor.setStyleSheet("background-color: rgb%s;" % str(self.channel_info[self.selected_channels[0]]["color"]))
    def change_value(self, value):
        self.selected_channels[0].setValue(value)
    
    def slider_changed(self, slider):
        label_rgb = self.channel_info[slider]["color"]
        label_rgb_brightness = tuple(int((slider.value()/127)*x) for x in label_rgb)
        self.channel_info[slider]["label"].setStyleSheet("color: rgb%s; background-color: rgba(0, 0, 0, 0);" % str(label_rgb_brightness))
        if self.selected_channels:
            if slider == self.selected_channels[0]:
                UI.spinBox.setValue(slider.value())
    
    def flash_press(self, slider):
        self.flash_previous_value = slider.value()
        slider.setValue(127)
    
    def flash_release(self, slider):
        slider.setValue(self.flash_previous_value)
class DeskIO:
    
    def __init__(self, channel: Channels):
        self.file_filters = "ChannelExport File (*.chexp);;Channel Export JSON (*.json)"
        self.channels = channel
    def export_channels(self):
        name = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Channel Settings', '', self.file_filters)
        json_data = {}
        if not name[0]:
            return

        for key in range(len(self.channels.channel_info.keys())):
            index = list(self.channels.channel_info.keys())[key]
            json_data[key] = {}
            json_data[key]["name"] = self.channels.channel_info[index]["name"]
            json_data[key]["color"] = self.channels.channel_info[index]["color"]
            json_data[key]["label"] = key
            json_data[key]["notes"] = self.channels.channel_info[index]["notes"]
        with open(name[0], 'w') as fp:
            json.dump(json_data, fp)
    
    def import_channels(self):
        name = QtWidgets.QFileDialog.getOpenFileName(None, 'Open Channel Settings', '', self.file_filters)
        json_data = {}
        if not name[0]:
            return

        with open(name[0], 'r') as fp:
            json_data = json.load(fp)

        channel_data = {}
        for key in range(len(json_data.keys())):
            channel_data[getattr(UI, "verticalSlider_a_"+str(key+1))] = {}
            channel_data[getattr(UI, "verticalSlider_a_"+str(key+1))]["name"] = json_data[str(key)]["name"]
            channel_data[getattr(UI, "verticalSlider_a_"+str(key+1))]["color"] = tuple(json_data[str(key)]["color"])
            channel_data[getattr(UI, "verticalSlider_a_"+str(key+1))]["label"] = getattr(UI, "label_a_"+str(key+1))
            channel_data[getattr(UI, "verticalSlider_a_"+str(key+1))]["notes"] = json_data[str(key)]["notes"]
        
        self.channels.channel_info = channel_data
        if len(self.channels.selected_channels) == 1:
            self.channels.get_channel_properties(self.channels.selected_channels[0])

DESK = LightingDesk()
CHANNEL = Channels()
APP_IO = DeskIO(CHANNEL)

UI.pushButton_exportChannel.clicked.connect(APP_IO.export_channels)
UI.pushButton_importChannel.clicked.connect(APP_IO.import_channels)

UI.comboBox_mididevice.currentIndexChanged.connect(DESK.select_midi_device)
UI.pushButton_qc_blackout.toggled.connect(DESK.blackout)

UI.verticalSlider_multiedit.valueChanged.connect(CHANNEL.multi_slide)
UI.pushButton_fullup.pressed.connect(lambda: CHANNEL.multi_slide(127))
UI.pushButton_fulldown.pressed.connect(lambda: CHANNEL.multi_slide(0))
UI.pushButton_lightcolor.pressed.connect(CHANNEL.change_color)
UI.lineEdit_channelname.textEdited.connect(CHANNEL.change_name)
UI.plainTextEdit_notes.textChanged.connect(lambda: CHANNEL.change_notes(UI.plainTextEdit_notes.toPlainText()))
UI.spinBox.valueChanged.connect(CHANNEL.change_value)

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

UI.verticalSlider_a_1.valueChanged.connect(lambda: CHANNEL.slider_changed(UI.verticalSlider_a_1))
UI.verticalSlider_a_2.valueChanged.connect(lambda: CHANNEL.slider_changed(UI.verticalSlider_a_2))
UI.verticalSlider_a_3.valueChanged.connect(lambda: CHANNEL.slider_changed(UI.verticalSlider_a_3))
UI.verticalSlider_a_4.valueChanged.connect(lambda: CHANNEL.slider_changed(UI.verticalSlider_a_4))
UI.verticalSlider_a_5.valueChanged.connect(lambda: CHANNEL.slider_changed(UI.verticalSlider_a_5))
UI.verticalSlider_a_6.valueChanged.connect(lambda: CHANNEL.slider_changed(UI.verticalSlider_a_6))
UI.verticalSlider_a_7.valueChanged.connect(lambda: CHANNEL.slider_changed(UI.verticalSlider_a_7))
UI.verticalSlider_a_8.valueChanged.connect(lambda: CHANNEL.slider_changed(UI.verticalSlider_a_8))
UI.verticalSlider_a_9.valueChanged.connect(lambda: CHANNEL.slider_changed(UI.verticalSlider_a_9))
UI.verticalSlider_a_10.valueChanged.connect(lambda: CHANNEL.slider_changed(UI.verticalSlider_a_10))
UI.verticalSlider_a_11.valueChanged.connect(lambda: CHANNEL.slider_changed(UI.verticalSlider_a_11))
UI.verticalSlider_a_12.valueChanged.connect(lambda: CHANNEL.slider_changed(UI.verticalSlider_a_12))

UI.checkBox_a_1.stateChanged.connect(lambda: CHANNEL.toggle_channel(1))
UI.checkBox_a_2.stateChanged.connect(lambda: CHANNEL.toggle_channel(2))
UI.checkBox_a_3.stateChanged.connect(lambda: CHANNEL.toggle_channel(3))
UI.checkBox_a_4.stateChanged.connect(lambda: CHANNEL.toggle_channel(4))
UI.checkBox_a_5.stateChanged.connect(lambda: CHANNEL.toggle_channel(5))
UI.checkBox_a_6.stateChanged.connect(lambda: CHANNEL.toggle_channel(6))
UI.checkBox_a_7.stateChanged.connect(lambda: CHANNEL.toggle_channel(7))
UI.checkBox_a_8.stateChanged.connect(lambda: CHANNEL.toggle_channel(8))
UI.checkBox_a_9.stateChanged.connect(lambda: CHANNEL.toggle_channel(9))
UI.checkBox_a_10.stateChanged.connect(lambda: CHANNEL.toggle_channel(10))
UI.checkBox_a_11.stateChanged.connect(lambda: CHANNEL.toggle_channel(11))
UI.checkBox_a_12.stateChanged.connect(lambda: CHANNEL.toggle_channel(12))

UI.pushButton_flash_1.pressed.connect(lambda: CHANNEL.flash_press(UI.verticalSlider_a_1))
UI.pushButton_flash_2.pressed.connect(lambda: CHANNEL.flash_press(UI.verticalSlider_a_2))
UI.pushButton_flash_3.pressed.connect(lambda: CHANNEL.flash_press(UI.verticalSlider_a_3))
UI.pushButton_flash_4.pressed.connect(lambda: CHANNEL.flash_press(UI.verticalSlider_a_4))
UI.pushButton_flash_5.pressed.connect(lambda: CHANNEL.flash_press(UI.verticalSlider_a_5))
UI.pushButton_flash_6.pressed.connect(lambda: CHANNEL.flash_press(UI.verticalSlider_a_6))
UI.pushButton_flash_7.pressed.connect(lambda: CHANNEL.flash_press(UI.verticalSlider_a_7))
UI.pushButton_flash_8.pressed.connect(lambda: CHANNEL.flash_press(UI.verticalSlider_a_8))
UI.pushButton_flash_9.pressed.connect(lambda: CHANNEL.flash_press(UI.verticalSlider_a_9))
UI.pushButton_flash_10.pressed.connect(lambda: CHANNEL.flash_press(UI.verticalSlider_a_10))
UI.pushButton_flash_11.pressed.connect(lambda: CHANNEL.flash_press(UI.verticalSlider_a_11))
UI.pushButton_flash_12.pressed.connect(lambda: CHANNEL.flash_press(UI.verticalSlider_a_12))

UI.pushButton_flash_1.released.connect(lambda: CHANNEL.flash_release(UI.verticalSlider_a_1))
UI.pushButton_flash_2.released.connect(lambda: CHANNEL.flash_release(UI.verticalSlider_a_2))
UI.pushButton_flash_3.released.connect(lambda: CHANNEL.flash_release(UI.verticalSlider_a_3))
UI.pushButton_flash_4.released.connect(lambda: CHANNEL.flash_release(UI.verticalSlider_a_4))
UI.pushButton_flash_5.released.connect(lambda: CHANNEL.flash_release(UI.verticalSlider_a_5))
UI.pushButton_flash_6.released.connect(lambda: CHANNEL.flash_release(UI.verticalSlider_a_6))
UI.pushButton_flash_7.released.connect(lambda: CHANNEL.flash_release(UI.verticalSlider_a_7))
UI.pushButton_flash_8.released.connect(lambda: CHANNEL.flash_release(UI.verticalSlider_a_8))
UI.pushButton_flash_9.released.connect(lambda: CHANNEL.flash_release(UI.verticalSlider_a_9))
UI.pushButton_flash_10.released.connect(lambda: CHANNEL.flash_release(UI.verticalSlider_a_10))
UI.pushButton_flash_11.released.connect(lambda: CHANNEL.flash_release(UI.verticalSlider_a_11))
UI.pushButton_flash_12.released.connect(lambda: CHANNEL.flash_release(UI.verticalSlider_a_12))

WINDOW.show()
APP.exec_()
