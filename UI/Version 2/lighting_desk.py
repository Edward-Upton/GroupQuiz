import json
import os
import sys
import time
from math import floor

import mido
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QStyleFactory
from worker import Worker

import pyaudio
import audioop
from Ui_lighting_control import Ui_MainWindow

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

APP = QApplication([])
ICON = QtGui.QIcon(SCRIPT_DIR+"\resources\light-bulb-off.png")
APP.setWindowIcon(ICON)
WINDOW = QMainWindow()
WINDOW.setWindowTitle("Lighting Desk Software")
UI = Ui_MainWindow()
UI.setupUi(WINDOW)


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
        slider_letter, slider_number = slider_name.split(
            '_')[1], slider_name.split('_')[2]
        slider_object = getattr(UI, slider_name)
        slider_number = int(slider_number)
        value = slider_object.value()
        msg = None

        if slider_letter == "a":
            msg = mido.Message("control_change", control=(
                slider_number-1), value=value, time=1)
        elif slider_letter == "b":
            msg = mido.Message("control_change", control=(
                slider_number+11), value=value, time=1)
        # print(str(msg))
        self.outport.send(msg)

    def blackout(self, value):
        if value:
            for channel in range(0, 12):
                msg = mido.Message(
                    "control_change", control=channel, value=0, time=1)
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
                msg = mido.Message("control_change", control=(
                    channel-1), value=slider.value(), time=1)
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
            UI.verticalSlider_multiedit.setValue(
                self.selected_channels[-1].value())
        elif len(self.selected_channels) == 1:
            UI.stackedWidget_channelproperties.setCurrentIndex(1)
            self.get_channel_properties(self.selected_channels[0])
        else:
            UI.stackedWidget_channelproperties.setCurrentIndex(0)

    def get_channel_properties(self, channel_object):
        UI.lineEdit_channelname.setText(
            self.channel_info[channel_object]["name"])
        UI.pushButton_lightcolor.setStyleSheet(
            "background-color: rgb%s;" % str(self.channel_info[channel_object]["color"]))
        UI.plainTextEdit_notes.setPlainText(
            self.channel_info[channel_object]["notes"])
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
        rgb_color = (int(hex_color[0:2], 16), int(
            hex_color[2:4], 16), int(hex_color[4:6], 16))
        self.channel_info[self.selected_channels[0]]["color"] = rgb_color
        UI.pushButton_lightcolor.setStyleSheet(
            "background-color: rgb%s;" % str(self.channel_info[self.selected_channels[0]]["color"]))

    def change_value(self, value):
        self.selected_channels[0].setValue(value)

    def slider_changed(self, slider):
        label_rgb = self.channel_info[slider]["color"]
        label_rgb_brightness = tuple(
            int((slider.value()/127)*x) for x in label_rgb)
        self.channel_info[slider]["label"].setStyleSheet(
            "color: rgb%s; background-color: rgba(0, 0, 0, 0);" % str(label_rgb_brightness))
        if self.selected_channels:
            if slider == self.selected_channels[0]:
                UI.spinBox.setValue(slider.value())

    def flash_press(self, slider):
        self.flash_previous_value = slider.value()
        slider.setValue(127)

    def flash_release(self, slider):
        slider.setValue(self.flash_previous_value)


