import os
import json
from PyQt5 import QtWidgets, QtCore, QtGui

import json
import serial
import pyttsx3
import requests

import datetime
import threading

from dotenv import load_dotenv


from VideoCaptureWidget import VideoCaptureDisplayWidget
from ControlPanel import ControlPanel

load_dotenv()

engine = pyttsx3.init()

# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[16].id) 
engine.setProperty('voice', 'english+f4')
engine.setProperty('rate', 120)
 

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

        self.instruction_executor = InstructionsExecutor()
        self.instruction_executor.setTerminationEnabled(True)
        self.instruction_executor.start()

        # self.reader = Reader()
        # self.reader.start()

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

        # print("Previosu: faces: ", self.previous_faces)

        with open(JSON_PATH,  encoding='utf-8', mode="r") as f_obj:
            try:
                self.user_preference = json.load(f_obj)
            
            except json.decoder.JSONDecodeError:
                pass
        
        self.change_ambinence(faces)
        self.previous_faces = faces

    def greet_user(self, user: str, read_news:bool = False):

        now = datetime.datetime.now()
        hour = now.hour

        if hour < 12:
            greeting = "Good morning"
        
        elif hour < 16:
            greeting = "Good afternoon"
        
        else:
            greeting = "Good evening"

        print("Spekaing")
        # self.reader.speak(greeting)
        pyttsx3.speak(greeting+user)

        pyttsx3.speak("Changing room ambience to your preference")
        
        print("spoke")

        if read_news:
            self.news = NewsReader()     
            self.news.start()



    def change_ambinence(self, faces):
        # change the room ambience according to the user
        
        if not faces:
            self.instruction_executor.setInstruction("off")
            return

        # if faces == self.previous_faces and not self.previous_faces:
        #     return 

        print("Face found...")


        face = faces[-1]


        for x in self.user_preference:
            if x["name"] == face:
                
                if faces != self.previous_faces: 
                    thread = threading.Thread(target=self.greet_user, args=(x["name"], x["preference"]["news"]))
                    thread.start()
            
                self.instruction_executor.setInstruction(json.dumps(x["preference"]))

                break

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.instruction_executor.setInstruction("off")
        self.instruction_executor.requestInterruption()
        self.instruction_executor.wait()
        print("Closing...")
        return super().closeEvent(a0)


class NewsReader(QtCore.QThread):

    finished_reading = QtCore.pyqtSignal()


    def run(self) -> None:
        """ using newsapi.org, please register with newsapi and place the API key in .env file or register in 
        system environment variables """
        try:
            res = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={ os.getenv('newsAPI')}&pageSize=3")

            pyttsx3.speak("Reading your top headlines")
            self.usleep(500)
            for x in res.json()["articles"]:
                pyttsx3.speak(x["title"])
                self.msleep(1)

            
        except Exception as e:
            print("error occurred: ", e)
            pyttsx3.speak("An error occured trying to read news")



class InstructionsExecutor(QtCore.QThread):
    completedInstruction = QtCore.pyqtSignal(bool)  # sent when instruction execution is complete
    connectionStatus = QtCore.pyqtSignal(str) 

    #NOTE: The com port for linux would be something like "/dev/ttyACM0" for windows use something like "COM3"
    def __init__(self, com: str="COM3", baud: int=9600, *args, **kwargs): # the com port for linux "/dev/ttyACM0", windows use COM3
        super(InstructionsExecutor, self).__init__(*args, **kwargs)
        self.com = com
        self.baud = baud
        self.instruction = ""
        self.serial_port = None

        # print(repr(com), baud, repr(baud))

    def run(self) -> None:
        print("STARTING INSTRUCTION....")
        self.connectionStatus.emit("Connecting...")

        try:
            self.serial_port = serial.Serial(self.com, self.baud, timeout=2)
            self.serial_port.stopbits = 2
            self.connectionStatus.emit("connection success")

        except serial.serialutil.SerialException as e:
            self.connectionStatus.emit(str(e))
            print("error occurred trying to connect to the given port", e)
            return

        while not self.isInterruptionRequested():

            if self.instruction: 
                self.serial_port.write(bytes(self.instruction, "utf-8"))

            # print("Instruction: ", bytes(self.instruction, "utf-8"))

            try:
                read = self.serial_port.readline()
                
                print("read: ", read.decode())
                # if read and read == b"done":
                #     self.completedInstruction.emit(True)
                #     self.instruction = ""

            except serial.SerialException:
                pass
        
        self.serial_port.write(bytes(self.instruction, "utf-8"))
        print("Disconnected")
        self.serial_port.close()
        self.connectionStatus.emit("Disconnected")

    def setInstruction(self, instruction):
        print("Set instructinos: ", instruction)
        self.instruction = instruction