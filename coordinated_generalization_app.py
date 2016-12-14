from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis import *
from qgis.core import *
from qgis.utils import *

from coordinated_generalization_model import CoordinatedGeneralizationModel
from coordinated_generalization_view import CoordinatedGeneralizationView

import resources

class CoordinatedGeneralizationApp:

    def __init__(self, iface):
        self.iface = iface
        self.view = CoordinatedGeneralizationView(
            CoordinatedGeneralizationModel())
        self.view.loadRasterLayer.connect(self._loadRasterLayer)

    def initGui(self):
        self.action = QAction(QIcon(":/plugins/coordgen/icon.png"),
            "Coordinated Generalization", self.iface.mainWindow())
        self.action.setObjectName("coordGenAction")
        self.action.setWhatsThis("Coordinated Generalization")

        self.action.triggered.connect(self.run)
        self.iface.addPluginToRasterMenu("&Coordinated Generalization",
            self.action)

    def unload(self):
        self.iface.removePluginRasterMenu("&Coordinated Generalization",
            self.action)

    def run(self):
        layers = self.iface.legendInterface().layers()
        self.view.setLayers(layers)
        self.view.exec_()

    def _loadRasterLayer(self, path, name, crsId):
        settings = QSettings()
        oldCrsBehaviour = settings.value("/Projections/defaultBehaviour")
        settings.setValue("/Projections/defaultBehaviour", "useProject")

        self.iface.addRasterLayer(path, name)
        loadedLayer = self.iface.activeLayer()
        loadedLayer.setCrs(QgsCoordinateReferenceSystem(crsId))

        settings.setValue("/Projections/defaultBehaviour", oldCrsBehaviour)
