# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_datarender.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QSplitter, QVBoxLayout, QWidget)

class Ui_Datarender(object):
    def setupUi(self, Datarender):
        if not Datarender.objectName():
            Datarender.setObjectName(u"Datarender")
        Datarender.resize(414, 339)
        self.verticalLayout = QVBoxLayout(Datarender)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.linObjectSize = QLineEdit(Datarender)
        self.linObjectSize.setObjectName(u"linObjectSize")

        self.gridLayout.addWidget(self.linObjectSize, 1, 2, 1, 1)

        self.label_2 = QLabel(Datarender)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)

        self.label = QLabel(Datarender)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.linNumCameras = QLineEdit(Datarender)
        self.linNumCameras.setObjectName(u"linNumCameras")

        self.gridLayout.addWidget(self.linNumCameras, 1, 0, 1, 1)

        self.label_3 = QLabel(Datarender)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)

        self.linFocalLen = QLineEdit(Datarender)
        self.linFocalLen.setObjectName(u"linFocalLen")

        self.gridLayout.addWidget(self.linFocalLen, 1, 1, 1, 1)

        self.linMargin = QLineEdit(Datarender)
        self.linMargin.setObjectName(u"linMargin")

        self.gridLayout.addWidget(self.linMargin, 1, 3, 1, 1)

        self.label_4 = QLabel(Datarender)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 0, 3, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.btnCameraDome = QPushButton(Datarender)
        self.btnCameraDome.setObjectName(u"btnCameraDome")
        self.btnCameraDome.setMinimumSize(QSize(0, 50))

        self.verticalLayout.addWidget(self.btnCameraDome)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.linDatasetName = QLineEdit(Datarender)
        self.linDatasetName.setObjectName(u"linDatasetName")

        self.gridLayout_2.addWidget(self.linDatasetName, 1, 1, 1, 1)

        self.label_5 = QLabel(Datarender)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 0, 0, 1, 1)

        self.linDatasetRoot = QLineEdit(Datarender)
        self.linDatasetRoot.setObjectName(u"linDatasetRoot")

        self.gridLayout_2.addWidget(self.linDatasetRoot, 1, 0, 1, 1)

        self.label_6 = QLabel(Datarender)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_2.addWidget(self.label_6, 0, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_2)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.chbSingleCamera_2 = QCheckBox(Datarender)
        self.chbSingleCamera_2.setObjectName(u"chbSingleCamera_2")
        self.chbSingleCamera_2.setChecked(True)

        self.gridLayout_4.addWidget(self.chbSingleCamera_2, 0, 0, 1, 1)

        self.chbSingleGeometry_2 = QCheckBox(Datarender)
        self.chbSingleGeometry_2.setObjectName(u"chbSingleGeometry_2")
        self.chbSingleGeometry_2.setChecked(True)

        self.gridLayout_4.addWidget(self.chbSingleGeometry_2, 0, 1, 1, 1)

        self.linSingleCameraName = QLineEdit(Datarender)
        self.linSingleCameraName.setObjectName(u"linSingleCameraName")

        self.gridLayout_4.addWidget(self.linSingleCameraName, 1, 0, 1, 1)

        self.linSingleGeometryName = QLineEdit(Datarender)
        self.linSingleGeometryName.setObjectName(u"linSingleGeometryName")

        self.gridLayout_4.addWidget(self.linSingleGeometryName, 1, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_4)

        self.splitter = QSplitter(Datarender)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.label_9 = QLabel(self.splitter)
        self.label_9.setObjectName(u"label_9")
        self.splitter.addWidget(self.label_9)
        self.boxJSONName = QComboBox(self.splitter)
        self.boxJSONName.setObjectName(u"boxJSONName")
        self.splitter.addWidget(self.boxJSONName)

        self.verticalLayout.addWidget(self.splitter)

        self.btnRenderDataset = QPushButton(Datarender)
        self.btnRenderDataset.setObjectName(u"btnRenderDataset")
        self.btnRenderDataset.setMinimumSize(QSize(0, 50))

        self.verticalLayout.addWidget(self.btnRenderDataset)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(Datarender)

        QMetaObject.connectSlotsByName(Datarender)
    # setupUi

    def retranslateUi(self, Datarender):
        Datarender.setWindowTitle(QCoreApplication.translate("Datarender", u"D A T A R E N D E R", None))
        self.linObjectSize.setText(QCoreApplication.translate("Datarender", u"2", None))
        self.label_2.setText(QCoreApplication.translate("Datarender", u"Focal Length", None))
        self.label.setText(QCoreApplication.translate("Datarender", u"Num of Cams", None))
        self.linNumCameras.setText(QCoreApplication.translate("Datarender", u"8", None))
        self.label_3.setText(QCoreApplication.translate("Datarender", u"Object Size", None))
        self.linFocalLen.setText(QCoreApplication.translate("Datarender", u"28", None))
        self.linMargin.setText(QCoreApplication.translate("Datarender", u"1.25", None))
        self.label_4.setText(QCoreApplication.translate("Datarender", u"Frame Margin", None))
        self.btnCameraDome.setText(QCoreApplication.translate("Datarender", u"Create Camera Dome", None))
        self.linDatasetName.setText(QCoreApplication.translate("Datarender", u"material_hero_v0", None))
        self.label_5.setText(QCoreApplication.translate("Datarender", u"Dataset Root", None))
        self.linDatasetRoot.setText(QCoreApplication.translate("Datarender", u"E:/Projects/neuron_data/datasets", None))
        self.label_6.setText(QCoreApplication.translate("Datarender", u"Dataset Name", None))
        self.chbSingleCamera_2.setText(QCoreApplication.translate("Datarender", u"Single Camera", None))
        self.chbSingleGeometry_2.setText(QCoreApplication.translate("Datarender", u"Single Geometry", None))
        self.linSingleCameraName.setText(QCoreApplication.translate("Datarender", u"cam_001", None))
        self.linSingleGeometryName.setText(QCoreApplication.translate("Datarender", u"sculpted_rubber_toy", None))
        self.label_9.setText(QCoreApplication.translate("Datarender", u"Material Library JSON", None))
        self.btnRenderDataset.setText(QCoreApplication.translate("Datarender", u"Render Dataset", None))
    # retranslateUi

