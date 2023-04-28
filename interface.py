# -*- coding: utf-8 -*-
# Copyright (c) 2023 by WenHuan Yang-Zhang.
# Date: 2023-04
# Ich und google :)
"""
Description:

"""
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDialog, QShortcut, QMessageBox, QMenu, QAction, QListWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QKeySequence
from PyQt5.QtCore import QModelIndex, Qt
from chatty_ux_main import Ui_MainWindow
from new_chat_setting import Ui_Dialog_NewChat
from api_key import Ui_Dialog_ApiKey
from gpt_requests import gpt_rob
import datetime
import database_handle
import openai


# Default model settings
class Utils:
    model = ["gpt-3.5-turbo", "gpt-4"]
    creative = 5
    scenario = "You are a helpful assistant, you call yourself Chatty."
    message = []


# Thread Configuration
class MyThread(QtCore.QThread):
    result_ready = QtCore.pyqtSignal(object)

    def __init__(self, thread_request:str, **kwargs:any):
        """
        :param thread_request: Thread Identification Keywords, identify threads and determine which method to call.
        :param kwargs:  Inputs of the thread.
        """
        super().__init__()
        self.thread_request = thread_request
        self.kwargs = kwargs

    def run(self) -> any:
        """
        :return: Output of the thread
        """
        if self.thread_request == "openai_requests":
            chat_setting = self.kwargs.get("chat_setting")
            message = [{"role":val.get("role"), "content":val.get("content")}
                       for val in self.kwargs.get("chat_setting").get("message")]
            title = self.kwargs.get("title")
            try:
                result = gpt_rob.openai_requests(chat_setting, message)
            except Exception as err:
                result = str(err)
        self.result_ready.emit([result, title])


# Custom additional window
class CustomDialog(QDialog, Ui_Dialog_NewChat):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        for model in Utils.model:
            self.comboBox_module.addItem(model)


# Custom API KEY window
class CustomDialogApiKey(QDialog, Ui_Dialog_ApiKey):
    def __init__(self, keys):
        super().__init__()
        self.setupUi(self)
        for key in keys:
            if key:
                self.comboBox_key.addItem(key)
        self.pushButton_clean_apikey.clicked.connect(lambda: self.comboBox_key.clear())


