import os
import json
from PyQt5 import QtWidgets, QtCore, QtGui

import requests
import pyttsx3
import json
from dotenv import load_dotenv


from VideoCaptureWidget import VideoCaptureDisplayWidget
from ControlPanel import ControlPanel

load_dotenv()

engine = pyttsx3.init()

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[16].id)  

JSON_PATH = os.path.join(os.getcwd(), "data/data.json")

class SplitterWindow(QtWidgets.QWidget):

    # This is the widget were all the other widgets such as VideoCaptureDisplayWidget and ControlPanel are placed
    # This also acts as a control class sending signals back and forth between two classes

    def __init__(self, *args, **kwargs):
        super(SplitterWindow, self).__init__(*args, **kwargs)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        self.control_panel = ControlPanel()
        self.control_panel.capture.connect(self.switchCapturing)
        self.control_panel.drawRect.connect(self.toggleDrawingRect)
        self.control_panel.cameraChanged.connect(self.changeCameraDevice)
        self.control_panel.setMaximumWidth(600)

        self.video = VideoCaptureDisplayWidget()
        self.video.capturedImage.connect(self.displayCaptured)
        self.video.cameraFailed.connect(self.control_panel.resetCameraCapture)
        self.video.foundFaces.connect(self.load)

        self.control_panel.imgSaved.connect(self.video.reload_data)

        splitter.addWidget(self.video)
        splitter.addWidget(self.control_panel)

        self.layout().addWidget(splitter)

        self.user_preference = []
        self.previous_faces = []

    def switchCapturing(self, capture: bool):  # starts and stops video captures

        if capture:
            self.video.start()

        else:
            self.video.stop()

    def changeCameraDevice(self, index):
        self.video.stop()
        self.video.setCameraDevice(index)

    def toggleDrawingRect(self, draw: bool):  # starts and stops drawing

        if draw:
            self.video.drawRect()

        else:
            self.video.stopDrawing()

    def displayCaptured(self, capturedImage: QtGui.QImage):  # shows the capture image
        self.control_panel.setCapturedImage(QtGui.QPixmap(capturedImage))

    def closeEvent(self, event) -> None:
        # print("destroying...")
        self.video.stop()
        super(SplitterWindow, self).closeEvent(event)

    
    def load(self, faces):
        
        if self.previous_faces == faces:
            return

        print("Previosu: faces: ", self.previous_faces)
        self.previous_faces = faces

        with open(JSON_PATH,  encoding='utf-8', mode="r") as f_obj:
            try:
                self.user_preference = json.load(f_obj)
            
            except json.decoder.JSONDecodeError:
                pass
        
        self.change_ambinence(faces)

    def change_ambinence(self, faces):
        # change the room ambience according to the user

        if not faces:
            return 

        face = faces[-1]

        # print(self.user_preference)
        for x in self.user_preference:
            if x["name"] == face:
                if x["preference"]["news"]:
                    self.news = NewsReader()
                    # news.exec()
                    self.news.start()

                    # break 

class NewsReader(QtCore.QThread):

    finished_reading = QtCore.pyqtSignal()


    def run(self) -> None:
    
        try:
            res = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={ os.getenv('newsAPI')}&pageSize=3")

            for x in res.json()["articles"]:
                pyttsx3.speak(x["title"])

            
        except Exception as e:
            print("error occurred: ", e)
            pyttsx3.speak("An error occured")