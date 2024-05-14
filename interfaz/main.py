"""Display an interface to filter audio files and view the results."""

import sys

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from scipy.io import wavfile

from filters import fir_filter, iir_filter


class MainWindow(QWidget):
    """Main window for the filtering GUI."""

    def __init__(self):
        """Initialize main window."""
        super().__init__()
        self.original()

    def original(self):
        """Initialyze the main layouts and geometry."""
        self.setGeometry(300, 300, 1100, 700)

        # Main horizontal layout
        main_layout = QHBoxLayout()

        # Layout for left side
        left_layout = QGridLayout()
        self.populate_left_layout(left_layout)

        # Layout for right side
        right_layout = QGridLayout()
        self.populate_right_layout(right_layout)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
        self.setWindowTitle("Filtering GUI")

    def populate_left_layout(self, layout):
        """Adding widgets to the left side."""
        # Create a QMediaPlayer object
        self.mediaPlayer = QMediaPlayer()
        # Initialize tab widget
        self.tabWidget = QTabWidget()

        # Button to select audio file in the first row
        self.selectButton = QPushButton("Select File", self)
        self.selectButton.setFixedSize(200, 50)
        layout.addWidget(self.selectButton, 0, 0, 2, 1)
        self.selectButton.clicked.connect(self.openFile)

        # Play and stop buttons on the first row
        self.playButton = QPushButton(" ", self)
        self.playButton.setIcon(QIcon("play.jpg"))
        self.playButton.setEnabled(False)
        self.playButton.setFixedSize(25, 25)
        layout.addWidget(self.playButton, 0, 1)
        self.playButton.clicked.connect(self.playAudio)

        self.stopButton = QPushButton(" ", self)
        self.stopButton.setIcon(QIcon("pausa.jpg"))
        self.stopButton.setEnabled(False)
        self.stopButton.setFixedSize(25, 25)
        layout.addWidget(self.stopButton, 0, 2)
        self.playButton.move(140, 120)
        self.stopButton.clicked.connect(self.stopAudio)

        # Filer button on the second row that uses the parameters on the right
        self.filterButton = QPushButton("Filter", self)
        self.filterButton.setFixedSize(200, 50)
        layout.addWidget(self.filterButton, 2, 0, 2, 2)
        self.filterButton.setEnabled(False)
        self.filterButton.clicked.connect(self.addFilter)

        # Add a tab to show and delete the sound graph
        tab1 = QWidget()
        self.tab1_1_layout = QGridLayout()
        tab1.setLayout(self.tab1_1_layout)

        self.soundButton1 = QPushButton("Show graph", self)
        self.soundButton1.setEnabled(False)
        self.soundButton1.clicked.connect(self.soundGraph)
        self.deleteSButton = QPushButton("Delete graph", self)
        self.deleteSButton.clicked.connect(self.deleteSGraph)

        self.tab1_1_layout.addWidget(self.soundButton1, 1, 0)
        self.tab1_1_layout.addWidget(self.deleteSButton, 1, 1)
        self.deleteSButton.hide()

        # Add a tab to show and delete the fourier graph
        tab2 = QWidget()
        self.tab1_2_layout = QGridLayout()
        tab2.setLayout(self.tab1_2_layout)

        self.freqButton1 = QPushButton("Show graph", self)
        self.freqButton1.setEnabled(False)
        self.tab1_2_layout.addWidget(self.freqButton1, 2, 0)
        self.freqButton1.clicked.connect(self.freqGraph)

        self.deleteFButton = QPushButton("Delete graph", self)
        self.deleteFButton.clicked.connect(self.deleteFGraph)

        self.tab1_2_layout.addWidget(self.freqButton1, 1, 0)
        self.tab1_2_layout.addWidget(self.deleteFButton, 1, 1)
        self.deleteFButton.hide()

        # Add the tabs to the tab widget
        self.tabWidget.addTab(tab1, "Sound graph")
        self.tabWidget.addTab(tab2, "Fourier graph")

        # Add the tab widget on the fourth row
        layout.addWidget(self.tabWidget, 4, 0, 1, 4)

    def populate_right_layout(self, layout):
        """Adding widgets to the right side, related to the filtering."""
        # IIR or FIR filter QComboBox on the first row
        self.filter_type = QComboBox(self)
        self.filter_type.addItems(["FIR", "IIR"])
        type_label = QLabel("FIR/IIR: ", self)
        layout.addWidget(type_label, 0, 0, 1, 1)
        layout.addWidget(self.filter_type, 0, 1, 1, 1)

        self.ir_type = self.filter_type.currentText()
        self.filter_type.currentIndexChanged.connect(self.type)

        # Type of filter QCobobox on the first row
        self.filter_type2 = QComboBox(self)
        self.filter_type2.addItems(["Band pass", "Low pass", "High pass"])
        type_label2 = QLabel("Type: ", self)
        layout.addWidget(type_label2, 0, 2, 1, 1)
        layout.addWidget(self.filter_type2, 0, 3, 1, 1)

        self.pass_type = self.filter_type2.currentText()
        self.filter_type2.currentIndexChanged.connect(self.show_bandpass)

        # Order silder on the second and third row
        self.order_slider = QSlider()
        self.order_slider.setOrientation(1)
        self.order_slider.setMinimum(1)
        self.order_slider.setMaximum(7)
        self.order_slider.setValue(50)
        self.order_slider.setTickInterval(1)

        order_min_label = QLabel(str(self.order_slider.minimum()))
        order_max_label = QLabel(str(self.order_slider.maximum()))
        self.order_value_label = QLabel(str(self.order_slider.value()))

        layout.addWidget(QLabel("Order: "), 1, 0, 1, 1, Qt.Alignment(Qt.AlignTop))
        layout.addWidget(self.order_value_label, 1, 1, 1, 1, Qt.Alignment(Qt.AlignTop))
        layout.addWidget(order_min_label, 2, 0, 1, 1, Qt.Alignment(Qt.AlignTop))
        layout.addWidget(self.order_slider, 2, 1, 2, 1, Qt.Alignment(Qt.AlignTop))
        layout.addWidget(order_max_label, 2, 3, 1, 1, Qt.Alignment(Qt.AlignTop))

        self.order_slider.valueChanged.connect(self.update_order_label)

        # Frequency cut slider on the fourth and fifth row
        self.cut_slider = QSlider()
        self.cut_slider.setOrientation(1)
        self.cut_slider.setMinimum(1)
        self.cut_slider.setMaximum(100)
        self.cut_slider.setValue(50)
        self.cut_slider.setTickInterval(1)

        cut_min_label = QLabel(str(self.cut_slider.minimum()))
        cut_max_label = QLabel(str(self.cut_slider.maximum()))
        self.cut_value_label = QLabel(str(self.cut_slider.value()))

        layout.addWidget(QLabel("Cut: "), 3, 0, 1, 1, Qt.Alignment(Qt.AlignTop))
        layout.addWidget(self.cut_value_label, 3, 1, 1, 1, Qt.Alignment(Qt.AlignTop))
        layout.addWidget(cut_min_label, 4, 0, 1, 1, Qt.Alignment(Qt.AlignTop))
        layout.addWidget(self.cut_slider, 4, 1, 2, 1, Qt.Alignment(Qt.AlignTop))
        layout.addWidget(cut_max_label, 4, 3, 1, 1, Qt.Alignment(Qt.AlignTop))

        self.cut_slider.valueChanged.connect(self.update_cut_label)

        # High frequency cut for band pass on the sixth and seventh row
        self.high_slider = QSlider()
        self.high_slider.setOrientation(1)
        self.high_slider.setMinimum(self.cut_slider.value() + 1)
        self.high_slider.setMaximum(self.cut_slider.maximum() * 2)
        self.high_slider.setValue(self.cut_slider.maximum() + 50)
        self.high_slider.setTickInterval(1)

        self.high_min_label = QLabel(str(self.high_slider.minimum()))
        self.high_max_label = QLabel(str(self.high_slider.maximum()))
        self.high_value_label = QLabel(str(self.high_slider.value()))

        self.high_cut_label = QLabel("High cut: ")
        layout.addWidget(self.high_cut_label, 5, 0)
        layout.addWidget(self.high_value_label, 5, 1)

        layout.addWidget(self.high_min_label, 6, 0)
        layout.addWidget(self.high_slider, 6, 1, 2, 1)
        layout.addWidget(self.high_max_label, 6, 3)

        self.high_slider.valueChanged.connect(self.update_high_label)

        # Delete graph button on the eighth row
        self.deleteSFButton = QPushButton("Delete graph", self)
        self.deleteSFButton.setEnabled(False)
        self.deleteSFButton.clicked.connect(self.deleteSFGraph)
        layout.addWidget(self.deleteSFButton, 7, 5, 1, 1, Qt.Alignment(Qt.AlignRight))

        # Save audio button on the eighth row
        self.saveButton = QPushButton("Save audio")
        self.saveButton.clicked.connect(self.saveAudio)
        self.saveButton.setEnabled(False)
        layout.addWidget(self.saveButton, 7, 3, 1, 1, Qt.Alignment(Qt.AlignRight))

        self.format_option = QComboBox()
        self.format_option.addItems(["wav", "mp3", "ogg"])
        layout.addWidget(self.format_option, 7, 4, 1, 1, Qt.Alignment(Qt.AlignRight))

        self.format_name = self.format_option.currentText()
        self.format_option.currentIndexChanged.connect(self.audio_format)

        # Adding tab widget to the right layout on the ninth row
        tab_widget = QTabWidget()

        # First tab
        tab1 = QWidget()
        self.tab2_1_layout = QVBoxLayout()

        tab1.setLayout(self.tab2_1_layout)
        tab_widget.addTab(tab1, "Tab 1")

        # Second tab
        tab2 = QWidget()
        self.tab2_2_layout = QVBoxLayout()
        tab2.setLayout(self.tab2_2_layout)
        tab_widget.addTab(tab2, "Tab 2")

        layout.addWidget(tab_widget, 8, 0, 2, 4)

    def openFile(self):
        """Select audio file to filter."""
        # Open file dialog to choose audio file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "Audio Files (*.wav *.mp3 *.aac)", options=options
        )

        # Read and anaylize the audio file
        # Enable buttons to prevent errors
        if fileName:
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
            self.stopButton.setEnabled(True)
            self.filterButton.setEnabled(True)
            self.soundButton1.setEnabled(True)
            self.freqButton1.setEnabled(True)

            self.sampFreq, self.sound = wavfile.read("MB_Song.wav")
            self.nyquist = self.sampFreq / 2.0
            self.sound = self.sound / (2.0**15)
            self.sound = self.sound[:, 0]
            self.length_in_s = self.sound.shape[0] / self.sampFreq

            self.soundButton1.show()
            self.freqButton1.show()

    def playAudio(self):
        """Reproduce file."""
        self.mediaPlayer.play()

    def stopAudio(self):
        """Pause audio."""
        self.mediaPlayer.stop()

    def soundGraph(self):
        """Show orginal sound graph."""
        time = np.arange(self.sound.shape[0]) / self.sound.shape[0] * self.length_in_s

        self.figS1, self.ax = plt.subplots(figsize=(4, 4))
        self.ax.plot(time, self.sound)
        self.ax.set_xlabel("Time")
        self.figS1.tight_layout()
        self.canvasS = FigureCanvas(self.figS1)
        self.tab1_1_layout.addWidget(self.canvasS)

        self.soundButton1.hide()
        self.deleteSButton.show()

    def freqGraph(self):
        """Show orginal fourier graph."""
        fft_spectrum = np.fft.rfft(self.sound)
        freq = np.fft.rfftfreq(self.sound.size, d=1.0 / self.sampFreq)
        fft_spectrum_abs = np.abs(fft_spectrum)

        self.figF1, self.ax = plt.subplots(figsize=(4, 4))
        self.ax.plot(freq, fft_spectrum_abs)
        self.ax.set_xlabel("Frequency")
        self.figF1.tight_layout()
        self.canvasF = FigureCanvas(self.figF1)
        self.tab1_2_layout.addWidget(self.canvasF)

        self.freqButton1.hide()
        self.deleteFButton.show()

    def deleteSGraph(self):
        """Delete orginal sound graph."""
        if hasattr(self, "canvasS"):
            self.canvasS.setParent(None)
            self.figS1.clear()
            del self.figS1
            self.soundButton1.show()
            self.deleteSButton.hide()

    def deleteFGraph(self):
        """Delete orginal fourier graph."""
        if hasattr(self, "canvasF"):

            self.canvasF.setParent(None)
            self.figF1.clear()
            del self.figF1
            self.freqButton1.show()
            self.deleteFButton.hide()

    def update_cut_label(self):
        """Update the label of the frequency cut slider."""
        self.cut_value_label.setText(str(self.cut_slider.value()))

    def update_order_label(self):
        """Update the label of the order slider."""
        self.order_value_label.setText(str(self.order_slider.value()))

    def update_high_label(self):
        """Update the label of the upper freceuncy cut slider."""
        self.high_value_label.setText(str(self.high_slider.value()))

    def show_bandpass(self):
        """Show the upper frequency cut slider if the filter is band pass."""
        self.pass_type = self.filter_type2.currentText()
        if self.pass_type == "Band pass":
            self.high_slider.show()
            self.high_min_label.show()
            self.high_max_label.show()
            self.high_value_label.show()
        else:
            self.high_slider.hide()
            self.high_min_label.hide()
            self.high_max_label.hide()
            self.high_value_label.hide()
            self.high_cut_label.hide()

    def type(self):
        """Update IIR or FIR filter type if changed."""
        self.ir_type = self.filter_type.currentText()

    def deleteSFGraph(self):
        """Delete filtered sound and fourier graphs."""
        self.canvasF2.setParent(None)
        self.figF2.clear()
        del self.figF2

        self.canvasSF.setParent(None)
        self.figS.clear()
        del self.figS

        self.deleteSFButton.setEnabled(False)

    def saveAudio(self):
        """Save file on any selected format."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Resultado",
            "",
            f"{self.format_name.upper()} Files (*.{self.format_name});;All Files (*)",
            options=options,
        )

        if filename:
            try:
                filename = filename + "." + self.format_name
                sf.write(filename, self.x_filtered, samplerate=44100)

            except Exception as e:
                print("Error al guardar el archivo:", e)

    def audio_format(self):
        """Update saved audio format if changed."""
        self.format_name = self.format_option.currentText()

    def addFilter(self):
        """Filter the original audio using the selected parameters."""
        # Use the filter functions from filters.py
        if self.ir_type == "IIR":
            self.x_filtered = iir_filter(
                self.sound,
                [self.cut_slider.value(), self.high_slider.value()],
                self.sampFreq,
                self.pass_type,
                self.order_slider.value(),
            )
        elif self.ir_type == "FIR":
            self.x_filtered, taps, n = fir_filter(
                self.sound,
                self.nyquist,
                [self.cut_slider.value(), self.high_slider.value()],
                self.pass_type,
            )

        # Find the fourier transform of the filtered sound
        fft_spectrum = np.fft.rfft(self.x_filtered)
        freq = np.fft.rfftfreq(self.sound.size, d=1.0 / self.sampFreq)
        fft_spectrum_abs = np.abs(fft_spectrum)

        # Plot the filtered sound and fourier graphs
        self.figF2, self.ax = plt.subplots(figsize=(4, 4))
        self.ax.plot(freq, fft_spectrum_abs)
        self.ax.set_xlabel("Frequency")
        self.figF2.tight_layout()
        self.canvasF2 = FigureCanvas(self.figF2)
        self.tab2_2_layout.addWidget(self.canvasF2)

        time = (
            np.arange(self.x_filtered.shape[0])
            / self.x_filtered.shape[0]
            * self.length_in_s
        )

        self.figS, self.ax = plt.subplots(figsize=(4, 4))
        self.ax.plot(time, self.x_filtered)
        self.ax.set_xlabel("Time")
        self.figS.tight_layout()
        self.canvasSF = FigureCanvas(self.figS)
        self.tab2_1_layout.addWidget(self.canvasSF)

        self.deleteSFButton.setEnabled(True)
        self.saveButton.setEnabled(True)


if __name__ == "__main__":
    """Open the main window and allow the execution."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
