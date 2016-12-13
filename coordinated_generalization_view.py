from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

class CoordinatedGeneralizationView(QDialog):

    def __init__(self, model):
        self.model = model
        self.__setupUi()

    def __setupUi(self):
        QDialog.__init__(self, None)
        self.setWindowTitle("Coordinated Generalization")
        self.resize(320, 190)

        dsmLabel = QLabel("DSM raster layer")
        self.dsmCombo = QComboBox()

        waterLabel = QLabel("Water linestring layer (optional)")
        self.waterCombo = QComboBox()

        outputLabel = QLabel("Output file")
        self.outputLine = QLineEdit()
        self.outputLine.setSizePolicy(QSizePolicy.MinimumExpanding,
            QSizePolicy.Fixed)
        self.outputLine.textChanged.connect(self.__validate)

        browseButton = QPushButton("Browse...")
        browseButton.clicked.connect(self.__selectOutputFile)

        outputLayout = QHBoxLayout()
        outputLayout.addWidget(self.outputLine)
        outputLayout.addWidget(browseButton)

        openAfterCheck = QCheckBox("Open output file")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
            | QDialogButtonBox.Cancel)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(openAfterCheck)
        bottomLayout.addWidget(self.buttonBox)

        layout = QVBoxLayout()
        layout.addWidget(dsmLabel)
        layout.addWidget(self.dsmCombo)
        layout.addWidget(waterLabel)
        layout.addWidget(self.waterCombo)
        layout.addWidget(outputLabel)
        layout.addLayout(outputLayout)
        layout.addStretch()
        layout.addLayout(bottomLayout)

        self.setLayout(layout)

    def __selectOutputFile(self):
        filename = QFileDialog.getSaveFileName(self, "Select output file", "",
            "*.tif")
        self.outputLine.setText(filename)

    def __validate(self):
        isValid = self.outputLine.text() != ""
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(isValid)

    def openOutput(self):
        return self.openAfterCheck.isChecked()

    def setLayers(self, layers):
        self.dsmCombo.clear()
        self.waterCombo.clear()
        for layer in layers:
            if layer.isSpatial() and layer.type() == QgsMapLayer.RasterLayer:
                self.dsmCombo.addItem(layer.name(), layer)
            elif layer.isSpatial() and layer.type() == QgsMapLayer.VectorLayer \
                    and layer.geometryType() == QgsWKBTypes.LineGeometry:
                self.waterCombo.addItem(layer.name(), layer)

    def accept(self):
        QDialog.accept(self)
