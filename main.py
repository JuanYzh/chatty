# -*- coding: utf-8 -*-
# Copyright (c) 2023 by WenHuan Yang-Zhang.
# Date: 2023-03.01
# Ich und google :)
import sys
from PyQt5 import QtWidgets
from interface import ChatUxMain
from gpt_requests import gpt_rob


class chatty:
    def __init__(self):
        pass

    def inter_face(self):
        pass


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = ChatUxMain()
    MainWindow.show()
    sys.exit(app.exec_())