class Sequencer:

    def __init__(self):
        self.sequence = []
        self.sequence_duration = 0
        self.sequence_worker = Worker(self.sequence_thread)
        self.delete = False

    def update_step(self, row):
        if self.delete:
            return

        for slider in range(1, 13):
            slider_object = getattr(UI, "verticalSlider_a_"+str(slider))
            slider_object.setValue(
                self.sequence[UI.listWidget_sequence.currentRow()]["verticalSlider_a_"+str(slider)])

    def add_step(self):
        step = {}
        step["fade_time"] = UI.doubleSpinBox_fadetime.value()
        step["hold_time"] = UI.doubleSpinBox_holdtime.value()
        for slider in range(1, 13):
            slider_object = getattr(UI, "verticalSlider_a_"+str(slider))
            step["verticalSlider_a_"+str(slider)] = slider_object.value()

        new_step = QtWidgets.QListWidgetItem()
        new_step.setText(str(UI.listWidget_sequence.count()+1))
        UI.listWidget_sequence.addItem(new_step)
        self.sequence.append(step)
        UI.listWidget_sequence.setCurrentRow(len(self.sequence)-1)
        UI.lcdNumber_steps.display(len(self.sequence))
        self.sequence_duration += UI.doubleSpinBox_fadetime.value() + \
            UI.doubleSpinBox_holdtime.value()
        UI.lcdNumber_duration.display(self.sequence_duration)

    def replace_step(self):
        currentRow = UI.listWidget_sequence.currentRow()
        self.sequence_duration -= self.sequence[currentRow]["fade_time"] + \
            self.sequence[currentRow]["hold_time"]
        step = {}
        step["fade_time"] = UI.doubleSpinBox_fadetime.value()
        step["hold_time"] = UI.doubleSpinBox_holdtime.value()
        for slider in range(1, 13):
            slider_object = getattr(UI, "verticalSlider_a_"+str(slider))
            step["verticalSlider_a_"+str(slider)] = slider_object.value()
        self.sequence[currentRow] = step
        self.sequence_duration += UI.doubleSpinBox_fadetime.value() + \
            UI.doubleSpinBox_holdtime.value()
        UI.lcdNumber_duration.display(self.sequence_duration)

    def delete_step(self):
        if not self.sequence:
            UI.lcdNumber_steps.display(0)
            UI.lcdNumber_duration.display(0)
            return
        self.delete = True
        currentRow = UI.listWidget_sequence.currentRow()
        self.sequence_duration -= self.sequence[currentRow]["fade_time"] + \
            self.sequence[currentRow]["hold_time"]
        UI.lcdNumber_duration.display(self.sequence_duration)
        self.sequence.pop(currentRow-1)
        UI.listWidget_sequence.takeItem(currentRow)
        UI.lcdNumber_steps.display(len(self.sequence))
        self.delete = False

    def next_step(self):
        if not self.sequence:
            return

        if UI.listWidget_sequence.currentRow() != len(self.sequence)-1:
            UI.listWidget_sequence.setCurrentRow(
                UI.listWidget_sequence.currentRow()+1)

    def prev_step(self):
        if not self.sequence:
            return

        if UI.listWidget_sequence.currentRow() != 0:
            UI.listWidget_sequence.setCurrentRow(
                UI.listWidget_sequence.currentRow()-1)

    def move_step_left(self):
        pass
        # currentRow = UI.listWidget_sequence.currentRow()
        # currentItem = UI.listWidget_sequence.takeItem(currentRow)
        # currentStep = self.sequence.pop(currentRow)
        # if currentRow == 0:
        #     UI.listWidget_sequence.addItem(currentItem)
        #     UI.listWidget_sequence.setCurrentRow(len(self.sequence))
        #     self.sequence.append(currentStep)
        # else:
        #     UI.listWidget_sequence.insertItem(currentRow - 1, currentItem)
        #     UI.listWidget_sequence.setCurrentRow(currentRow - 1)
        #     self.sequence.insert(currentRow, currentStep)

    def move_step_right(self):
        pass
        # currentRow = UI.listWidget_sequence.currentRow()
        # currentItem = UI.listWidget_sequence.takeItem(currentRow)
        # currentStep = self.sequence.pop(currentRow)
        # if currentRow == len(self.sequence):
        #     UI.listWidget_sequence.insertItem(0, currentItem)
        #     UI.listWidget_sequence.setCurrentRow(0)
        #     self.sequence.insert(0, currentStep)
        # else:
        #     UI.listWidget_sequence.insertItem(currentRow + 1, currentItem)
        #     UI.listWidget_sequence.setCurrentRow(currentRow + 1)
        #     self.sequence.insert(currentRow + 1, currentStep)

    def sequence_thread(self):
        if UI.pushButton_sequencer_repeat.isChecked():
            while UI.pushButton_sequencer_repeat.isChecked():
                for index, step in enumerate(self.sequence):
                    time.sleep(step["hold_time"])
                    if step["fade_time"]:
                        for update in range(0, int(step["fade_time"]*100), 1):
                            for slider in range(1, 13):
                                if not UI.pushButton_sequencer_play.isChecked() or UI.pushButton_qc_blackout.isChecked():
                                    return
                                slider_object = getattr(
                                    UI, "verticalSlider_a_"+str(slider))
                                if index:
                                    begin = step["verticalSlider_a_" +
                                                 str(slider)]
                                else:
                                    begin = self.sequence[0]["verticalSlider_a_" +
                                                             str(slider)]

                                if index >= len(self.sequence)-1:
                                    end = self.sequence[0]["verticalSlider_a_" +
                                                           str(slider)]
                                else:
                                    end = self.sequence[index +
                                                        1]["verticalSlider_a_"+str(slider)]

                                gradient = (end-begin)/step["fade_time"]
                                change_value = int(
                                    floor((gradient*update*0.01)+begin))
                                slider_object.setValue(change_value)
                            time.sleep(0.01)
                    else:
                        for slider in range(1, 13):
                            slider_object = getattr(
                                UI, "verticalSlider_a_"+str(slider))
                            if index >= len(self.sequence)-1:
                                slider_object.setValue(
                                    self.sequence[0]["verticalSlider_a_"+str(slider)])
                            else:
                                slider_object.setValue(
                                    self.sequence[index+1]["verticalSlider_a_"+str(slider)])
        else:
            for index, step in enumerate(self.sequence):
                if index != len(self.sequence) - 1:
                    time.sleep(step["hold_time"])
                if step["fade_time"]:
                    for update in range(0, int(step["fade_time"]*100), 1):
                        for slider in range(1, 13):
                            if not UI.pushButton_sequencer_play.isChecked() or UI.pushButton_qc_blackout.isChecked():
                                return
                            slider_object = getattr(
                                UI, "verticalSlider_a_"+str(slider))
                            if index:
                                begin = step["verticalSlider_a_"+str(slider)]
                            else:
                                begin = self.sequence[0]["verticalSlider_a_" +
                                                         str(slider)]

                            if index >= len(self.sequence)-1:
                                break
                            else:
                                end = self.sequence[index +
                                                    1]["verticalSlider_a_"+str(slider)]

                            gradient = (end-begin)/step["fade_time"]
                            change_value = int(
                                floor((gradient*update*0.01)+begin))
                            slider_object.setValue(change_value)
                        time.sleep(0.01)
                else:
                    for slider in range(1, 13):
                        slider_object = getattr(
                            UI, "verticalSlider_a_"+str(slider))
                        if index >= len(self.sequence)-1:
                            break
                        else:
                            slider_object.setValue(
                                self.sequence[index+1]["verticalSlider_a_"+str(slider)])
                # UI.listWidget_sequence.setCurrentRow(index)

            UI.pushButton_sequencer_play.setChecked(False)
            return

    def stop_sequence(self):
        self.sequence_worker.pause()
        UI.listWidget_sequence.setCurrentRow(0)

    def start_sequence(self):
        if self.sequence_worker.is_running():
            self.sequence_worker.resume()
        else:
            self.sequence_worker.start()

    def toggle_playback(self, value):
        if value:
            self.start_sequence()
            UI.frame_multiedit.setDisabled(True)
            UI.spinBox.setDisabled(True)
        else:
            # UI.pushButton_sequencer_repeat.setChecked(False)
            self.stop_sequence()
            UI.frame_multiedit.setDisabled(False)
            UI.spinBox.setDisabled(False)

