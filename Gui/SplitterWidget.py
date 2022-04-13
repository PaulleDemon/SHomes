from PyQt5 import QtWidgets, QtCore, QtGui

from VideoCaptureWidget import VideoCaptureDisplayWidget
from ControlPanel import ControlPanel


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

        self.control_panel.imgSaved.connect(self.video.reload_data)

        splitter.addWidget(self.video)
        splitter.addWidget(self.control_panel)

        self.layout().addWidget(splitter)

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