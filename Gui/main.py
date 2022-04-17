import sys
from PyQt5 import QtWidgets
from SplitterWidget import SplitterWindow

import os

# os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH") # for linux users to use open cv with pyqt

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    win = SplitterWindow()
    win.setWindowTitle("S Homes")

    with open(r"GUI/Theme.qss", 'r') as read:
        win.setStyleSheet(read.read())

    win.show()

    sys.exit(app.exec())