class SoundToLight:

    def __init__(self):
        self.audio_class = pyaudio.PyAudio()

        self.chunk = 4096 #sample rate, higher = chunkier, slower       def: 2048
        self.device = 4 #device from dev = p.get_device_info_by_index(device)   def: 2
        self.scale = 50 #scale: < dimmer    > brighter                      def: 50
        self.exponent = 1 #increases/decreases distance between loudness. lower means flatter change    def: 4

        self.stream = self.audio_class.open(format = pyaudio.paInt16,
                             channels=1,
                             rate=44100,
                             input=True,
                             frames_per_buffer=self.chunk,
                             input_device_index=self.device)

        self.audio_worker = Worker(self.soundlight_thread)
        #self.audio_worker.start()

    def soundlight_thread(self):
        time.sleep(10)
        while True:
            data  = self.stream.read(self.chunk)
            rms   = audioop.rms(data, 2)

            level = min(rms / (2.0 ** 16) * self.scale, 1.0)
            level = level**self.exponent
            level = int(level * 127) + 50
            if level > 127:
                level = 127

            UI.verticalSlider_a_1.setValue(127-level+50)
            UI.verticalSlider_a_4.setValue(level)
            time.sleep(0.01)


class DeskIO:

    def __init__(self, channel: Channels):
        self.file_filters = "ChannelExport File (*.chexp);;Channel Export JSON (*.json)"
        self.channels = channel

    def export_channels(self):
        name = QtWidgets.QFileDialog.getSaveFileName(
            None, 'Save Channel Settings', '', self.file_filters)
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
        name = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Open Channel Settings', '', self.file_filters)
        json_data = {}
        if not name[0]:
            return

        with open(name[0], 'r') as fp:
            json_data = json.load(fp)

        channel_data = {}
        for key in range(len(json_data.keys())):
            channel_data[getattr(UI, "verticalSlider_a_"+str(key+1))] = {}
            channel_data[getattr(UI, "verticalSlider_a_"+str(key+1))
                         ]["name"] = json_data[str(key)]["name"]
            channel_data[getattr(UI, "verticalSlider_a_"+str(key+1))
                         ]["color"] = tuple(json_data[str(key)]["color"])
            channel_data[getattr(UI, "verticalSlider_a_"+str(key+1))
                         ]["label"] = getattr(UI, "label_a_"+str(key+1))
            channel_data[getattr(UI, "verticalSlider_a_"+str(key+1))
                         ]["notes"] = json_data[str(key)]["notes"]

        self.channels.channel_info = channel_data
        if len(self.channels.selected_channels) == 1:
            self.channels.get_channel_properties(
                self.channels.selected_channels[0])


