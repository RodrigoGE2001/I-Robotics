import sys

import matplotlib.pyplot as plt
import numpy as np
from filtrado import Filtro
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QMovie
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from scipy.io import wavfile


class SelectFile(QWidget):

    def __init__(self):
        super().__init__()
        self.original()

    def original(self):
        self.setWindowTitle("Original File")

        layout = QGridLayout()
        self.setLayout(layout)
        self.setGeometry(300, 300, 1100, 700)

        self.mediaPlayer = QMediaPlayer()

        self.tabWidget = QTabWidget()

        self.selectButton = QPushButton("Select File", self)
        # self.selectButton.setGeometry(30, 30, 200, 50)
        self.selectButton.setFixedSize(200, 50)
        layout.addWidget(self.selectButton, 0, 0, 2, 1)
        self.selectButton.clicked.connect(self.openFile)

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

        self.filterButton = QPushButton("Filter", self)
        # self.filterButton.move(100, 150)
        # self.filterButton.setFixedSize(200, 50)
        self.filterButton.setFixedSize(200, 50)
        layout.addWidget(self.filterButton, 2, 0, 2, 2)
        self.filterButton.setEnabled(False)
        self.filterButton.clicked.connect(self.addFilter)

        #################################################### TABS ####################################################

        self.tab1 = QWidget()
        self.tab1_layout = QGridLayout()
        self.tab1.setLayout(self.tab1_layout)

        self.soundButton = QPushButton("Show graph", self)
        self.soundButton.setEnabled(False)
        self.soundButton.clicked.connect(self.soundGraph)
        # self.tab1_layout.addWidget(self.soundButton, 1, 0)
        # self.soundButton.move(250, 30)
        # self.soundButton.clicked.connect(self.soundGraph)
        self.deleteSButton = QPushButton("Delete graph", self)
        # self.deleteSButton.setEnabled(False)
        self.deleteSButton.clicked.connect(self.deleteSGraph)

        self.tab1_layout.addWidget(self.soundButton, 1, 0)
        self.tab1_layout.addWidget(self.deleteSButton, 1, 1)
        self.deleteSButton.hide()

        self.tab2 = QWidget()
        self.tab2_layout = QGridLayout()
        self.tab2.setLayout(self.tab2_layout)

        self.freqButton = QPushButton("Show graph", self)
        # self.freqButton.setEnabled(False)
        self.tab2_layout.addWidget(self.freqButton, 2, 0)
        self.freqButton.clicked.connect(self.freqGraph)
        # self.soundButton.move(250, 30)
        # self.soundButton.clicked.connect(self.soundGraph)

        self.deleteFButton = QPushButton("Delete graph", self)
        # self.deleteFButton.setEnabled(False)
        self.deleteFButton.clicked.connect(self.deleteFGraph)

        self.tab2_layout.addWidget(self.freqButton, 1, 0)
        self.tab2_layout.addWidget(self.deleteFButton, 1, 1)
        self.deleteFButton.hide()

        self.tabWidget.addTab(self.tab1, "Sound graph")
        self.tabWidget.addTab(self.tab2, "Fourier graph")

        layout.addWidget(self.tabWidget, 4, 0, 1, 4)

    def openFile(self):
        """
        Selecciona el archivo de audio.
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "Audio Files (*.wav *.mp3 *.aac)", options=options
        )
        if fileName:
            # self.filePathLabel.setText("Selected File: " + fileName)
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
            self.stopButton.setEnabled(True)
            self.filterButton.setEnabled(True)
            self.soundButton.setEnabled(True)
            self.freqButton.setEnabled(True)

            self.sampFreq, self.sound = wavfile.read("MB_Song.wav")
            self.sound = self.sound / (2.0**15)
            self.sound = self.sound[:, 0]
            self.length_in_s = self.sound.shape[0] / self.sampFreq

            self.soundButton.show()
            self.freqButton.show()

    def playAudio(self):
        """
        Reproduce el audio.
        """
        self.mediaPlayer.play()

    def stopAudio(self):
        """
        Pausa el audio.
        """
        self.mediaPlayer.stop()

    def soundGraph(self):
        time = np.arange(self.sound.shape[0]) / self.sound.shape[0] * self.length_in_s

        self.figS, self.ax = plt.subplots()
        self.ax.plot(time, self.sound)
        self.ax.set_xlabel("Time")
        self.figS.tight_layout()
        self.canvasS = FigureCanvas(self.figS)
        self.tab1_layout.addWidget(self.canvasS)

        self.soundButton.hide()
        self.deleteSButton.show()

    def freqGraph(self):
        fft_spectrum = np.fft.rfft(self.sound)
        freq = np.fft.rfftfreq(self.sound.size, d=1.0 / self.sampFreq)
        fft_spectrum_abs = np.abs(fft_spectrum)

        self.figF, self.ax = plt.subplots()
        self.ax.plot(freq, fft_spectrum_abs)
        self.ax.set_xlabel("Frequency")
        self.figF.tight_layout()
        self.canvasF = FigureCanvas(self.figF)
        self.tab2_layout.addWidget(self.canvasF)

        self.freqButton.hide()
        self.deleteFButton.show()

    def deleteSGraph(self):
        if hasattr(self, "canvasS"):
            self.canvasS.setParent(None)
            self.figS.clear()
            del self.figS
            self.soundButton.show()

    def deleteFGraph(self):
        if hasattr(self, "canvasF"):
            self.canvasF.setParent(None)
            self.figF.clear()
            del self.figF
            self.freqButton.show()

    def addFilter(self):
        """
        Abre la ventana de filtrado.
        """
        self.filter = Filtro()
        self.filter.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SelectFile()
    ex.show()
    sys.exit(app.exec_())
