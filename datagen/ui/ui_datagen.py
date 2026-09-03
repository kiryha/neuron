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
from PySide6.QtWidgets import (QApplication, QComboBox, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QSpacerItem,
    QSplitter, QVBoxLayout, QWidget)

class Ui_Datagen(object):
    def setupUi(self, Datagen):
        if not Datagen.objectName():
            Datagen.setObjectName(u"Datagen")
        Datagen.resize(402, 413)
        self.verticalLayout = QVBoxLayout(Datagen)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(Datagen)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.label = QLabel(self.splitter)
        self.label.setObjectName(u"label")
        self.splitter.addWidget(self.label)
        self.boxJSONName = QComboBox(self.splitter)
        self.boxJSONName.setObjectName(u"boxJSONName")
        self.splitter.addWidget(self.boxJSONName)

        self.verticalLayout.addWidget(self.splitter)

        self.btnBuildData = QPushButton(Datagen)
        self.btnBuildData.setObjectName(u"btnBuildData")
        self.btnBuildData.setMinimumSize(QSize(0, 50))

        self.verticalLayout.addWidget(self.btnBuildData)

        self.btnBuildPrompts = QPushButton(Datagen)
        self.btnBuildPrompts.setObjectName(u"btnBuildPrompts")
        self.btnBuildPrompts.setMinimumSize(QSize(0, 50))

        self.verticalLayout.addWidget(self.btnBuildPrompts)

        self.btnReloadData = QPushButton(Datagen)
        self.btnReloadData.setObjectName(u"btnReloadData")
        self.btnReloadData.setMinimumSize(QSize(0, 50))

        self.verticalLayout.addWidget(self.btnReloadData)

        self.listMaterials = QListWidget(Datagen)
        self.listMaterials.setObjectName(u"listMaterials")

        self.verticalLayout.addWidget(self.listMaterials)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(Datagen)

        QMetaObject.connectSlotsByName(Datagen)
    # setupUi

    def retranslateUi(self, Datagen):
        Datagen.setWindowTitle(QCoreApplication.translate("Datagen", u"D A T A G E N", None))
        self.label.setText(QCoreApplication.translate("Datagen", u"Material Library JSON", None))
        self.btnBuildData.setText(QCoreApplication.translate("Datagen", u"Build Materials Data", None))
        self.btnBuildPrompts.setText(QCoreApplication.translate("Datagen", u"Build Material Prompts", None))
        self.btnReloadData.setText(QCoreApplication.translate("Datagen", u"Reload Data", None))
    # retranslateUi