DESK = LightingDesk()
CHANNEL = Channels()
SEQUENCE = Sequencer()
SNDTOLIGHT = SoundToLight()
APP_IO = DeskIO(CHANNEL)

UI.pushButton_moveStepLeft.clicked.connect(SEQUENCE.move_step_left)
UI.pushButton_moveStepRight.clicked.connect(SEQUENCE.move_step_right)
UI.pushButton_sequencer_nextstep.clicked.connect(SEQUENCE.next_step)
UI.pushButton_sequencer_prevstep.clicked.connect(SEQUENCE.prev_step)
UI.pushButton_addStep.clicked.connect(SEQUENCE.add_step)
UI.pushButton_deleteStep.clicked.connect(SEQUENCE.delete_step)
UI.pushButton_replaceStep.clicked.connect(SEQUENCE.replace_step)
UI.listWidget_sequence.currentRowChanged.connect(SEQUENCE.update_step)
UI.pushButton_sequencer_play.toggled.connect(SEQUENCE.toggle_playback)

UI.pushButton_exportChannel.clicked.connect(APP_IO.export_channels)
UI.pushButton_importChannel.clicked.connect(APP_IO.import_channels)

UI.comboBox_mididevice.currentIndexChanged.connect(DESK.select_midi_device)
UI.pushButton_qc_blackout.toggled.connect(DESK.blackout)

UI.verticalSlider_multiedit.valueChanged.connect(CHANNEL.multi_slide)
UI.pushButton_fullup.pressed.connect(lambda: CHANNEL.multi_slide(127))
UI.pushButton_fulldown.pressed.connect(lambda: CHANNEL.multi_slide(0))
UI.pushButton_lightcolor.pressed.connect(CHANNEL.change_color)
UI.lineEdit_channelname.textEdited.connect(CHANNEL.change_name)
UI.plainTextEdit_notes.textChanged.connect(
    lambda: CHANNEL.change_notes(UI.plainTextEdit_notes.toPlainText()))
UI.spinBox.valueChanged.connect(CHANNEL.change_value)

UI.verticalSlider_a_1.valueChanged.connect(
    lambda: DESK.updateLight("verticalSlider_a_1"))
UI.verticalSlider_a_2.valueChanged.connect(
    lambda: DESK.updateLight("verticalSlider_a_2"))
UI.verticalSlider_a_3.valueChanged.connect(
    lambda: DESK.updateLight("verticalSlider_a_3"))
UI.verticalSlider_a_4.valueChanged.connect(
    lambda: DESK.updateLight("verticalSlider_a_4"))
UI.verticalSlider_a_5.valueChanged.connect(
    lambda: DESK.updateLight("verticalSlider_a_5"))
UI.verticalSlider_a_6.valueChanged.connect(
    lambda: DESK.updateLight("verticalSlider_a_6"))
UI.verticalSlider_a_7.valueChanged.connect(
    lambda: DESK.updateLight("verticalSlider_a_7"))
UI.verticalSlider_a_8.valueChanged.connect(
    lambda: DESK.updateLight("verticalSlider_a_8"))
UI.verticalSlider_a_9.valueChanged.connect(
    lambda: DESK.updateLight("verticalSlider_a_9"))
UI.verticalSlider_a_10.valueChanged.connect(
    lambda: DESK.updateLight("verticalSlider_a_10"))
UI.verticalSlider_a_11.valueChanged.connect(
    lambda: DESK.updateLight("verticalSlider_a_11"))
UI.verticalSlider_a_12.valueChanged.connect(
    lambda: DESK.updateLight("verticalSlider_a_12"))

UI.verticalSlider_a_1.valueChanged.connect(
    lambda: CHANNEL.slider_changed(UI.verticalSlider_a_1))
UI.verticalSlider_a_2.valueChanged.connect(
    lambda: CHANNEL.slider_changed(UI.verticalSlider_a_2))
