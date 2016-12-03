# coding=utf-8
import sys

import matplotlib
import numpy as np
from PyQt4 import QtCore
from PyQt4 import QtGui

matplotlib.use("Qt4Agg")
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import time
import threading

import bari

sensor = bari.Chip()

__author__ = 'Moe'
__copyright__ = 'Copyright 2016  Moe'
__license__ = 'MIT'
__version__ = '0.0.2'
# pinched and modified from http://stackoverflow.com/questions/11874767/real-time-plotting-in-while-loop-with-matplotlib

XLIMIT = 3000
YUPPER = 106000
YLOWER = 98000
SLEEP_FOR = .052  # Guesstimate for approx. 10 readings per second.


def setCustomSize(x, width, height):
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(x.sizePolicy().hasHeightForWidth())
    x.setSizePolicy(sizePolicy)
    x.setMinimumSize(QtCore.QSize(width, height))
    x.setMaximumSize(QtCore.QSize(width, height))


class CustomMainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(CustomMainWindow, self).__init__()

        # Define the geometry of the main window
        self.setGeometry(300, 300, 1000, 400)
        self.setWindowTitle("Drummoyne Wharf")

        # Create FRAME_A
        self.FRAME_A = QtGui.QFrame(self)
        self.FRAME_A.setStyleSheet("QWidget { background-color: %s }" % QtGui.QColor(210, 210, 235, 255).name())
        self.LAYOUT_A = QtGui.QGridLayout()
        self.FRAME_A.setLayout(self.LAYOUT_A)
        self.setCentralWidget(self.FRAME_A)
        #
        # self.button_test = QtGui.QPushButton(text='Test')
        # setCustomSize(self.button_test, 60, 30)
        # self.button_test.clicked.connect(self.test_me())
        self.buttonbox = QtGui.QHBoxLayout()
        # self.FRAME_A.setLayout(self.buttonbox)

        # IN button
        self.zoomInBtn = QtGui.QPushButton(text='In')
        setCustomSize(self.zoomInBtn, 60, 30)
        self.zoomInBtn.clicked.connect(self.zoomIn)
        self.LAYOUT_A.addWidget(self.zoomInBtn, *(1, 0))

        # OUT button
        self.zoomOutBtn = QtGui.QPushButton(text='Out')
        setCustomSize(self.zoomOutBtn, 60, 30)
        self.zoomOutBtn.clicked.connect(self.zoomOut)
        self.LAYOUT_A.addWidget(self.zoomOutBtn, *(1, 1))

        # x fewer button
        self.XfewerBtn = QtGui.QPushButton(text='Less')
        setCustomSize(self.XfewerBtn, 60, 30)
        self.XfewerBtn.clicked.connect(self.x_fewer)
        # self.buttonbox.addWidget(self.XfewerBtn, *(1, 0))

        # x more button
        self.XmoreBtn = QtGui.QPushButton(text='More')
        setCustomSize(self.XmoreBtn, 60, 30)
        self.XmoreBtn.clicked.connect(self.x_more)
        # self.buttonbox.addWidget(self.XmoreBtn, *(1, 1))

        # Place the matplotlib figure
        self.myFig = CustomFigCanvas()
        self.LAYOUT_A.addWidget(self.myFig, *(0, 1))

        # Add the callbackfunc to ..
        myDataLoop = threading.Thread(name='myDataLoop', target=dataSendLoop, daemon=True,
                                      args=(self.addData_callbackFunc,))
        myDataLoop.start()

        self.show()

    def zoomIn(self):
        print("IN zoom")
        self.myFig.zoomIn(1000)

    def zoomOut(self):
        print("zoom OUT")
        self.myFig.zoomOut(1000)

    def x_fewer(self):
        print("IN zoom")
        self.myFig.lessIn(500)

    def x_more(self):
        print("zoom OUT")
        self.myFig.moreOut(500)

    def addData_callbackFunc(self, value):
        # print("Add data: " + str(value))
        self.myFig.addData(value)


