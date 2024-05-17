from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
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

from filters import fir_filter, iir_filter


class Filtro(QDialog):

    def __init__(self):
        super().__init__()
        self.setModal(True)
        self.filter_options()

    def filter_options(self):
        self.setWindowTitle("Filtrado")
        self.setGeometry(800, 300, 600, 700)

        layout = QGridLayout()
        self.setLayout(layout)

        self.tabWidget = QTabWidget()

        ######################################### Type #########################################
        self.filter_type = QComboBox(self)
        self.filter_type.addItems(["FIR", "IIR"])

        self.type_label = QLabel("Type: ", self)
        layout.addWidget(self.type_label, 0, 0)
        layout.addWidget(self.filter_type, 0, 1)

        ######################################### Frequency Cut #########################################
        self.cut_slider = QSlider()
        self.cut_slider.setOrientation(1)
        self.cut_slider.setMinimum(0)
        self.cut_slider.setMaximum(100)
        self.cut_slider.setValue(50)
        self.cut_slider.setTickInterval(1)
        self.cut_slider.setTickPosition(QSlider.TicksBelow)

        self.cut_min_label = QLabel(str(self.cut_slider.minimum()))
        self.cut_max_label = QLabel(str(self.cut_slider.maximum()))
        self.cut_value_label = QLabel(str(self.cut_slider.value()))

        layout.addWidget(QLabel("Cut: "), 1, 0)
        layout.addWidget(self.cut_value_label, 1, 1)
        layout.addWidget(self.cut_min_label, 2, 0)
        layout.addWidget(self.cut_slider, 2, 1)
        layout.addWidget(self.cut_max_label, 2, 2)

        self.cut_slider.valueChanged.connect(self.update_cut_label)

        ######################################### Order #########################################
        self.order_slider = QSlider()
        self.order_slider.setOrientation(1)
        self.order_slider.setMinimum(1)
        self.order_slider.setMaximum(7)
        self.order_slider.setValue(50)
        self.order_slider.setTickInterval(1)
        self.order_slider.setTickPosition(QSlider.TicksBelow)

        self.order_min_label = QLabel(str(self.order_slider.minimum()))
        self.order_max_label = QLabel(str(self.order_slider.maximum()))
        self.order_value_label = QLabel(str(self.order_slider.value()))

        layout.addWidget(QLabel("Order: "), 3, 0)
        layout.addWidget(self.order_value_label, 3, 1)
        layout.addWidget(self.order_min_label, 4, 0)
        layout.addWidget(self.order_slider, 4, 1)
        layout.addWidget(self.order_max_label, 4, 2)

        self.order_slider.valueChanged.connect(self.update_order_label)

        ######################################### Tabs #########################################

        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout()
        self.tab1.setLayout(self.tab1_layout)

        soundButton = QPushButton("Show graph", self)
        soundButton.setEnabled(False)
        soundButton.clicked.connect(self.soundGraph)
        self.tab1_layout.addWidget(soundButton)

        self.tab2 = QWidget()
        self.tab2_layout = QVBoxLayout()
        self.tab2.setLayout(self.tab2_layout)

        freqButton = QPushButton("Show graph", self)
        freqButton.setEnabled(False)
        freqButton.clicked.connect(self.freqGraph)
        self.tab2_layout.addWidget(freqButton)

        self.tabWidget.addTab(self.tab1, "Sound graph")
        self.tabWidget.addTab(self.tab2, "Fourier graph")

        layout.addWidget(self.tabWidget, 5, 0, 1, 3)

    def update_cut_label(self):
        self.cut_value_label.setText(str(self.cut_slider.value()))

    def update_order_label(self):
        self.order_value_label.setText(str(self.order_slider.value()))

    def soundGraph(self):
        pass

    def freqGraph(self):
        pass
