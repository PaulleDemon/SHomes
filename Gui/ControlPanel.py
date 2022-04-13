import re
import os
import sys
import json
import requests
import pyttsx3
from PyQt5 import QtWidgets, QtCore, QtGui, QtMultimedia

from dotenv import load_dotenv

load_dotenv()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[16].id)

JSON_PATH = os.path.join(os.getcwd(), "data/data.json")

class ControlPanel(QtWidgets.QWidget):
    # widget that is use to save image, capture image, draw rect etc.

    capture = QtCore.pyqtSignal(bool)  # sends signal when capture button is pressed
    drawRect = QtCore.pyqtSignal(bool)  # sends signal when draw rect is pressed
    cameraChanged = QtCore.pyqtSignal(int)

    imgSaved =QtCore.pyqtSignal() # emits signal when the data is saved

    def __init__(self, *args, **kwargs):
        super(ControlPanel, self).__init__(*args, **kwargs)

        self.capturing = False
        self.drawingRect = False
        self.capturedImage: QtGui.QImage = QtGui.QImage()

        self.setLayout(QtWidgets.QVBoxLayout())

        self.capturedFrame = QtWidgets.QFrame(self)
        self.capturedFrame.setLayout(QtWidgets.QVBoxLayout())

        self.captured_img_lbl = QtWidgets.QLabel()
        self.captured_img_lbl.setScaledContents(True)
        self.setMinimumSize(300, 250)
        self.captured_img_lbl.setMaximumHeight(300)

        self.captured_img_dimensions = QtWidgets.QLabel()

        self.error_lbl = QtWidgets.QLabel(objectName="ErrorLabel")
        self.error_lbl.setWordWrap(True)

        self.directory_edit = QtWidgets.QLineEdit()
        self.directory_edit.setPlaceholderText("Set output folder")
        self.directory_edit.insert(os.path.join(os.getcwd(), 'data', 'imagedata'))

        self.save_as_lbl = QtWidgets.QLineEdit()
        self.save_as_lbl.setPlaceholderText("Set image name")

        self.set_fan_speed = QtWidgets.QSpinBox()
        self.set_fan_speed.setMinimum(0)
        self.set_fan_speed.setMaximum(4)

        self.glow_bulb1 = QtWidgets.QCheckBox(text="Glow bulb1?")
        self.glow_bulb2 = QtWidgets.QCheckBox(text="Glow bulb2?")
        self.read_news = QtWidgets.QCheckBox(text="Read news")

        self.saveImage = QtWidgets.QPushButton("Save data", clicked=self.save)

        self.capturedFrame.layout().addWidget(self.captured_img_lbl)
        self.capturedFrame.layout().addWidget(self.captured_img_dimensions)
        self.capturedFrame.layout().addWidget(self.error_lbl)
        self.capturedFrame.layout().addWidget(self.directory_edit)
        self.capturedFrame.layout().addWidget(self.save_as_lbl)
        self.capturedFrame.layout().addWidget(self.set_fan_speed)
        
        self.capturedFrame.layout().addWidget(self.glow_bulb1)
        self.capturedFrame.layout().addWidget(self.glow_bulb2)
        self.capturedFrame.layout().addWidget(self.read_news)
        
        self.capturedFrame.layout().addWidget(self.saveImage)

        self.capturedFrame.hide()

        self.camera_devices = QtWidgets.QComboBox()
        self.camera_devices.addItems([x.description() for x in QtMultimedia.QCameraInfo.availableCameras()])
        self.camera_devices.currentIndexChanged.connect(self.changeCameraDevice)

        self.draw_rect = QtWidgets.QPushButton("Capture Frame")
        self.draw_rect.setDisabled(True)
        self.draw_rect.clicked.connect(self.draw)

        self.camera_capture = QtWidgets.QPushButton("Start Capture")
        self.camera_capture.clicked.connect(self.toggleVideoCapture)

        self.layout().addWidget(self.capturedFrame)
        self.layout().addWidget(self.camera_devices)
        self.layout().addWidget(self.draw_rect)
        self.layout().addWidget(self.camera_capture)

        self.layout().addStretch(1)

    def toggleVideoCapture(self):  # starts and stops video capture
        self.capturing = not self.capturing

        if self.capturing:
            self.draw_rect.setDisabled(False)
            self.camera_capture.setText("Stop Capturing")

        else:
            self.draw_rect.setDisabled(True)
            self.camera_capture.setText("Start Capturing")

        self.capture.emit(self.capturing)

    def draw(self):  # emits signal when draw button is pressed
        self.drawingRect = not self.drawingRect
        self.drawRect.emit(self.drawingRect)

    def resetCameraCapture(self):
        self.draw_rect.setDisabled(True)
        self.capturing = False
        self.camera_capture.setText("Start Capturing")

    def changeCameraDevice(self, index):
        self.resetCameraCapture()
        self.cameraChanged.emit(index)

    def resetDraw(self):
        self.drawingRect = False

    def setCapturedImage(self, img: QtGui.QPixmap):  # shows the captured image in the widget
        self.capturedImage = img
        self.captured_img_dimensions.setText(f"{img.width()} X {img.height()}")
        self.captured_img_lbl.setPixmap(img)
        self.showCaptureOptions()
        self.resetDraw()

    def showCaptureOptions(self):
        self.capturedFrame.show()

    def hideCaptureOptions(self):
        self.capturedFrame.hide()

    def save(self):

        directory = self.directory_edit.text()
        save_image = self.save_as_lbl.text()

        if not os.path.isdir(directory):
            self.error_lbl.setText("Enter a valid directory")
            return

        if not save_image:
            self.error_lbl.setText("Enter a file name")

        path = os.path.join(directory, save_image)

        data = {
            "name": re.sub('[^A-Za-z0-9]+', '', save_image),
            "path": path+".jpeg",
            "preference": {
                "fanspeed": self.set_fan_speed.value(),
                "light1": self.glow_bulb1.isChecked(),
                "light2": self.glow_bulb2.isChecked(),
                "news": self.read_news.isChecked()
            }
        }

        previous_data = []


        with open(JSON_PATH,  encoding='utf-8', mode="r") as f_obj:
            try:
                previous_data = json.load(f_obj)
            
            except json.decoder.JSONDecodeError:
                pass

        previous_data.append(data)

        with open(JSON_PATH,  encoding='utf-8', mode="w") as f_obj:
            json.dump(previous_data, f_obj, indent=4)

        saved = self.capturedImage.save(path+".jpeg")

        if saved:
            self.error_lbl.setText(f"Saved to successfully to {path}")

        else:
            self.error_lbl.setText(f"Save unsuccessful")

        self.imgSaved.emit()

