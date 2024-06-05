import sys
import serial
import signal
import time
import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.exporters import ImageExporter
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
from collections import deque
from datetime import datetime as date

arduinoPort = "/dev/cu.usbmodemF412FA75E7882"
# arduinoPort = "/dev/tty.usbmodem1101"

class SerialHistogram(QtWidgets.QWidget):
    def __init__(self, port, baudrate=9600, parent=None):
        super(SerialHistogram, self).__init__(parent)
        self.serial_port = serial.Serial(port, baudrate, timeout=1)
        self.time_differences = deque(maxlen=1000000)
        self.timeStamps = deque(maxlen=1000000)

        self.maxXRangeExp = 1000  # Default max X-axis range
        self.numBinsExp = 20 # Default number of bins for Exp
        self.timeIntervalPoisson = 730 # Default time interval for Poisson
        self.setupUi()
        self.setupSerial()

        # Get the directory of the currently running script
        script_directory = os.path.dirname(os.path.realpath(__file__))

        # Define the folder path for saving data
        folder_path = os.path.join(script_directory, 'Data')

        # Create the 'Data' directory if it does not exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Create the file within the specified folder
        file_path = os.path.join(folder_path, f"GeigerDataset_{date.today()}.txt")
        self.file = open(file_path, "w")


    def setupUi(self):
        self.setWindowTitle('Geiger Counter')
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
        self.exponentialPlotWidget.setLabel('left', 'Absolute frequency')
        self.exponentialPlotWidget.setLabel('bottom', 'Time between counts (ms)')
        self.exponentialPlotWidget.showGrid(x=True, y=True)
        self.exponentialPlotWidget.setBackground('#FFFFFF')

        # Button X-axis range
        self.changeXAxisButtonExp = QtWidgets.QPushButton("Change X-axis Range")
        self.exponentialLayout.addWidget(self.changeXAxisButtonExp)
        self.changeXAxisButtonExp.setStyleSheet(button_style)
        self.changeXAxisButtonExp.clicked.connect(self.changeXAxisRangeExp)

        # Button number of bins
        self.changeBinsButtonExp = QtWidgets.QPushButton("Change Number of Bins")
        self.exponentialLayout.addWidget(self.changeBinsButtonExp)
        self.changeBinsButtonExp.setStyleSheet(button_style)
        self.changeBinsButtonExp.clicked.connect(self.changeNumberOfBinsExp)

        # Button to clear the plot
        self.clearPlotButtonExp = QtWidgets.QPushButton("Clear Plot")
        self.exponentialLayout.addWidget(self.clearPlotButtonExp)
        self.clearPlotButtonExp.setStyleSheet(button_style)
        self.clearPlotButtonExp.clicked.connect(self.clearPlotExp)

        # Button to save the plot
        self.savePlotButtonExp = QtWidgets.QPushButton("Save Plot")
        self.exponentialLayout.addWidget(self.savePlotButtonExp)
        self.savePlotButtonExp.setStyleSheet(button_style)
        self.savePlotButtonExp.clicked.connect(self.savePlotExp)

        """Poisson Histogram Controls"""
        # Layout for the new counts plot
        self.poissonLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addLayout(self.poissonLayout)

        # Plot for the new counts
        self.poissonPlotWidget = pg.PlotWidget()
        self.poissonLayout.addWidget(self.poissonPlotWidget)
        self.poissonPlotWidget.setTitle("Poisson Distribution of Counts per Time Interval")
        self.poissonPlotWidget.setLabel('left', 'Count of events')
        self.poissonPlotWidget.setLabel('bottom', 'Time (s)')
        self.poissonPlotWidget.showGrid(x=True, y=True)
        self.poissonPlotWidget.setBackground('#FFFFFF')

        # Button X-axis range
        self.changeXAxisButtonPoisson = QtWidgets.QPushButton("Change X-axis Range")
        self.poissonLayout.addWidget(self.changeXAxisButtonPoisson)
        self.changeXAxisButtonPoisson.setStyleSheet(button_style)
        self.changeXAxisButtonPoisson.clicked.connect(self.changeXAxisRangePoisson)

        # Button number of bins
        self.changeBinsButtonPoisson = QtWidgets.QPushButton("Change Time Interval")
        self.poissonLayout.addWidget(self.changeBinsButtonPoisson)
        self.changeBinsButtonPoisson.setStyleSheet(button_style)
        self.changeBinsButtonPoisson.clicked.connect(self.changeTimeIntervalPoisson)

        # Button to clear the plot
        self.clearPlotButtonPoisson = QtWidgets.QPushButton("Clear Plot")
        self.poissonLayout.addWidget(self.clearPlotButtonPoisson)
        self.clearPlotButtonPoisson.setStyleSheet(button_style)
        self.clearPlotButtonPoisson.clicked.connect(self.clearPlotPoisson)

        # Button to save the plot
        self.savePlotButtonPoisson = QtWidgets.QPushButton("Save Plot")
        self.poissonLayout.addWidget(self.savePlotButtonPoisson)
        self.savePlotButtonPoisson.setStyleSheet(button_style)
        self.savePlotButtonPoisson.clicked.connect(self.savePlotPoisson)

    def setupSerial(self):
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.updateExponential)
        self.timer.timeout.connect(self.updatePoisson)
        self.timer.start(self.timeIntervalPoisson*3)  # Update interval in milliseconds

    def getData(self):
        try:
            while self.serial_port.inWaiting() > 0:
                line = self.serial_port.readline().decode("utf-8").rstrip()
                if line:
                    peak, time_stamp, time_since_last_pulse = map(int, line.split())

                    self.time_differences.append(time_since_last_pulse) # ms
                    self.timeStamps.append(time_stamp)

                    # Write data to file
                    self.writeDataToFile(peak, time_stamp, time_since_last_pulse)

            self.file.flush() # Ensure data is written to disk

        except Exception as e:
            print(f"Error in getData: {e}")

    def writeDataToFile(self, peak, time_stamp, time_since_last_pulse):
        """Write acquired data to file."""

        # Unix timestamp in seconds
        current_time = int(time.time())

        # Format: count; unix_time_seconds (s); peak (mV); time_stamp(μs); time_since_last_pulse (μs)
        line = f"{len(self.time_differences)} {current_time} {peak} {time_stamp} {time_since_last_pulse}\n"
        self.file.write(line)

    def closeEvent(self, event):
        """Ensures the file is closed properly"""
        self.file.close()
        self.serial_port.close()
        super(SerialHistogram, self).closeEvent(event)

    """Exponential funtions"""
    def updateExponential(self):
        """Updates the exponential plot based on the collected time differences."""
        self.getData()
        if len(self.time_differences) > 0:
            y, x = np.histogram(list(self.time_differences), bins=self.numBinsExp, range=(12, self.maxXRangeExp))
            self.exponentialPlotWidget.clear()
            self.exponentialPlotWidget.plot(x, y, stepMode=True, fillLevel=0, brush=pg.mkBrush('#374c80'))

    def changeXAxisRangeExp(self):
        maxXRange, ok = QtWidgets.QInputDialog.getInt(self, "Change X-axis Range", "Enter new max X-axis value (ms):", value=self.maxXRangeExp, min=500)
        if ok:
            self.maxXRangeExp = maxXRange
            self.updateExponential()  # Update histogram to reflect new X-axis range immediately

    def changeNumberOfBinsExp(self):
        numBins, ok = QtWidgets.QInputDialog.getInt(self, "Change Number of Bins", "Enter new number of bins:", value=self.numBinsExp, min=1)
        if ok:
            self.numBinsExp = numBins
            self.updateExponential()  # Update histogram to reflect new number of bins immediately

    def clearPlotExp(self):
        """Clear the plot and the underlying data."""
        self.exponentialPlotWidget.clear()  # This clears the visual plot
        self.time_differences.clear()


    def updatePoisson(self):
        """Updates the Poisson plot based on the counts accumulated in fixed time intervals, excluding the last incomplete interval."""
        self.getData()
        if len(self.timeStamps) > 0:
            interval_size = self.timeIntervalPoisson  # Assume this is set to a value like 1000 milliseconds

            # Determine the time range from the first to the last timestamp
            first_timestamp = self.timeStamps[0]
            last_timestamp = self.timeStamps[-1]

            # Calculate the total number of intervals, considering only completed intervals
            num_intervals = (last_timestamp - first_timestamp) // interval_size
            counts = [0] * num_intervals

            # Count the timestamps in each interval
            for ts in self.timeStamps:
                interval_index = (ts - first_timestamp) // interval_size
                if interval_index < num_intervals:  # This ensures we do not count into the last, potentially unfinished interval
                    counts[interval_index] += 1

            # Update the Poisson plot with new data
            self.poissonPlotWidget.clear()

            # Calculate bin edges from 0 to the max number of counts found, plus one extra bin
            max_count = max(counts) if counts else 0
            count_bins = np.arange(0, max_count + 2)  # +2 to include the last bin edge
            count_frequencies, bin_edges = np.histogram(counts, bins=count_bins)

            # Correct plotting call, ensure that data plotted does not include the last incomplete interval
            self.poissonPlotWidget.plot(bin_edges, count_frequencies, stepMode=True, fillLevel=0, brush=pg.mkBrush('#374c80'))

    def changeXAxisRangePoisson(self):
        maxXRange, ok = QtWidgets.QInputDialog.getInt(self, "Change X-axis Range", "Enter new max X-axis value (ms):", value=self.maxXRangeExp, min=1, max=50)
        if ok:
            self.maxXRangeExp = maxXRange
            self.updateExponential()  # Update histogram to reflect new X-axis range immediately

    def changeTimeIntervalPoisson(self):
        numBins, ok = QtWidgets.QInputDialog.getInt(self, "Change Poisson Time Interval", "Enter new time interval:", value=self.timeIntervalPoisson, min=10, max=20000)
        if ok:
            self.timeIntervalPoisson = numBins
            self.updatePoisson()  # Update histogram to reflect new number of bins immediately

    def clearPlotPoisson(self):
        """Clear the plot and the underlying data."""
        self.poissonPlotWidget.clear()  # This clears the visual plot
        self.timeStamps.clear()

    def savePlot(self, plotWidget, defaultName="plot"):
        """Save the current plot to a file."""
        # Get the directory of the currently running script
        script_directory = os.path.dirname(os.path.realpath(__file__))

        # Define the folder path for saving plots
        folder_path = os.path.join(script_directory, 'Plots')

        # Create the 'Plots' directory if it does not exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Format the file name with the current date
        today_date = date.today().strftime("%Y-%m-%d")
        fileName = os.path.join(folder_path, f"{defaultName}_{today_date}.png")

        try:
            exporter = pg.exporters.ImageExporter(plotWidget.plotItem)
            exporter.export(fileName)
            QMessageBox.information(self, "Success", "Plot saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save the file: {str(e)}")
            print(f"Error saving the plot: {e}")

    def savePlotExp(self):
        """Save the current exponential plot to a file."""
        self.savePlot(self.exponentialPlotWidget, "exponential")

    def savePlotPoisson(self):
        """Save the current Histogram plot to a file."""
        self.savePlot(self.poissonPlotWidget, "poisson")

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL) # ^C works this way

    app = QtWidgets.QApplication(sys.argv)
    window = SerialHistogram(arduinoPort)
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec_())