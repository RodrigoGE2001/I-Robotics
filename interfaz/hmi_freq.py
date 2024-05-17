"""
Se crea la primer ventana para seleccionar archivo.
"""

import sys

import matplotlib.pyplot as plt
import numpy as np
from filtrado import Filtro
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon, QMovie
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from scipy.io import wavfile


class FileSelectorWindow(QWidget):
    """
    Clase para la ventana de selección de archivo.
    """

    def __init__(self):
        """
        Inicializa la ventana.
        """
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        Se declaran los elementos gaficos.
        """
        self.setWindowTitle("Original file")

        self.layout = QVBoxLayout()
        self.tabWidget = QTabWidget()

        self.selectButton = QPushButton("Select File", self)
        self.selectButton.setGeometry(30, 30, 200, 50)
        self.selectButton.clicked.connect(self.openFile)

        self.playButton = QPushButton(" ", self)
        self.playButton.setIcon(QIcon("play.jpg"))
        self.playButton.setEnabled(False)
        self.playButton.setFixedSize(25, 25)
        self.playButton.move(105, 110)
        self.playButton.clicked.connect(self.playAudio)

        self.stopButton = QPushButton(" ", self)
        self.stopButton.setIcon(QIcon("pausa.jpg"))
        self.stopButton.setEnabled(False)
        self.stopButton.setFixedSize(25, 25)
        self.stopButton.move(140, 110)
        self.stopButton.clicked.connect(self.stopAudio)

        self.filterButton = QPushButton("Filter", self)
        self.filterButton.setGeometry(30, 150, 200, 50)
        self.filterButton.setEnabled(False)
        self.filterButton.clicked.connect(self.addFilter)

        # self.filePathLabel = QLabel(self)
        # self.filePathLabel.setGeometry(40, 200, 250, 50)

        self.tab1 = QWidget()

        self.tab1_layout = QVBoxLayout()

        # self.tabWidget.addTab(self.tab1, "Sound graph")
        self.tab1.setLayout(self.tab1_layout)

        self.soundButton = QPushButton("Show graph", self)
        # self.soundButton.setIcon(QIcon('sound.gif'))
        self.soundButton.setEnabled(False)
        self.soundButton.setGeometry(200, 150, 200, 50)
        # self.soundButton.move(250, 30)
        self.soundButton.clicked.connect(self.soundGraph)
        self.tab1_layout.addWidget(self.soundButton)

        # self.tabWidget.addTab(self.tab2, "Fourirer graph")
        self.tab2 = QWidget()
        self.tab2_layout = QVBoxLayout()
        self.tab2.setLayout(self.tab2_layout)

        self.freqButton = QPushButton("Show graph", self)
        self.freqButton.setEnabled(False)
        self.freqButton.setGeometry(200, 150, 200, 50)
        self.freqButton.clicked.connect(self.freqGraph)
        self.tab2_layout.addWidget(self.freqButton)

        self.tabWidget.addTab(self.tab1, "Sound graph")
        self.tabWidget.addTab(self.tab2, "Fourier graph")

        self.tabWidget.setGeometry(200, 200, 200, 200)

        # self.layout.addWidget(self.tabWidget)

        self.fig, self.ax = plt.subplots()

        self.mediaPlayer = QMediaPlayer()

        self.setGeometry(300, 300, 500, 300)

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
        self.ax.plot(time, self.sound[:], "r")
        self.ax.set_xlabel("time, signal")
        self.fig.tight_layout()
        # self.canvas.draw()
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

    def freqGraph(self):
        fft_spectrum = np.fft.rfft(self.sound)
        freq = np.fft.rfftfreq(self.sound.size, d=1.0 / self.sampFreq)
        fft_spectrum_abs = np.abs(fft_spectrum)
        self.ax.plot(freq, fft_spectrum_abs)
        self.ax.set_xlabel("Frequency")
        self.fig.tight_layout()
        # self.canvas.draw()
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

    def addFilter(self):
        """
        Abre la ventana de filtrado.
        """
        self.filter = Filtro()
        self.filter.show()


if __name__ == "__main__":
    """
    Abre y cierra la ventana.
    """
    app = QApplication(sys.argv)
    window = FileSelectorWindow()
    window.show()
    sys.exit(app.exec_())