class CustomFigCanvas(FigureCanvas, TimedAnimation):
    def __init__(self):

        self.addedData = []
        print('Loading...', matplotlib.__version__)

        # The data
        self.xlim = XLIMIT
        self.n = np.linspace(self.xlim - 1, 0, self.xlim)

        self.y = (self.n * 0.0) + YLOWER

        # The window
        self.fig = Figure(figsize=(12, 2), dpi=80)
        self.ax1 = self.fig.add_subplot(111)

        # self.ax1 settings
        self.ax1.set_xlabel('Readings incremented time')
        self.ax1.set_ylabel('River Level - Raw data')
        self.line1 = Line2D([], [], color='blue', aa=True)
        self.line1_tail = Line2D([], [], color='red', linewidth=2)
        self.line1_head = Line2D([], [], color='red', marker='o', markeredgecolor='r')
        # self.line2 = Line2D([], [], linewidth=5, color='red', )

        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line1_tail)
        self.ax1.add_line(self.line1_head)
        # self.ax1.add_line(self.line2)
        self.ax1.set_xlim(0, self.xlim - 1)  # REVERSE GRAPHING X AXIS HERE
        self.ax1.set_ylim(YLOWER, YUPPER)

        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=50, blit=True)

    def new_frame_seq(self):
        return iter(range(self.n.size))

    def _init_draw(self):
        lines = [self.line1, self.line1_tail, self.line1_head]
        for l in lines:
            l.set_data([], [])

    def addData(self, value):
        self.addedData.append(value)

    def zoomIn(self, value):
        bottom = self.ax1.get_ylim()[0]
        top = self.ax1.get_ylim()[1]
        bottom += value
        top -= value
        self.ax1.set_ylim(bottom, top)
        self.draw()

    def zoomOut(self, value):
        bottom = self.ax1.get_ylim()[0]
        top = self.ax1.get_ylim()[1]
        bottom -= value
        top += value
        self.ax1.set_ylim(bottom, top)
        self.draw()

    def lessIn(self, value):
        left = self.ax1.get_xlim()[0]
        right = self.ax1.get_xlim()[1]
        # left += value
        right -= value
        self.ax1.set_xlim(left, right)
        self.draw()

    def moreOut(self, value):
        left = self.ax1.get_xlim()[0]
        right = self.ax1.get_xlim()[1]
        # left -= value
        right += value
        self.ax1.set_xlim(left, right)
        self.draw()

    def _step(self, *args):
        # Extends the _step() method for the TimedAnimation class.
        try:
            TimedAnimation._step(self, *args)
        except Exception as e:
            self.abc += 1
            print(str(self.abc))
            TimedAnimation._stop(self)
            pass

    def _draw_frame(self, framedata):
        margin = 2
        while (len(self.addedData) > 0):
            self.y = np.roll(self.y, -1)
            self.y[-1] = self.addedData[0]
            del (self.addedData[0])
            # np.ro

        self.line1.set_data(self.n[0: self.n.size - margin], self.y[0: self.n.size - margin])
        self.line1_tail.set_data(np.append(self.n[-100:-1 - margin], self.n[-1 - margin]),
                                 np.append(self.y[-100:-1 - margin], self.y[-1 - margin]))
        self.line1_head.set_data(self.n[-1 - margin], self.y[-1 - margin])

        # self.line2.set_data(self.n[1: self.n.size - margin], self.y[1: self.n.size - margin])
        self._drawn_artists = [self.line1, self.line1_tail, self.line1_head]  # , self.line2]


        # self.line2_tail.set_data(np.append(self.n[-10:-1 - margin], self.n[-1 - margin]),
        #                          np.append(self.y[-10:-1 - margin], self.y[-1 - margin]))
        # self.line2_head.set_data(self.n[-1 - margin], self.y[-1 - margin])
        # self._drawn_artists = [self.line2]


class Communicate(QtCore.QObject):
    data_signal = QtCore.pyqtSignal(float)


def dataSendLoop(addData_callbackFunc):
    # Setup the signal-slot mechanism.
    mySrc = Communicate()
    mySrc.data_signal.connect(addData_callbackFunc)

    n = np.linspace(0, 499, 500)
    i = 0

    while (True):
        if (i > 499):
            i = 0
        # pressure, _temperature = sensor.bari()
        pressure, _temperature = sensor.bari()
        ##############
        time.sleep(SLEEP_FOR)  # (.052)  # Guestimated 1/10 second readinging with 5367 Chip lag

        mySrc.data_signal.emit(pressure)  # <- Here you emit a signal!
        i += 1


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Plastique'))
    myGUI = CustomMainWindow()

    sys.exit(app.exec_())
