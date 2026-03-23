# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_datagen.ui'
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
from PySide6.QtWidgets import (QApplication, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_Datagen(object):
    def setupUi(self, Datagen):
        if not Datagen.objectName():
            Datagen.setObjectName(u"Datagen")
        Datagen.resize(400, 102)
        self.verticalLayout = QVBoxLayout(Datagen)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.btnRun = QPushButton(Datagen)
        self.btnRun.setObjectName(u"btnRun")
        self.btnRun.setMinimumSize(QSize(0, 50))

        self.verticalLayout.addWidget(self.btnRun)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(Datagen)

        QMetaObject.connectSlotsByName(Datagen)
    # setupUi

    def retranslateUi(self, Datagen):
        Datagen.setWindowTitle(QCoreApplication.translate("Datagen", u"D A T A G E N", None))
        self.btnRun.setText(QCoreApplication.translate("Datagen", u"Run", None))
    # retranslateUi