UI.verticalSlider_a_3.valueChanged.connect(
    lambda: CHANNEL.slider_changed(UI.verticalSlider_a_3))
UI.verticalSlider_a_4.valueChanged.connect(
    lambda: CHANNEL.slider_changed(UI.verticalSlider_a_4))
UI.verticalSlider_a_5.valueChanged.connect(
    lambda: CHANNEL.slider_changed(UI.verticalSlider_a_5))
UI.verticalSlider_a_6.valueChanged.connect(
    lambda: CHANNEL.slider_changed(UI.verticalSlider_a_6))
UI.verticalSlider_a_7.valueChanged.connect(
    lambda: CHANNEL.slider_changed(UI.verticalSlider_a_7))
UI.verticalSlider_a_8.valueChanged.connect(
    lambda: CHANNEL.slider_changed(UI.verticalSlider_a_8))
UI.verticalSlider_a_9.valueChanged.connect(
    lambda: CHANNEL.slider_changed(UI.verticalSlider_a_9))
UI.verticalSlider_a_10.valueChanged.connect(
    lambda: CHANNEL.slider_changed(UI.verticalSlider_a_10))
UI.verticalSlider_a_11.valueChanged.connect(
    lambda: CHANNEL.slider_changed(UI.verticalSlider_a_11))
UI.verticalSlider_a_12.valueChanged.connect(
    lambda: CHANNEL.slider_changed(UI.verticalSlider_a_12))

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

UI.pushButton_flash_1.pressed.connect(
    lambda: CHANNEL.flash_press(UI.verticalSlider_a_1))
UI.pushButton_flash_2.pressed.connect(
    lambda: CHANNEL.flash_press(UI.verticalSlider_a_2))
UI.pushButton_flash_3.pressed.connect(
    lambda: CHANNEL.flash_press(UI.verticalSlider_a_3))
UI.pushButton_flash_4.pressed.connect(
    lambda: CHANNEL.flash_press(UI.verticalSlider_a_4))
UI.pushButton_flash_5.pressed.connect(
    lambda: CHANNEL.flash_press(UI.verticalSlider_a_5))
UI.pushButton_flash_6.pressed.connect(
    lambda: CHANNEL.flash_press(UI.verticalSlider_a_6))
UI.pushButton_flash_7.pressed.connect(
    lambda: CHANNEL.flash_press(UI.verticalSlider_a_7))
UI.pushButton_flash_8.pressed.connect(
    lambda: CHANNEL.flash_press(UI.verticalSlider_a_8))
UI.pushButton_flash_9.pressed.connect(
    lambda: CHANNEL.flash_press(UI.verticalSlider_a_9))
UI.pushButton_flash_10.pressed.connect(
    lambda: CHANNEL.flash_press(UI.verticalSlider_a_10))
UI.pushButton_flash_11.pressed.connect(
    lambda: CHANNEL.flash_press(UI.verticalSlider_a_11))
UI.pushButton_flash_12.pressed.connect(
    lambda: CHANNEL.flash_press(UI.verticalSlider_a_12))

UI.pushButton_flash_1.released.connect(
    lambda: CHANNEL.flash_release(UI.verticalSlider_a_1))
UI.pushButton_flash_2.released.connect(
    lambda: CHANNEL.flash_release(UI.verticalSlider_a_2))
UI.pushButton_flash_3.released.connect(
    lambda: CHANNEL.flash_release(UI.verticalSlider_a_3))
UI.pushButton_flash_4.released.connect(
    lambda: CHANNEL.flash_release(UI.verticalSlider_a_4))
UI.pushButton_flash_5.released.connect(
    lambda: CHANNEL.flash_release(UI.verticalSlider_a_5))
UI.pushButton_flash_6.released.connect(
    lambda: CHANNEL.flash_release(UI.verticalSlider_a_6))
UI.pushButton_flash_7.released.connect(
    lambda: CHANNEL.flash_release(UI.verticalSlider_a_7))
UI.pushButton_flash_8.released.connect(
    lambda: CHANNEL.flash_release(UI.verticalSlider_a_8))
UI.pushButton_flash_9.released.connect(
    lambda: CHANNEL.flash_release(UI.verticalSlider_a_9))
UI.pushButton_flash_10.released.connect(
    lambda: CHANNEL.flash_release(UI.verticalSlider_a_10))
UI.pushButton_flash_11.released.connect(
    lambda: CHANNEL.flash_release(UI.verticalSlider_a_11))
UI.pushButton_flash_12.released.connect(
    lambda: CHANNEL.flash_release(UI.verticalSlider_a_12))

WINDOW.show()
APP.exec_()
