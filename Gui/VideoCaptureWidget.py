import os
import cv2
import json
import numpy as np
import face_recognition

from PyQt5 import QtWidgets, QtCore, QtGui


class VideoCaptureDisplayWidget(QtWidgets.QWidget):

    # Displays image frame by frame

    capturedImage = QtCore.pyqtSignal(QtGui.QImage)  # emits the captured image
    cameraFailed = QtCore.pyqtSignal()

    foundFaces = QtCore.pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        super(VideoCaptureDisplayWidget, self).__init__(*args, **kwargs)

        self.setLayout(QtWidgets.QVBoxLayout())

        self.img_label = DrawLabel()
        self.img_label.drawingComplete.connect(self.extractImageFromRect)
        self.img_label.drawingComplete.connect(self.stopDrawing)
        self.img_label.setText("Click capture to display")
        self.img_label.setScaledContents(True)
        
        self.layout().addWidget(self.img_label)
        self.capture = None
        self.cameraDevice = 0

    def updateImage(self, img): # changes the current frame
        self.img_label.setPixmap(QtGui.QPixmap.fromImage(img))

    def start(self):
        self.img_label.setText("")
        self.capture = Capture(self.cameraDevice)
        self.capture.frameChanged.connect(self.updateImage)
        self.capture.cameraFailed.connect(self.cameraUnsuccessful)
        self.capture.facesFound.connect(self.foundFaces.emit)
        self.capture.start()

    def cameraUnsuccessful(self):
        self.stop()
        self.cameraFailed.emit()
        self.img_label.clear()
        self.img_label.setText("Camera Failed")

    def stop(self):

        if self.capture:
            self.capture.stop()
            self.capture.quit()
            self.capture = None

    def drawRect(self):  # enables draw rect
        self.img_label.startDraw()
        self.capture.is_drawing = True

    def stopDrawing(self):  # stops drawing
        self.img_label.stopDraw()
        self.capture.is_drawing = False

    def extractImageFromRect(self):  # emits the image inside the drawn rect
        pixmap = self.img_label.pixmap()

        image = pixmap.copy(self.img_label.drawingRect().toRect()).toImage()
        self.capturedImage.emit(image)
        self.img_label.stopDraw()

    def setCameraDevice(self, index):
        self.cameraDevice = index


    def reload_data(self):
        self.capture.reload_data()


class Capture(QtCore.QThread): # capture video frame by frame

    frameChanged = QtCore.pyqtSignal(QtGui.QImage)  # emits new image
    cameraFailed = QtCore.pyqtSignal() # emits when the camera was unsuccessful

    facesFound = QtCore.pyqtSignal(list)

    def __init__(self, cameraDevice=0, *args, **kwargs):
        super(Capture, self).__init__(*args, **kwargs)
        self.cameraDevice = cameraDevice

        self.img_recog = ImageRecognition()
        self.img_recog.facesFound.connect(self.facesFound.emit)

        self.is_drawing = False

    def run(self) -> None:
        self.cap = cv2.VideoCapture(self.cameraDevice)

        if not self.cap.isOpened():
            self.cameraFailed.emit()
            return

        process_frame = 0

        while not self.isInterruptionRequested():

            ret, frame = self.cap.read()

            if process_frame == 3:
                process_frame = 0

            if process_frame == 0:

                frame = self.img_recog.read_frame(frame, not self.is_drawing)

                if ret:
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QtGui.QImage(rgbImage.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
                    pix = convertToQtFormat.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
                    self.frameChanged.emit(pix)

            process_frame += 1

        self.cap.release()

    def stop(self):
        self.requestInterruption()
        self.wait()

    def reload_data(self):
        self.img_recog.load()

class DrawLabel(QtWidgets.QLabel):  # Enables user to draw over the image

    drawingComplete = QtCore.pyqtSignal()  # emits when mouse released when drawing

    def __init__(self, *args, **kwargs):
        super(DrawLabel, self).__init__(*args, **kwargs)
        self.draw = False
        self._isdrawing = False
        self._drawingRect = QtCore.QRectF()

        self.penColor = QtGui.QColor("#06c42c")
        self._penWidth = 2

    def setPenWidth(self, penwidth: float):
        self._penWidth = penwidth

    def setPenColor(self, color):
        self.penColor = QtGui.QColor(color)

    def startDraw(self):
        self.draw = True
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

    def stopDraw(self):
        self.draw = False
        self._drawingRect = QtCore.QRectF()
        self.setCursor(QtGui.QCursor())

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:

        if self.draw:
            pos = event.pos()
            self._isdrawing = True
            self._drawingRect.setRect(pos.x(), pos.y(), pos.x(), pos.y())

        else:
            super(DrawLabel, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:

        if self._isdrawing:
            self._drawingRect.setBottomRight(event.pos())

        else:
            super(DrawLabel, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:

        if self._isdrawing:
            self._drawingRect.setBottomRight(event.pos())
            self._isdrawing = False
            self.drawingComplete.emit()

        else:
            super(DrawLabel, self).mouseReleaseEvent(event)

    def drawingRect(self):
        return self._drawingRect

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        super(DrawLabel, self).paintEvent(event)

        if self.draw:
            painter = QtGui.QPainter(self)
            painter.setPen(self.penColor)
            painter.pen().setWidthF(self._penWidth)
            painter.drawRect(self.drawingRect())
            self.update()


class ImageRecognition(QtCore.QObject):

    facesFound = QtCore.pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        super(ImageRecognition, self).__init__(*args, **kwargs)

        self.data = []
        self.known_face_encodings = []
        self.known_names = []
        self.load()

    def load(self):

        with open(os.path.join(os.getcwd(), 'data', 'data.json')) as f_obj:
            try:
                self.data = json.load(f_obj)
                
            except json.decoder.JSONDecodeError:
                print("decoding error...")

        for x in self.data:

            image_load = face_recognition.load_image_file(x["path"]) 
            img_encoding = face_recognition.face_encodings(image_load)

            if img_encoding:
                self.known_face_encodings.append(img_encoding[0])
                self.known_names.append(x["name"])

        
    def read_frame(self, frame, draw_frame=True):

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.15, fy=0.15)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        # if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame, model="cnn")
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            if self.known_face_encodings:
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    name = self.known_names[best_match_index]

            face_names.append(name)

        # if face_names:
        self.facesFound.emit(face_names)
        # process_this_frame = not process_this_frame
        
        if draw_frame:
            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 7
                right *= 7
                bottom *= 7
                left *= 7

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)


        return frame