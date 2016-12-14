from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import os

class CoordinatedGeneralizationView(QDialog):

    loadRasterLayer = pyqtSignal(str, str, str)

    def __init__(self, model):
        self.model = model
        self._setupUi()

    def _setupUi(self):
        QDialog.__init__(self, None)
        self.setWindowTitle("Coordinated Generalization")
        self.resize(320, 0)

        dsmLabel = QLabel("DSM raster layer")
        self.dsmCombo = QComboBox()

        waterLabel = QLabel("Water linestring layer (optional)")
        self.waterCombo = QComboBox()
        self.waterCombo.currentIndexChanged.connect(
            self._checkSelectedWaterLayer)

        warningIcon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
        warningPixmap = warningIcon.pixmap(16)

        self.warningLabel = QLabel()
        self.warningLabel.setPixmap(warningPixmap)
        self.warningLabel.setVisible(False)
        self.warningLabel.setToolTip("The selected water layer contains "
            "MultiLineString features, which might cause anomalies in the "
            "generalized output.")

        waterLayout = QHBoxLayout()
        waterLayout.addWidget(waterLabel)
        waterLayout.addWidget(self.warningLabel)
        waterLayout.addStretch()

        outputLabel = QLabel("Output file")
        self.outputLine = QLineEdit()
        self.outputLine.setSizePolicy(QSizePolicy.MinimumExpanding,
            QSizePolicy.Fixed)
        self.outputLine.textChanged.connect(self._validate)

        browseButton = QPushButton("Browse...")
        browseButton.clicked.connect(self._selectOutputFile)

        outputLayout = QHBoxLayout()
        outputLayout.addWidget(self.outputLine)
        outputLayout.addWidget(browseButton)

        self.openAfterCheck = QCheckBox("Open output file")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
            | QDialogButtonBox.Cancel)
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Generalize")
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(self.openAfterCheck)
        bottomLayout.addWidget(self.buttonBox)

        layout = QVBoxLayout()
        layout.addWidget(dsmLabel)
        layout.addWidget(self.dsmCombo)
        layout.addSpacing(8)
        layout.addLayout(waterLayout)
        layout.addWidget(self.waterCombo)
        layout.addSpacing(8)
        layout.addWidget(outputLabel)
        layout.addLayout(outputLayout)
        layout.addSpacing(2)
        layout.addLayout(bottomLayout)

        self.setLayout(layout)

    def _selectOutputFile(self):
        filename = QFileDialog.getSaveFileName(self, "Select output file", "",
            "*.asc")
        self.outputLine.setText(filename)

    def _validate(self):
        isValid = self.outputLine.text() != ""
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(isValid)

    def setLayers(self, layers):
        self.dsmCombo.clear()
        self.waterCombo.clear()
        self.waterCombo.addItem("none", None)
        for layer in layers:
            if layer.isSpatial() and layer.type() == QgsMapLayer.RasterLayer:
                self.dsmCombo.addItem(layer.name(), layer)
            elif layer.isSpatial() and layer.type() == QgsMapLayer.VectorLayer \
                    and layer.geometryType() == QgsWKBTypes.LineGeometry:
                self.waterCombo.addItem(layer.name(), layer)

    def _checkSelectedWaterLayer(self, idx):
        waterLayer = self.waterCombo.itemData(idx)
        containsMultilines = waterLayer is not None and \
            any(f.geometry().isMultipart() for f in waterLayer.getFeatures())
        self.warningLabel.setVisible(containsMultilines)

    def accept(self):
        dsmLayer = self.dsmCombo.itemData(self.dsmCombo.currentIndex())
        waterLayer = self.waterCombo.itemData(self.waterCombo.currentIndex())

        dsmPath = dsmLayer.dataProvider().dataSourceUri()
        waterLayerPath = (None if waterLayer is None else
            waterLayer.dataProvider().dataSourceUri().split("|")[0])
        outputPath = self.outputLine.text()

        self.model.filterAndSave(dsmPath, waterLayerPath, outputPath)

        if self.openAfterCheck.isChecked():
            self.loadRasterLayer.emit(outputPath,
                os.path.splitext(os.path.basename(outputPath))[0],
                dsmLayer.crs().authid())

        QDialog.accept(self)
