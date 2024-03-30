import sys
import serial
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtGui, QtCore
from collections import deque

class SerialHistogram(QtWidgets.QWidget):
    def __init__(self, port, baudrate=9600, parent=None):
        super(SerialHistogram, self).__init__(parent)
        self.serial_port = serial.Serial(port, baudrate)
        self.time_differences = deque(maxlen=100000)

        self.maxXRange = 1000  # Default max X-axis range
        self.numBins = 20 # Default number of bins
        self.setupUi()
        self.setupSerial()

    def setupUi(self):
        button_style = ("QPushButton {"
                        "background-color: #FFFFFF;"
                        "color: #374c80;"
                        "border-radius: 5px;"
                        "padding: 6px;"
                        "}")

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.plotWidget = pg.PlotWidget()
        self.layout.addWidget(self.plotWidget)
        self.plotWidget.setTitle("Histogram of Time Between Detections")
        self.plotWidget.showGrid(x=True, y=True)

        # Changing X-axis range
        self.changeXAxisButton = QtWidgets.QPushButton("Change X-axis Range")
        self.layout.addWidget(self.changeXAxisButton)
        self.changeXAxisButton.setStyleSheet(button_style)
        self.changeXAxisButton.clicked.connect(self.changeXAxisRange)

        # Changing number of bins
        self.changeBinsButton = QtWidgets.QPushButton("Change Number of Bins")
        self.layout.addWidget(self.changeBinsButton)
        self.changeBinsButton.setStyleSheet(button_style)
        self.changeBinsButton.clicked.connect(self.changeNumberOfBins)

        self.changeXAxisButton.clicked.connect(self.changeXAxisRange)
        self.plotWidget.setBackground('#FFFFFF')

    def setupSerial(self):
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.updateHistogram)
        self.timer.start(1000)  # Update interval in milliseconds

    def updateHistogram(self):
        try:
            while self.serial_port.inWaiting() > 0:
                line = self.serial_port.readline().decode("utf-8").rstrip()
                _, time_since_last_pulse, _ = line.split(" ")
                self.time_differences.append(float(time_since_last_pulse))

        except Exception as e:
            print(f"Error: {e}")

        if len(self.time_differences) > 0:
            y, x = np.histogram(list(self.time_differences), bins=self.numBins, range=(0, self.maxXRange))
            self.plotWidget.clear()
            self.plotWidget.plot(x, y, stepMode=True, fillLevel=0, brush=pg.mkBrush('#374c80'))

    def changeXAxisRange(self):
        maxXRange, ok = QtWidgets.QInputDialog.getInt(self, "Change X-axis Range", "Enter new max X-axis value (ms):", value=self.maxXRange, min=500)
        if ok:
            self.maxXRange = maxXRange
            self.updateHistogram()  # Update histogram to reflect new X-axis range immediately

    def changeNumberOfBins(self):
        numBins, ok = QtWidgets.QInputDialog.getInt(self, "Change Number of Bins", "Enter new number of bins:", value=self.numBins, min=1)
        if ok:
            self.numBins = numBins
            self.updateHistogram()  # Update histogram to reflect new number of bins immediately

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SerialHistogram("/dev/cu.usbmodemF412FA75E7882")
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec_())
