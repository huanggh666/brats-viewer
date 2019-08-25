# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\code\vscode\brats-viewer/textviewer.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(403, 291)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/source/12.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_1 = QtWidgets.QPushButton(Form)
        self.pushButton_1.setObjectName("pushButton_1")
        self.horizontalLayout.addWidget(self.pushButton_1)
        self.comboBox = QtWidgets.QComboBox(Form)
        self.comboBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.comboBox.setAutoFillBackground(False)
        self.comboBox.setEditable(False)
        self.comboBox.setModelColumn(0)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout.addWidget(self.comboBox)
        self.pushButton_3 = QtWidgets.QPushButton(Form)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        self.comboBox.setCurrentIndex(0)
        self.pushButton_2.released.connect(Form.close)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Dice Value"))
        self.pushButton_1.setText(_translate("Form", "打开"))
        self.comboBox.setWhatsThis(_translate("Form", "选择显示的内容"))
        self.comboBox.setCurrentText(_translate("Form", "Mean"))
        self.comboBox.setItemText(0, _translate("Form", "Mean"))
        self.comboBox.setItemText(1, _translate("Form", "StdDev"))
        self.comboBox.setItemText(2, _translate("Form", "Median"))
        self.comboBox.setItemText(3, _translate("Form", "25quantile"))
        self.comboBox.setItemText(4, _translate("Form", "75quantile"))
        self.pushButton_3.setText(_translate("Form", "自动复制（开）"))
        self.pushButton_2.setText(_translate("Form", "关闭"))


import viewer_rc