class ChatUxMain(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        super().setupUi(self)
        super().retranslateUi(self)
        self.conn = database_handle.create_database_and_tables()
        self.chat_map: dict[str[dict], ...] = {}  # Cache - conversation history and settings
        # ========================================== default param
        self.du_title = "du: " # Used to identify the username
        self.assistant_title = "Chatty: " # assistant name
        self.now_title = None # the current ongoing conversation
        self.last_send = None #  Record the last sent text
        # ========================================== function
        self.add_widgets()
        self.buttons_actions() # Add behavior to buttons
        self.menu_actions()
        self.textEdit_user.setReadOnly(False) # Set up user input box
        shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Return), self.textEdit_user)
        shortcut.activated.connect(self.on_shortcut_activated)
        self.chat_history_model = QStandardItemModel(self.listView_history) # Set up history conversation box
        self.listView_history.setModel(self.chat_history_model)
        self.listView_history.clicked.connect(self.clicked_chat_title)
        self.listView_history.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView_history.customContextMenuRequested.connect(self.show_context_menu)
        # =========================================
        self.tab_page.setHidden(not self.tab_page.isHidden()) # Set the right side as a closable tab.
        # self.Chat
        # self.label_creative
        # self.textEdit_dialogue
        # self.textEdit_user
        # self.statusbar
        # thread setting
        self.thread_openai = None
        # data_base
        self.load_database()
        if not self.api_key:
            self.open_api_window()

    def show_context_menu(self, point):
        """
        Pop-up menu, display delete
        """
        context_menu = QMenu(self.listView_history)

        delete_action = QAction("Delete", self.listView_history)
        delete_action.triggered.connect(self.delete_item)
        context_menu.addAction(delete_action)

        global_position = self.listView_history.viewport().mapToGlobal(point)
        context_menu.exec_(global_position)

    def delete_item(self):
        """
        delete a item from chat titles
        :return:
        """
        index = self.listView_history.currentIndex()
        title = index.data()
        database_handle.delete_chat(self.conn, title)
        self.chat_map.pop(title, None)
        if index.isValid():
            self.chat_history_model.removeRow(index.row())
        self.tab_page.setHidden(True)

    def load_database(self):
        """
         Load information, including keys, chat history, etc.
        :return:
        """
        self.api_key_list = database_handle.api_key_get(self.conn)
        self.chat_map = database_handle.load_chat_map(self.conn)
        if len(self.api_key_list) > 0:
            self.api_key = self.api_key_list[0]
            openai.api_key = database_handle.decrypt_key(self.api_key)
        else:
            self.api_key = None
        for title, val in self.chat_map.items():
            item_text = "{item}".format(item=title)
            model = val.get("model")
            creative = val.get("creative")
            scenario = val.get("scenario")
            item = QStandardItem(item_text)
            item.setToolTip(f"model: {model}\ncreative: {creative}\nscenario: {scenario}")
            self.chat_history_model.appendRow(item)

    def open_api_window(self):
        """
        api key
        :return:
        """
        def clean_apikey():
            self.api_key_list = []

        api_win = CustomDialogApiKey(self.api_key_list)
        api_win.pushButton_clean_apikey.clicked.connect(lambda :clean_apikey())
        result = api_win.exec_()
        if result == QtWidgets.QDialog.Accepted:
            if api_win.comboBox_key.currentText():
                self.api_key_list = [api_win.comboBox_key.currentText()]
            for index in range(api_win.comboBox_key.count()):
                key = api_win.comboBox_key.itemText(index)
                if key and key not in self.api_key_list:
                    self.api_key_list.append(api_win.comboBox_key.itemText(index))
        if len(self.api_key_list) > 0:
            self.api_key = self.api_key_list[0]
            openai.api_key = database_handle.decrypt_key(self.api_key)
        database_handle.insert_setting(self.conn, self.api_key_list)

    def on_shortcut_activated(self):
        if not self.textEdit_user.hasFocus() or self.textEdit_user.isReadOnly():
            return
        self.send()

    def closeEvent(self, event):
        """
        Set the behavior when closing the program, wait for the thread to finished.
        :param event:
        :return:
        """
        self.close_chat()
        # database_handle.insert_setting(self.conn, self.api_key_list)
        if self.thread_openai:
            self.thread_openai.terminate()
            # self.thread_openai.wait()
        event.accept()
        self.conn.close()

    def add_widgets(self):
        self._translate = QtCore.QCoreApplication.translate
        # add a send button
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./ui/icons/paper-plane-return.png"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_send = QtWidgets.QPushButton(self.textEdit_user)
        self.pushButton_send.setObjectName("pushButton_send")
        self.pushButton_send.setIcon(icon)
        # add regenerate button
        self.icon_regenerate = QtGui.QIcon()
        self.icon_regenerate.addPixmap(QtGui.QPixmap("./ui/icons/arrow-circle-225-left.png"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icon_stop_response = QtGui.QIcon()
        self.icon_stop_response.addPixmap(QtGui.QPixmap("./ui/icons/control-stop-square.png"),
                                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_regenerate = QtWidgets.QPushButton(self.Chat)
        self.pushButton_regenerate.setObjectName("pushButton_regenerate")
        self.pushButton_regenerate.setText(self._translate("MainWindow", "Regenerate"))
        self.pushButton_regenerate.setIcon(self.icon_regenerate)
        self.pushButton_regenerate.raise_()
        self.pushButton_regenerate.setVisible(False)

    def resizeEvent(self, event):
        """
        Set the position of some components, and the position will change every time the window is modified.
        :param event:
        :return:
        """
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
        self.pushButton_clean.clicked.connect(self.clean_histories)
        self.pushButton_close.clicked.connect(self.close_chat)
        # dialogue buttons
        self.pushButton_send.clicked.connect(self.send)
        self.pushButton_regenerate.clicked.connect(lambda : self.regenerate(self.pushButton_regenerate))

    def menu_actions(self):
        def setting(qaction):
            if qaction.text() == "Preferences":
                QMessageBox.information(self, "hi", "pop up preferences window")

        def user_help(qaction):
            if qaction.text() == "How to use":
                QMessageBox.information(self, "hi", "pop up how to use window")
            elif qaction.text() == "About me":
                message_box = QMessageBox()
                message_box.setIcon(QMessageBox.Information)
                message_box.setWindowTitle("about Chatty")
                label = QtWidgets.QLabel()
                label.setText('''<a href="https://p.yusukekamiyamane.com/">icons</a> <br>
                    <a href="https://creativecommons.org/licenses/by/3.0/">icons licenses</a> <br> <br>
                    <a href="https://github.com/JuanYzh/chatty">github me</a> <br>
                    Acknowledgements: <br> <br>
                    <a href="https://www.youtube.com/watch?v=rZcdhles6vQ&list=
                    PLCC34OHNcOtpmCA8s_dpPMvQLyHbvxocY&index=1">thanks to John Elder (Youtuber)</a> <br>
                    ''')
                layout = message_box.layout()
                layout.addWidget(label, 0, 1)
                label.setOpenExternalLinks(True)
                message_box.exec()
            elif qaction.text() == "Feedback":
                QMessageBox.information(self, "hi", "pop up feedback window")

        self.actionPre.triggered.connect(lambda : setting(self.actionPre))
        self.actionHow_to_use.triggered.connect(lambda : user_help(self.actionHow_to_use))
        self.actionAbout_me.triggered.connect(lambda : user_help(self.actionAbout_me))
        self.actionFeedback.triggered.connect(lambda : user_help(self.actionFeedback))
        self.actionapi_key.triggered.connect(lambda : self.open_api_window())

    def new_chat(self):
        """
         Create a new conversation and set it up.
        self.chat_title, self.comboBox_module, self.horizontalSlider_creative, self.textEdit_scenario
        :return:
        """
        window_new_chat = CustomDialog()
        result = window_new_chat.exec_()
        if result == QtWidgets.QDialog.Accepted:
            title = window_new_chat.chat_title.text()
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
            self.now_title = title
            scenario = window_new_chat.textEdit_scenario.toPlainText()
            model = window_new_chat.comboBox_module.itemText(0)
            creative = window_new_chat.horizontalSlider_creative.value()
            self.label_creative.setText(str(creative))
            if not scenario:
                scenario = "You are a helpful assistant, you call yourself Chatty."
            self.chat_map.update({title:{
                "model":model,
                "creative":creative,
                "scenario":scenario,
                "message":[],
                "create_time":datetime.datetime.now().timestamp()
            }})
            item_text = "{item}".format(item=title)
            item = QStandardItem(item_text)
            item.setToolTip(f"model: {model}\ncreative: {creative}\nscenario: {scenario}")
            self.chat_history_model.appendRow(item)
            if self.tab_page.isHidden():
                self.tab_page.setHidden(False)
            self.textEdit_dialogue.setText("")
            self.pushButton_regenerate.setVisible(False)
            self.textEdit_user.setReadOnly(False)
        else:
            print("Dialog result: Rejected")

    def clicked_chat_title(self, index: QModelIndex):
        """
        When clicked a title switch to other conversations.
        :param index:
        :return:
        """
        item_text = index.data()
        if self.tab_page.isHidden():
            self.tab_page.setHidden(False)
        self.now_title = item_text
        self.textEdit_dialogue.setText("")
        for message in self.chat_map.get(self.now_title).get("message"):
            chat_title = self.du_title if message.get("role") == 'user' else self.assistant_title
            self.textEdit_dialogue.append(chat_title + message.get("content") + "\n")
        self.pushButton_regenerate.setVisible(False)

    def change_creative(self, button):
        """
        Change the randomness of the conversation based on the current conversation.
        :param button:
        :return:
        """
        creative = int(self.label_creative.text())
        if button.text() == "+":
            if creative >= 10:
                return
            creative += 1
            self.label_creative.setText(str(creative))
            self.chat_map.get(self.now_title).update({"creative":creative})
        else:
            if creative <= 0:
                return
            creative -= 1
            self.label_creative.setText(str(creative))
            self.chat_map.get(self.now_title).update({"creative": creative})
        model = self.chat_map.get(self.now_title).get("model")
        scenario = self.chat_map.get(self.now_title).get("scenario")
        for i in range(self.chat_history_model.rowCount()):
            if self.chat_history_model.item(i).text() == self.now_title:
                item_text = "{item}".format(item=self.now_title)
                item = QStandardItem(item_text)
                item.setToolTip(f"model: {model}\ncreative: {creative}\nscenario: {scenario}")
                self.chat_history_model.setItem(i, 0, item)
                break

    def edit_chat(self):
        """
        Edit the settings of an existing conversation.
        """
        now_title = self.now_title
        edit_chat = CustomDialog()
        edit_chat.chat_title.setText(now_title)
        edit_chat.chat_title.setReadOnly(True)
        edit_chat.textEdit_scenario.setText(self.chat_map.get(now_title).get("scenario"))
        edit_chat.comboBox_module.setCurrentText(self.chat_map.get(now_title).get("model"))
        edit_chat.horizontalSlider_creative.setValue(self.chat_map.get(now_title).get("creative"))
        result = edit_chat.exec_()
        if result == QtWidgets.QDialog.Accepted:
            scenario = edit_chat.textEdit_scenario.toPlainText()
            model = edit_chat.comboBox_module.currentText()
            creative = edit_chat.horizontalSlider_creative.value()
            self.label_creative.setText(str(creative))
            if not scenario:
                scenario = "You are a helpful assistant, you call yourself Chatty."
            self.chat_map.update({now_title: {
                "model": model,
                "creative": creative,
                "scenario": scenario,
                "message": self.chat_map.get(now_title).get("message"),
                "create_time":self.chat_map.get(now_title).get("create_time")
            }})
            for i in range(self.chat_history_model.rowCount()):
                if self.chat_history_model.item(i).text() == now_title:
                    item_text = "{item}".format(item=now_title)
                    item = QStandardItem(item_text)
                    item.setToolTip(f"model: {model}\ncreative: {creative}\nscenario: {scenario}")
                    self.chat_history_model.setItem(i, 0, item)
                    break
        else:
            print("Dialog result: Rejected")

    def clean_histories(self):
        """
        Clear the conversation history, but keep the settings.
        :return:
        """
        self.chat_map.get(self.now_title)["message"] = []
        self.textEdit_dialogue.setText("")
        self.pushButton_regenerate.setVisible(False)
        database_handle.delete_chat_history_by_title_id(self.conn, self.now_title)

    def close_chat(self):
        """
        Close the conversation window.
        :return:
        """
        self.tab_page.setHidden(not self.tab_page.isHidden())
        self.now_title = None
        # insert title
        chat_title = [(title, val.get("create_time", None)) for title, val in self.chat_map.items()]
        database_handle.insert_chat_title(self.conn, chat_title)
        # insert or update chat_config
        chat_title_id = database_handle.title_id_get(self.conn, [titles[0] for titles in chat_title])
        chat_config = [{
            "title_id":chat_title_id.get(title),
            "role":"system",
            "content":val.get("scenario"),
            "token":0,
            "max_memory":9999,
            "temperature":val.get("creative"),
            "model":val.get("model")
        }
        for title, val in self.chat_map.items()]
        database_handle.insert_or_update_chat_config(self.conn, chat_config)
        # insert chat_history
        chat_history = [
            {
            "title_id":chat_title_id.get(title),
            "role":val.get("role"),
            "content":val.get("content"),
            "time":val.get("time"),
            "token":0,
            "page":None,
        }
        for title, val_ in self.chat_map.items() for val in val_.get("message")
        ]
        database_handle.insert_chat_history_bulk(self.conn, chat_history)


    def set_reg_stop(self, state:str="stop"):
        """
        Set the style of the "Regenerate" and "Stop" buttons, and change whether the user input box is editable.
        :param state: str
        :return:
        """
        if not self.pushButton_regenerate.isVisible():
            self.pushButton_regenerate.setVisible(True)
        if state == "stop":
            self.pushButton_regenerate.setText(self._translate("MainWindow", "Stop"))
            self.pushButton_regenerate.setIcon(self.icon_stop_response)
            self.textEdit_user.setReadOnly(False)
        else:
            self.pushButton_regenerate.setText(self._translate("MainWindow", "Regenerate"))
            self.pushButton_regenerate.setIcon(self.icon_regenerate)

    def send(self, last_send:str=None, regenerte:bool=False):
        """
        Send the conversation and start a thread to receive replies.
        :param last_send:
        :param regenerte: Whether the conversation in this paragraph is regenerated.
        :return:
        """
        if self.thread_openai and not self.thread_openai.isFinished():
            return
        if not last_send:
            toPlainText = self.textEdit_user.toPlainText()
        else:
            toPlainText = last_send
        if toPlainText:
            if not toPlainText.strip(): # if nothing typed return
                return
            self.last_send = toPlainText
            self.textEdit_user.setText("")
            now_title = self.now_title
            if not regenerte:
                message = self.chat_map.get(now_title).get("message")
                message.append({"role": "user", "content": self.last_send, "time":datetime.datetime.now().timestamp()})
                self.textEdit_dialogue.append("du: " + self.last_send + "\n")
            self.thread_openai = MyThread(
                thread_request="openai_requests", chat_setting=self.chat_map.get(now_title), title=now_title)
            self.thread_openai.result_ready.connect(self.receive_respond)
            self.thread_openai.start()
            self.set_reg_stop(state="stop")
            self.textEdit_user.setReadOnly(True)

    def regenerate(self, button):
        """
        Button to stop the thread receiving conversation or regenerate the conversation (resend the previous content
        :param button: the regenerate_stop push button
        :return:
        """
        if button.text() == "Regenerate" and self.last_send:
            message = self.chat_map.get(self.now_title).get("message")
            if not message:
                return
            if message[-1].get("role") == "assistant":
                message.pop()
            self.set_reg_stop(state="stop")
            self.send(message[-1].get("content"), regenerte=True)
        elif button.text() == "Stop":
            self.textEdit_user.setReadOnly(False)
            self.thread_openai.terminate()
            self.set_reg_stop(state="res")

    def receive_respond(self, result):
        """
        After the thread ends, receive the reply and add it to the conversation history.
        If the current conversation has not changed, display it.
        :param result: reply of the thread
        :return:
        """
        anser, anser_title = result
        message = self.chat_map.get(anser_title).get("message")
        message.append({"role": "assistant", "content": anser, "time":datetime.datetime.now().timestamp()})
        if self.now_title == anser_title:
            self.textEdit_dialogue.append("Chatty: " + anser + "\n")
            self.set_reg_stop(state="reg")
            self.textEdit_user.setReadOnly(False)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = ChatUxMain()
    MainWindow.show()
    sys.exit(app.exec_())
