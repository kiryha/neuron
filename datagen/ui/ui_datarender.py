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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_Datarender(object):
    def setupUi(self, Datarender):
        if not Datarender.objectName():
            Datarender.setObjectName(u"Datarender")
        Datarender.resize(402, 158)
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
    # retranslateUi

