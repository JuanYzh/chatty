# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'new_chat_setting.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_NewChat(object):
    def setupUi(self, Dialog_NewChat):
        Dialog_NewChat.setObjectName("Dialog_NewChat")
        Dialog_NewChat.resize(500, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog_NewChat)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_5 = QtWidgets.QLabel(Dialog_NewChat)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Dialog_NewChat)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.chat_title = QtWidgets.QLineEdit(Dialog_NewChat)
        self.chat_title.setObjectName("chat_title")
        self.horizontalLayout.addWidget(self.chat_title)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 8)
        self.horizontalLayout.setStretch(2, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtWidgets.QLabel(Dialog_NewChat)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.comboBox_module = QtWidgets.QComboBox(Dialog_NewChat)
        self.comboBox_module.setObjectName("comboBox_module")
        self.horizontalLayout_2.addWidget(self.comboBox_module)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 8)
        self.horizontalLayout_2.setStretch(2, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(Dialog_NewChat)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.horizontalSlider_creative = QtWidgets.QSlider(Dialog_NewChat)
        self.horizontalSlider_creative.setAutoFillBackground(False)
        self.horizontalSlider_creative.setMaximum(10)
        self.horizontalSlider_creative.setProperty("value", 5)
        self.horizontalSlider_creative.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_creative.setObjectName("horizontalSlider_creative")
        self.horizontalLayout_3.addWidget(self.horizontalSlider_creative)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 8)
        self.horizontalLayout_3.setStretch(2, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(Dialog_NewChat)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.textEdit_scenario = QtWidgets.QTextEdit(Dialog_NewChat)
        self.textEdit_scenario.setObjectName("textEdit_scenario")
        self.horizontalLayout_4.addWidget(self.textEdit_scenario)
        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(1, 9)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog_NewChat)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog_NewChat)
        self.buttonBox.accepted.connect(Dialog_NewChat.accept) # type: ignore
        self.buttonBox.rejected.connect(Dialog_NewChat.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog_NewChat)

    def retranslateUi(self, Dialog_NewChat):
        _translate = QtCore.QCoreApplication.translate
        Dialog_NewChat.setWindowTitle(_translate("Dialog_NewChat", "NewChat"))
        self.label_5.setText(_translate("Dialog_NewChat", "Chat setting"))
        self.label.setText(_translate("Dialog_NewChat", "Title"))
        self.chat_title.setPlaceholderText(_translate("Dialog_NewChat", "New Chat"))
        self.label_3.setText(_translate("Dialog_NewChat", "Module"))
        self.label_2.setText(_translate("Dialog_NewChat", "Creative"))
        self.label_4.setText(_translate("Dialog_NewChat", "scenario"))
        self.textEdit_scenario.setPlaceholderText(_translate("Dialog_NewChat", "You are a helpful assistant, you call yourself Chatty."))