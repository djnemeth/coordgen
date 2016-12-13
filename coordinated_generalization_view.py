from PyQt4.QtGui import *

class CoordinatedGeneralizationView(QDialog):

    def __init__(self, model):
        self.model = model
        self.setupUi()

    def setupUi(self):
        QDialog.__init__(self, None)
        self.setWindowTitle('Coordinated Generalization')
