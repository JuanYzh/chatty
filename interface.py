# -*- coding: utf-8 -*-
# Copyright (c) 2023 by WenHuan Yang-Zhang.
# Date: 2023-04
# Ich und google :)
"""
Description:

"""
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, \
    QPushButton, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QModelIndex
from chatty_ux_main import Ui_MainWindow
from new_chat_setting import Ui_Dialog_NewChat
from gpt_requests import gpt_rob


class Utils:
    model = ["gpt-3.5-turbo", "gpt-4"]
    creative = 5
    scenario = "You are a helpful assistant, you call yourself Chatty."
    message = []


class CustomDialog(QDialog, Ui_Dialog_NewChat):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        for model in Utils.model:
            self.comboBox_module.addItem(model)


class ChatUxMain(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        super().setupUi(self)
        super().retranslateUi(self)
        self.last_send = None
        self.chat_setting = {
            "title":"",
            "model": Utils.model[0],
            "creative": Utils.creative,
            "scenario": Utils.scenario
        }
        self.chat_map = {}
        self.add_widgets()
        self.buttons_actions()
        self.menu_actions()
        self.textEdit_user.setReadOnly(False)
        self.model = QStandardItemModel(self.listView_history)
        self.listView_history.setModel(self.model)
        self.listView_history.clicked.connect(self.clicked_chat_title)
        # =========================================
        self.tab_page.setHidden(not self.tab_page.isHidden())
        self.Chat
        self.label_creative

        self.textEdit_dialogue
        self.textEdit_user
        self.statusbar

    def add_widgets(self):
        self._translate = QtCore.QCoreApplication.translate
        # add a send button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./ui/icon/paper-plane-return.png"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_send = QtWidgets.QPushButton(self.textEdit_user)
        self.pushButton_send.setObjectName("pushButton_send")
        self.pushButton_send.setIcon(icon)
        # add regenerate button
        self.icon_regenerate = QtGui.QIcon()
        self.icon_regenerate.addPixmap(QtGui.QPixmap("./ui/icon/arrow-circle-225-left.png"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icon_stop_response = QtGui.QIcon()
        self.icon_stop_response.addPixmap(QtGui.QPixmap("./ui/icon/control-stop-square.png"),
                                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_regenerate = QtWidgets.QPushButton(self.Chat)
        self.pushButton_regenerate.setObjectName("pushButton_regenerate")
        self.pushButton_regenerate.setText(self._translate("MainWindow", "Regenerate"))
        self.pushButton_regenerate.setIcon(self.icon_regenerate)
        self.pushButton_regenerate.raise_()
        self.pushButton_regenerate.setVisible(False)

    def resizeEvent(self, event):
        # pushButton_send bnutton
        button_size = self.pushButton_send.sizeHint()
        button_x = self.textEdit_user.width() - button_size.width() - 5
        button_y = self.textEdit_user.height() - button_size.height() - 5
        self.pushButton_send.move(button_x, button_y)
        # pushButton_regenerate button
        button_size = self.pushButton_regenerate.sizeHint()
        button_x = int((self.textEdit_user.width() - button_size.width()) / 2)
        button_y = int(self.Chat.height() - self.textEdit_user.height() - button_size.height())
        self.pushButton_regenerate.move(button_x, button_y)
        super().resizeEvent(event)

    def buttons_actions(self):
        # new chat and history
        self.newChat.clicked.connect(self.new_chat)
        # edit chat behave buttons
        self.pushButton_reduce.clicked.connect(lambda : self.change_creative(self.pushButton_reduce))
        self.pushButton_plus.clicked.connect(lambda : self.change_creative(self.pushButton_plus))
        self.pushButton_edit.clicked.connect(self.edit_chat)
        self.pushButton_clearn.clicked.connect(self.clearn_histories)
        self.pushButton_close.clicked.connect(self.close_chat)
        # dialogue buttons
        self.pushButton_send.clicked.connect(self.send)
        self.pushButton_regenerate.clicked.connect(lambda : self.regenerate(self.pushButton_regenerate))

    def menu_actions(self):
        def setting(qaction):
            if qaction.text() == "Preferences":
                print("pop up preferences window")

        def user_help(qaction):
            if qaction.text() == "How to use":
                print("pop up how to use window")
            elif qaction.text() == "About me":
                print("pop up about me window")
            elif qaction.text() == "Feedback":
                print("pop up feedback window")

        def how_to_use(qaction):
            print("pop up how to use guide")

        def feedback(qaction):
            print("pop up feedback window")

        def about_me(qaction):
            print("pop uo how about me")

        self.actionPre.triggered.connect(lambda : setting(self.actionPre))
        self.actionHow_to_use.triggered.connect(lambda : user_help(self.actionHow_to_use))
        self.actionAbout_me.triggered.connect(lambda : user_help(self.actionAbout_me))
        self.actionFeedback.triggered.connect(lambda : user_help(self.actionFeedback))

    # create a new chat
    def new_chat(self):
        # print("create a new chat")
        """
        self.chat_title, self.comboBox_module, self.horizontalSlider_creative, self.textEdit_scenario
        :return:
        """
        self.window_new_chat = CustomDialog()
        result = self.window_new_chat.exec_()
        if result == QtWidgets.QDialog.Accepted:
            title = self.window_new_chat.chat_title.text()
            if not title:
                title = "New Chat"
            index = 1
            temp_title = title
            while temp_title in self.chat_map:
                temp_title = f"{title}_{index}"
                index += 1
                if index >= 100:
                    return
            title = temp_title
            scenario = self.window_new_chat.textEdit_scenario.toPlainText()
            model = self.window_new_chat.comboBox_module.itemText(0)
            creative = self.window_new_chat.horizontalSlider_creative.value()
            if not scenario:
                scenario = "You are a helpful assistant, you call yourself Chatty."
                print(title)
            self.chat_setting = {
                "title":title,
                "model":model,
                "creative":creative,
                "scenario":scenario
            }
            self.chat_map.update({title:{
                "model":model,
                "creative":creative,
                "scenario":scenario,
                "message":[]
            }})
            item_text = "{item}".format(index=(self.model.rowCount() + 1), item=title)
            item = QStandardItem(item_text)
            self.model.appendRow(item)
            if self.tab_page.isHidden():
                self.tab_page.setHidden(False)
        else:
            print("Dialog result: Rejected")

    # when click chat title
    def clicked_chat_title(self, index: QModelIndex):
        item_text = index.data()
        if self.tab_page.isHidden():
            self.tab_page.setHidden(False)

        print(self.chat_map)
        print("Clicked item: ", item_text)

    def change_creative(self, button):
        creative = int(self.label_creative.text())
        if button.text() == "+":
            print("+")
            if creative >= 10:
                return
            creative += 1
            self.label_creative.setText(str(creative))
            self.chat_setting.update({"creative":creative})
        else:
            print("-")
            if creative <= 0:
                return
            creative -= 1
            self.label_creative.setText(str(creative))
            self.chat_setting.update({"creative": creative})

    def edit_chat(self):
        print("pop out edit window")

    def clearn_histories(self):
        print("clean this conversasion")

    def close_chat(self):
        print("close this conversation")
        self.tab_page.setHidden(not self.tab_page.isHidden())

    def send(self):
        toPlainText = self.textEdit_user.toPlainText()
        if toPlainText:
            self.last_send = toPlainText
            self.textEdit_user.setText("")
            self.textEdit_dialogue.insertPlainText("du: " + self.last_send + "\n\n")
            self.pushButton_regenerate.setText(self._translate("MainWindow", "Regenerate"))
            self.pushButton_regenerate.setIcon(self.icon_regenerate)
            if not self.pushButton_regenerate.isVisible():
                self.pushButton_regenerate.setVisible(True)
            # gpt_rob.go_to_chat(self.last_send)
            now_title = self.chat_setting.get("title")
            message = self.chat_map.get(now_title).get("message")
            message.append({"role": "user", "content": self.last_send})
            anser = gpt_rob.openai_requests(self.chat_setting, message)
            message.append({"role": "assistant", "content": anser})
            self.textEdit_dialogue.append("Chatty: " + anser + "\n\n")
        else:
            self.pushButton_regenerate.setText(self._translate("MainWindow", "Stop respones"))
            self.pushButton_regenerate.setIcon(self.icon_stop_response)

    def regenerate(self, button):
        if button.text() == "Regenerate" and self.last_send:
            print(f"Regenerate: {self.last_send}")
        elif button.text() == "Stop respones":
            print("Stop respones")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = ChatUxMain()
    MainWindow.show()
    sys.exit(app.exec_())