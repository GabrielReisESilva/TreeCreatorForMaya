import pprint
import treeCreator
from maya import cmds
import pymel.core as pm
from maya import OpenMayaUI as omui

reload(treeCreator)

import Qt
from Qt import QtWidgets, QtCore, QtGui

if Qt.__binding__=='PySide':
    from shiboken import wrapInstance
    from Qt.QtCore import Signal
elif Qt.__binding__.startswith('PyQt'):
    from sip import wrapinstance as wrapInstance
    from Qt.QtCore import pyqtSignal as Signal
else:
    from shiboken2 import wrapInstance
    from Qt.QtCore import Signal

def getMayaMainWindow():
    win = omui.MQtUtil_mainWindow()
    #Convert memory address into long
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    return ptr

def getDock(name='ParkManagerDock'):
    deleteDock(name)
    ctrl = pm.workspaceControl(name, dockToMainWindow=('right', 1), label = 'Park Manager')
    qtControl = omui.MQtUtil_findControl(ctrl)
    ptr = wrapInstance(long(qtControl), QtWidgets.QWidget)
    return ptr

def deleteDock(name='ParkManagerDock'):
    if pm.workspaceControl(name, query=True, exists=True):
        pm.deleteUI(name)

class ParkUI(QtWidgets.QDialog):

    def __init__(self, dock = False):
        if dock:
            parent = getDock()
        else:
            deleteDock()

            try:
                pm.deleteUI('parkManager')
            except:
                print 'No previous UI exists'

            parent = QtWidgets.QDialog(parent=getMayaMainWindow())
            parent.setObjectName('parkManager')
            parent.setWindowTitle('Park Manager')
            self.mainLayout = QtWidgets.QVBoxLayout(parent)

        super(ParkUI, self).__init__(parent = parent)

        #self.setWindowTitle('Park UI')
        self.library = treeCreator.Tree()
        self.parkWidth = 10
        self.parkLength = 10
        self.bushesDistribution = 0
        self.treesDistribution = 0
        self.previewTree = None
        self.minHeight = 4.0
        self.maxHeight = 8.0
        self.minRadius = 0.5
        self.maxRadius = 0.5
        self.branches = 4
        self.leafColor1 = QtGui.QColor(0,255,0)
        self.leafColor2 = QtGui.QColor(0,200,0)
        self.leafColor3 = QtGui.QColor(0,128,0)
        self.trunkColor = QtGui.QColor(30,8,0)
        self.buildUI()

        self.parent().layout().addWidget(self)
        if not dock:
            parent.show()

    def buildUI(self):
        #self.mainLayout = QtWidgets.QVBoxLayout(self)
        #PARK BOX
        parkGB = QtWidgets.QGroupBox('Park')
        parkLayout = QtWidgets.QVBoxLayout(parkGB)
        self.mainLayout.addWidget(parkGB)
            #DIMENSION
        dimensionWidget = QtWidgets.QWidget()
        dimensionLayout = QtWidgets.QHBoxLayout(dimensionWidget)
        dimensionLayout.addWidget(QtWidgets.QLabel('Dimension'))
        self.dimensionWidth = QtWidgets.QLineEdit('10')
        self.dimensionWidth.setAlignment(QtCore.Qt.AlignRight)
        dimensionLayout.addWidget(self.dimensionWidth)
        dimensionLayout.addWidget(QtWidgets.QLabel('x'))
        self.dimensionLength = QtWidgets.QLineEdit('10')
        dimensionLayout.addWidget(self.dimensionLength)
        parkLayout.addWidget(dimensionWidget)
            #BUSHES
        bushesWidget = QtWidgets.QWidget()
        bushesLayout = QtWidgets.QHBoxLayout(bushesWidget)
        bushesLayout.addWidget(QtWidgets.QLabel('Bushes Distribution'))
        self.bushesSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.bushesSlider.setMinimum(0)
        self.bushesSlider.setMaximum(10)
        self.bushesSlider.setValue(1)
        bushesLayout.addWidget(QtWidgets.QLabel('0')) #SORRY
        bushesLayout.addWidget(self.bushesSlider)
        bushesLayout.addWidget(QtWidgets.QLabel('10'))
        parkLayout.addWidget(bushesWidget)
            #TREES
        treesDistributionWidget = QtWidgets.QWidget()
        treesDistributionLayout = QtWidgets.QHBoxLayout(treesDistributionWidget)
        treesDistributionLayout.addWidget(QtWidgets.QLabel('Tree Distribution'))
        self.treesDistributionSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.treesDistributionSlider.setMinimum(0)
        self.treesDistributionSlider.setMaximum(10)
        self.treesDistributionSlider.setValue(5)
        treesDistributionLayout.addWidget(QtWidgets.QLabel('     0'))
        treesDistributionLayout.addWidget(self.treesDistributionSlider)
        treesDistributionLayout.addWidget(QtWidgets.QLabel('10'))
        parkLayout.addWidget(treesDistributionWidget)

        #TREE BOX
        treeGB = QtWidgets.QGroupBox('Tree')
        treeLayout = QtWidgets.QVBoxLayout(treeGB)
        self.mainLayout.addWidget(treeGB)
            #HEIGHT
        heightWidget = QtWidgets.QWidget()
        heightLayout = QtWidgets.QHBoxLayout(heightWidget)
        heightLayout.addWidget(QtWidgets.QLabel('Height'))
        self.minHeightLabel = QtWidgets.QLineEdit('4.0')
        self.minHeightLabel.setAlignment(QtCore.Qt.AlignRight)
        heightLayout.addWidget(self.minHeightLabel)
        heightLayout.addWidget(QtWidgets.QLabel('-'))
        self.maxHeightLabel = QtWidgets.QLineEdit('8.0')
        heightLayout.addWidget(self.maxHeightLabel)
        treeLayout.addWidget(heightWidget)
            #RADIUS
        radiusWidget = QtWidgets.QWidget()
        radiusLayout = QtWidgets.QHBoxLayout(radiusWidget)
        radiusLayout.addWidget(QtWidgets.QLabel('Radius'))
        self.minRadiusLabel = QtWidgets.QLineEdit('0.5')
        self.minRadiusLabel.setAlignment(QtCore.Qt.AlignRight)
        radiusLayout.addWidget(self.minRadiusLabel)
        radiusLayout.addWidget(QtWidgets.QLabel('-'))
        self.maxRadiusLabel = QtWidgets.QLineEdit('1.5')
        radiusLayout.addWidget(self.maxRadiusLabel)
        treeLayout.addWidget(radiusWidget)
            #BRANCHES
        branchesWidget = QtWidgets.QWidget()
        branchesLayout = QtWidgets.QHBoxLayout(branchesWidget)
        branchesLayout.addWidget(QtWidgets.QLabel('Max Branches'))
        self.branchesSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.branchesSlider.setMinimum(0)
        self.branchesSlider.setMaximum(4)
        self.branchesSlider.setValue(4)
        branchesLayout.addWidget(QtWidgets.QLabel('0'))
        branchesLayout.addWidget(self.branchesSlider)
        branchesLayout.addWidget(QtWidgets.QLabel('4'))
        treeLayout.addWidget(branchesWidget)
            #LEAF COLOR
        leafColorWidget = QtWidgets.QWidget()
        leafColorLayout = QtWidgets.QHBoxLayout(leafColorWidget)
        leafColor1Btn = QtWidgets.QPushButton()
        leafColor1Btn.setMaximumWidth(20)
        leafColor1Btn.setMaximumHeight(20)
        self.setButtonColor(leafColor1Btn, [0, 1, 0])
        leafColor1Btn.clicked.connect(lambda *_: self.setColor(leafColor1Btn, self.leafColor1))
        leafColor2Btn = QtWidgets.QPushButton()
        leafColor2Btn.setMaximumWidth(20)
        leafColor2Btn.setMaximumHeight(20)
        self.setButtonColor(leafColor2Btn, [0, 0.75, 0])
        leafColor2Btn.clicked.connect(lambda *_: self.setColor(leafColor2Btn, self.leafColor2))
        leafColor3Btn = QtWidgets.QPushButton()
        leafColor3Btn.setMaximumWidth(20)
        leafColor3Btn.setMaximumHeight(20)
        self.setButtonColor(leafColor3Btn, [0, 0.5, 0])
        leafColor3Btn.clicked.connect(lambda *_: self.setColor(leafColor3Btn, self.leafColor3))
        leafColorLayout.addWidget(QtWidgets.QLabel('Leaves Color'))
        leafColorLayout.addWidget(QtWidgets.QLabel(' 1:'))
        leafColorLayout.addWidget(leafColor1Btn)
        leafColorLayout.addWidget(QtWidgets.QLabel(' 2:'))
        leafColorLayout.addWidget(leafColor2Btn)
        leafColorLayout.addWidget(QtWidgets.QLabel(' 3:'))
        leafColorLayout.addWidget(leafColor3Btn)
        treeLayout.addWidget(leafColorWidget)
            #TRUNK COLOR
        trunkColorWidget = QtWidgets.QWidget()
        trunkColorLayout = QtWidgets.QHBoxLayout(trunkColorWidget)
        trunkColorBtn = QtWidgets.QPushButton()
        trunkColorBtn.setMaximumWidth(20)
        trunkColorBtn.setMaximumHeight(20)
        self.setButtonColor(trunkColorBtn, [0.15, 0.03, 0])
        trunkColorBtn.clicked.connect(lambda *_: self.setColor(trunkColorBtn, self.trunkColor))
        trunkColorLayout.addWidget(QtWidgets.QLabel('Trunk Color'))
        trunkColorLayout.addWidget(QtWidgets.QLabel('  '))
        trunkColorLayout.addWidget(trunkColorBtn)
        treeLayout.addWidget(trunkColorWidget)
            #PREVIEW BUTTON
        previewBtn = QtWidgets.QPushButton('Generate Tree')
        previewBtn.clicked.connect(self.createTreePreview)
        treeLayout.addWidget(previewBtn)

        #CREATE PARK
        createParkBtn = QtWidgets.QPushButton('Generate Park')
        createParkBtn.clicked.connect(self.createPark)
        self.mainLayout.addWidget(createParkBtn)

    def setButtonColor(self, button, color):
        if not color:
            return

        assert len(color) == 3, "You must provide a list of 3 colors"

        r, g, b = [c * 255 for c in color]
        button.setStyleSheet('background-color: rgba(%s,%s,%s,1.0)' % (r, g, b))

    def setColor(self, button, leafColor):
        currentColor = self.getRgb(leafColor)
        color = pm.colorEditor(rgbValue=currentColor)
        r, g, b, a = [float(c) for c in color.split()]
        color = (r, g, b)
        leafColor.setRgb(r*255,g*255,b*255)
        self.setButtonColor(button, color)

    def updateValue(self):
        try:
            self.minRadius = float(self.minRadiusLabel.text())
            self.maxRadius = float(self.maxRadiusLabel.text())
            if self.minRadius <= 0.0 or self.minRadius > self.maxRadius:
                raise ValueError
        except ValueError:
            cmds.error('Please check Radius value')
            return False

        try:
            self.minHeight = float(self.minHeightLabel.text())
            self.maxHeight = float(self.maxHeightLabel.text())
            if self.minHeight <= 0.0 or self.minHeight > self.maxHeight:
                raise ValueError
        except ValueError:
            cmds.error('Please check Height value')
            return False

        try:
            self.parkWidth = float(self.dimensionWidth.text())
            self.parkLength = float(self.dimensionLength.text())
            if self.parkWidth <= 0.0 or self.parkLength <= 0.0:
                raise ValueError
        except ValueError:
            cmds.error('Please check dimension values')
            return False

        try:
            self.branches = int(self.branchesSlider.value())
            self.bushesDistribution = int(self.bushesSlider.value())
            self.treesDistribution = int(self.treesDistributionSlider.value())
        except ValueError:
            cmds.error('Please check slider values')
            return False

        return True

    def createTreePreview(self):
        if self.updateValue():
            if cmds.objExists('PreviewTree'):
                cmds.delete('PreviewTree')

            self.previewTree = self.library.CreateTree(self.minRadius, self.maxRadius, self.minHeight, self.maxHeight,
                                                       self.branches, self.getRgb(self.leafColor1), self.getRgb(self.leafColor2),
                                                       self.getRgb(self.leafColor3), self.getRgb(self.trunkColor), name='PreviewTree')

            cmds.select(clear=True)
            print 'Tree Created'

    def createTreeAt(self, posX, posZ):
        return self.library.CreateTree(self.minRadius, self.maxRadius, self.minHeight, self.maxHeight,
                                self.branches, self.getRgb(self.leafColor1), self.getRgb(self.leafColor2),
                                self.getRgb(self.leafColor3), self.getRgb(self.trunkColor), 'ParkTree#',
                                posX, posZ)

    def createPark(self):
        if self.updateValue():
            if cmds.objExists('Park'):
                cmds.delete('Park')

            self.library.CreatePark(self.parkWidth, self.parkLength, self.treesDistribution, self.bushesDistribution, self.createTreeAt)
            cmds.select(clear=True)
            print 'Park Created'

    def resetValue(self):
        pass

    def getRgb(self, color):
        return [color.red()/255.0, color.green()/255.0, color.blue()/255.0]