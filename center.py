#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial

This program centers a window
on the screen.

Author: Jan Bodnar
Website: zetcode.com
Last edited: August 2017
"""

import sys
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        self.resize(250, 150)
        self.center()

        self.setWindowTitle('Center')
        self.show()


    def center(self):

        qr = self.frameGeometry() #获取主窗口所在的框架
        cp = QDesktopWidget().availableGeometry().center() #获取显示器的分辨率, 然后得到屏幕中间点的位置
        qr.moveCenter(cp) #把主窗口框架的中心点放置到屏幕的中心位置
        self.move(qr.topLeft()) #把主窗口的左上角移动到其框架的左上角


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())