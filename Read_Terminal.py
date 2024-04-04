import sys
import serial
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtGui, QtCore
from collections import deque

#from MouseHover import CustomPlotWidget

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
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.mainLayout)

        button_style = ("QPushButton {"
                        "background-color: #FFFFFF;"
                        "color: #374c80;"
                        "border-radius: 5px;"
                        "padding: 6px;"
                        "}")

        """Exponential Histogram Controls"""
        # Layout for histogram
        self.exponentialLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addLayout(self.exponentialLayout)

        # Plot for histogram
        self.exponentialPlotWidget = pg.PlotWidget()
        self.exponentialLayout.addWidget(self.exponentialPlotWidget)
        self.exponentialPlotWidget.setTitle("Histogram of Time Between Detections")
        self.exponentialPlotWidget.showGrid(x=True, y=True)
        self.exponentialPlotWidget.setBackground('#FFFFFF')

        # Button X-axis range
        self.changeXAxisButton = QtWidgets.QPushButton("Change X-axis Range")
        self.exponentialLayout.addWidget(self.changeXAxisButton)
        self.changeXAxisButton.setStyleSheet(button_style)
        self.changeXAxisButton.clicked.connect(self.changeXAxisRange)

        # Button number of bins
        self.changeBinsButton = QtWidgets.QPushButton("Change Number of Bins")
        self.exponentialLayout.addWidget(self.changeBinsButton)
        self.changeBinsButton.setStyleSheet(button_style)
        self.changeBinsButton.clicked.connect(self.changeNumberOfBins)

        # Button to clear the plot
        self.clearPlotButton = QtWidgets.QPushButton("Clear Plot")
        self.exponentialLayout.addWidget(self.clearPlotButton)
        self.clearPlotButton.setStyleSheet(button_style)
        self.clearPlotButton.clicked.connect(self.clearPlot)

        # Button to save the plot
        self.savePlotButton = QtWidgets.QPushButton("Save Plot")
        self.exponentialLayout.addWidget(self.savePlotButton)
        self.savePlotButton.setStyleSheet(button_style)
        self.savePlotButton.clicked.connect(self.savePlot)

        """Poisson Histogram Controls"""
        # Layout for the new counts plot
        self.poissonLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addLayout(self.poissonLayout)

        # Plot for the new counts
        self.poissonPlotWidget = pg.PlotWidget()
        self.poissonLayout.addWidget(self.poissonPlotWidget)
        self.poissonPlotWidget.setTitle("Histogram of Counts per Interval")
        self.poissonPlotWidget.showGrid(x=True, y=True)
        self.poissonPlotWidget.setBackground('#FFFFFF')

        # Button X-axis range
        self.changeXAxisButton = QtWidgets.QPushButton("Change X-axis Range")
        self.poissonLayout.addWidget(self.changeXAxisButton)
        self.changeXAxisButton.setStyleSheet(button_style)
        self.changeXAxisButton.clicked.connect(self.changeXAxisRange)

        # Button number of bins
        self.changeBinsButton = QtWidgets.QPushButton("Change Number of Bins")
        self.poissonLayout.addWidget(self.changeBinsButton)
        self.changeBinsButton.setStyleSheet(button_style)
        self.changeBinsButton.clicked.connect(self.changeNumberOfBins)

        # Button to clear the plot
        self.clearPlotButton = QtWidgets.QPushButton("Clear Plot")
        self.poissonLayout.addWidget(self.clearPlotButton)
        self.clearPlotButton.setStyleSheet(button_style)
        self.clearPlotButton.clicked.connect(self.clearPlot)

        # Button to save the plot
        self.savePlotButton = QtWidgets.QPushButton("Save Plot")
        self.poissonLayout.addWidget(self.savePlotButton)
        self.savePlotButton.setStyleSheet(button_style)
        self.savePlotButton.clicked.connect(self.savePlot)

    def setupSerial(self):
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.updateHistogram)
        self.timer.start(1000)  # Update interval in milliseconds

    def updateHistogram(self):
        try:
            while self.serial_port.inWaiting() > 0:
                line = self.serial_port.readline().decode("utf-8").rstrip()
                _, time_since_last_pulse, _ = line.split(" ")
                time_since_last_pulse = float(time_since_last_pulse)
                self.time_differences.append(time_since_last_pulse)

        except Exception as e:
            print(f"Error: {e}")

        if len(self.time_differences) > 0:
            y, x = np.histogram(list(self.time_differences), bins=self.numBins, range=(25, self.maxXRange))
            self.exponentialPlotWidget.clear()
            self.exponentialPlotWidget.plot(x, y, stepMode=True, fillLevel=0, brush=pg.mkBrush('#374c80'))

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

    def clearPlot(self):
        """Clear the plot and the underlying data."""
        self.exponentialPlotWidget.clear()  # This clears the visual plot
        self.time_differences.clear()

    def savePlot(self):
        """Save the current plot to a file."""
        # Define the file name and format. For example, 'histogram.png'
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Plot", "", "PNG Image (*.png);;All Files (*)")
        if fileName:
            exporter = pg.exporters.ImageExporter(self.exponentialPlotWidget.plotItem)
            exporter.export(fileName)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SerialHistogram("/dev/cu.usbmodemF412FA75E7882")
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec_())
