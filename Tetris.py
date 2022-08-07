#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial

This is a Tetris game clone.

Author: Jan Bodnar
Website: zetcode.com
Last edited: August 2017
"""

from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor
import sys, random

class Tetris(QMainWindow): #创建游戏

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self): #开始游戏
        '''initiates application UI'''

        self.tboard = Board(self)
        self.setCentralWidget(self.tboard)

        self.statusbar = self.statusBar() #状态栏
        self.tboard.msg2Statusbar[str].connect(self.statusbar.showMessage)

        self.tboard.start() #游戏开始

        self.resize(180, 380)
        self.center() #游戏面板居中
        self.setWindowTitle('Tetris')
        self.show()


    def center(self): #游戏面板居中
        '''centers the window on the screen'''

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2,
            (screen.height()-size.height())/2)


class Board(QFrame):

    msg2Statusbar = pyqtSignal(str)

    BoardWidth = 10
    BoardHeight = 22
    Speed = 300

    def __init__(self, parent):
        super().__init__(parent)

        self.initBoard()


    def initBoard(self): #初始化定时器及其他变量, 清空游戏面板
        '''initiates board'''

        self.timer = QBasicTimer()
        self.isWaitingAfterLine = False

        self.curX = 0
        self.curY = 0
        self.numLinesRemoved = 0
        self.board = []

        self.setFocusPolicy(Qt.StrongFocus)
        self.isStarted = False
        self.isPaused = False
        self.clearBoard() #面板上填充无形状


    def shapeAt(self, x, y): #以小方块为单位, 获取在面板中的位置
        '''determines shape at the board position'''
        #print("x", x, y, Board.BoardWidth, (y * Board.BoardWidth) + x)
        return self.board[(y * Board.BoardWidth) + x] #(x, y) 每行BoardWidth个小方块, y行第x列


    def setShapeAt(self, x, y, shape): #在面板的位置上设置指定形状
        '''sets a shape at the board'''

        self.board[(y * Board.BoardWidth) + x] = shape


    def squareWidth(self): #每个小块的宽度, 计算并返回每个块应该占用多少像素
        '''returns the width of one square'''
        #print("width", self.contentsRect().width(), "BoardWidth", Board.BoardWidth, self.contentsRect().width() // Board.BoardWidth)
        return self.contentsRect().width() // Board.BoardWidth #面板宽度 / 横向方块个数  = 每个方块宽度


    def squareHeight(self): #每个小块的高度, 计算并返回每个块应该占用多少像素
        '''returns the height of one square'''
        #print("height", self.contentsRect().height(), "BoardHeight", Board.BoardHeight, self.contentsRect().height() // Board.BoardHeight)
        return self.contentsRect().height() // Board.BoardHeight #面板高度 / 纵向方块个数  = 每个方块高度


    def start(self): #开始游戏, 发送信号显示状态栏, 清除面板, 创建新的块
        '''starts game'''
        print("starts game")
        if self.isPaused:
            return

        self.isStarted = True
        self.isWaitingAfterLine = False
        self.numLinesRemoved = 0
        self.clearBoard() #清除面板

        self.msg2Statusbar.emit(str(self.numLinesRemoved))

        self.newPiece() #创建新的块
        self.timer.start(Board.Speed, self)


    def pause(self): #暂停
        '''pauses game'''

        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.msg2Statusbar.emit("paused")

        else:
            self.timer.start(Board.Speed, self)
            self.msg2Statusbar.emit(str(self.numLinesRemoved))

        self.update()


    def paintEvent(self, event): #先画已经落下的块, 再画正在下落的块
        '''paints all shapes of the game'''

        painter = QPainter(self)
        rect = self.contentsRect() #画出矩形区域

        boardTop = rect.bottom() - Board.BoardHeight * self.squareHeight() #获取面板高度
        print("h", Board.BoardHeight, "w", Board.BoardWidth, "hh", self.squareHeight(), "bot", rect.bottom())
        for i in range(Board.BoardHeight): 
            for j in range(Board.BoardWidth):
                #print("shapeAt", j, Board.BoardHeight - i - 1)
                shape = self.shapeAt(j, Board.BoardHeight - i - 1) #已经落下的在 board[] 中的位置
                #print("shape", j, Board.BoardHeight - i - 1, shape)
                if shape != Tetrominoe.NoShape:
                    self.drawSquare(painter,
                        rect.left() + j * self.squareWidth(),
                        boardTop + i * self.squareHeight(), shape)

        if self.curPiece.shape() != Tetrominoe.NoShape: #画正在下落的块

            for i in range(4):

                x = self.curX + self.curPiece.x(i) #以块为单位, 块在面板中的位置  +  元组第 index 个的横坐标,单位也是块
                y = self.curY - self.curPiece.y(i) #以块的左下角为块中每个小块的坐标起点
                self.drawSquare(painter, rect.left() + x * self.squareWidth(),
                    boardTop + (Board.BoardHeight - y - 1) * self.squareHeight(),
                    self.curPiece.shape())


    def keyPressEvent(self, event): #键盘事件处理
        '''processes key press events'''

        if not self.isStarted or self.curPiece.shape() == Tetrominoe.NoShape: #游戏没有开始, 或没有新块
            super(Board, self).keyPressEvent(event)
            return

        key = event.key()

        if key == Qt.Key_P:
            self.pause()
            return

        if self.isPaused:
            return

        elif key == Qt.Key_Left:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)

        elif key == Qt.Key_Right:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)

        elif key == Qt.Key_Down:
            self.tryMove(self.curPiece.rotateRight(), self.curX, self.curY)

        elif key == Qt.Key_Up:
            self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)

        elif key == Qt.Key_Space:
            self.dropDown()

        elif key == Qt.Key_D:
            self.oneLineDown()

        else:
            super(Board, self).keyPressEvent(event)


    def timerEvent(self, event): #定时事件处理, 等一个方块下落完之后创建一个新的方块, 或者, 一个方块直接落到底
        '''handles timer event'''

        if event.timerId() == self.timer.timerId():

            if self.isWaitingAfterLine: #已经等待的下落完了
                self.isWaitingAfterLine = False
                self.newPiece()
            else: #没有下落完
                self.oneLineDown()

        else:
            super(Board, self).timerEvent(event)


    def clearBoard(self): #清除面板中的块
        '''clears shapes from the board'''

        for i in range(Board.BoardHeight * Board.BoardWidth):
            self.board.append(Tetrominoe.NoShape)


    def dropDown(self): #扔到可以到达的下端
        '''drops down a shape'''

        newY = self.curY

        while newY > 0:

            if not self.tryMove(self.curPiece, self.curX, newY - 1): #失败则跳出循环
                break

            newY -= 1

        self.pieceDropped()


    def oneLineDown(self): #直线下降
        '''goes one line down with a shape'''

        if not self.tryMove(self.curPiece, self.curX, self.curY - 1): #失败
            self.pieceDropped()


    def pieceDropped(self): #在底部设置形状, 删除满行, 创建新行
        '''after dropping shape, remove full lines and create new shape'''

        for i in range(4):

            x = self.curX + self.curPiece.x(i) #以块为单位, 块在面板中的位置  +  元组第 index 个的横坐标,单位也是块
            y = self.curY - self.curPiece.y(i) #以块的左下角为块中每个小块的坐标起点
            #print("drop", x, y, self.curPiece.shape())
            print("drop", self.curPiece.x(i), self.curPiece.y(i), self.curX, self.curY, self.curPiece.shape())
            self.setShapeAt(x, y, self.curPiece.shape())

        self.removeFullLines()

        if not self.isWaitingAfterLine: #没有要等待下落的行
            self.newPiece()


    def removeFullLines(self): #从下往上删除完整行
        '''removes all full lines from the board'''

        numFullLines = 0
        rowsToRemove = []

        for i in range(Board.BoardHeight): #遍历要删除的行

            n = 0
            for j in range(Board.BoardWidth):
                if not self.shapeAt(j, i) == Tetrominoe.NoShape:
                    n = n + 1

            if n == 10:
                rowsToRemove.append(i)

        rowsToRemove.reverse() #翻转一下, 从下往上删除完整行


        for m in rowsToRemove: #从上往下移动覆盖删除的行

            for k in range(m, Board.BoardHeight):
                for l in range(Board.BoardWidth):
                        self.setShapeAt(l, k, self.shapeAt(l, k + 1))

        numFullLines = numFullLines + len(rowsToRemove)

        if numFullLines > 0: #要覆盖的行如上已经向下覆盖, 则将当前块位置设置为无形状

            self.numLinesRemoved = self.numLinesRemoved + numFullLines
            self.msg2Statusbar.emit(str(self.numLinesRemoved))

            self.isWaitingAfterLine = True
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.update()


    def newPiece(self): #新创建一个块,并尝试移动至目标位置, 以块为单位, 块在面板中的位置
        '''creates a new shape'''

        self.curPiece = Shape()
        self.curPiece.setRandomShape()
        self.curX = Board.BoardWidth // 2 + 1 #以块为单位, 块在面板中的位置
        self.curY = Board.BoardHeight - 1 + self.curPiece.minY() #以块为单位, 块在面板中的位置
        print("newPiece", self.curX, self.curY)
        if not self.tryMove(self.curPiece, self.curX, self.curY):

            self.curPiece.setShape(Tetrominoe.NoShape)
            self.timer.stop()
            self.isStarted = False
            self.msg2Statusbar.emit("Game over")



    def tryMove(self, newPiece, newX, newY): #以块为单位, 移动到在面板中的块位置
        '''tries to move a shape'''

        for i in range(4):

            x = newX + newPiece.x(i)
            y = newY - newPiece.y(i)

            if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
                return False

            if self.shapeAt(x, y) != Tetrominoe.NoShape:
                return False

        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.update()

        return True


    def drawSquare(self, painter, x, y, shape): #根据坐标和形状 选择相应验收  绘制方块
        '''draws a square of a shape'''

        colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                      0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

        color = QColor(colorTable[shape])
        painter.fillRect(x + 1, y + 1, self.squareWidth() - 2,
            self.squareHeight() - 2, color)
'''
        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.squareHeight() - 1, x, y) #x 横坐标不变, 由下往上画线
        painter.drawLine(x, y, x + self.squareWidth() - 1, y)  #y 纵坐标不变, 由左向右画线

        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.squareHeight() - 1,   #y+h-1 纵坐标不变, 由左向右画线
            x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        painter.drawLine(x + self.squareWidth() - 1,           #x+h-1 横坐标不变, 由下往上画线
            y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)
'''

class Tetrominoe(object):

    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7


class Shape(object):

    coordsTable = ( #坐标
        ((0, 0),     (0, 0),     (0, 0),     (0, 0)), #0
        ((0, -1),    (0, 0),     (-1, 0),    (-1, 1)),#1 
        ((0, -1),    (0, 0),     (1, 0),     (1, 1)), #2
        ((0, -1),    (0, 0),     (0, 1),     (0, 2)), #3
        ((-1, 0),    (0, 0),     (1, 0),     (0, 1)), #4
        ((0, 0),     (1, 0),     (0, 1),     (1, 1)), #5
        ((-1, -1),   (0, -1),    (0, 0),     (0, 1)), #6
        ((1, -1),    (0, -1),    (0, 0),     (0, 1))  #7
    )

    def __init__(self):

        self.coords = [[0,0] for i in range(4)]
        self.pieceShape = Tetrominoe.NoShape

        self.setShape(Tetrominoe.NoShape)


    def shape(self): #返回当前形状
        '''returns shape'''

        return self.pieceShape


    def setShape(self, shape): #根据入参匹配相应的元组
        '''sets a shape'''

        table = Shape.coordsTable[shape]
        print("shape", shape, "table", table)
        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self.pieceShape = shape


    def setRandomShape(self):
        '''chooses a random shape'''

        self.setShape(random.randint(1, 7))


    def x(self, index): #返回元组第 index 个的横坐标
        '''returns x coordinate'''

        return self.coords[index][0]


    def y(self, index): #返回元组第 index 个的纵坐标
        '''returns y coordinate'''

        return self.coords[index][1]


    def setX(self, index, x): #重置元组第 index 个的横坐标
        '''sets x coordinate'''

        self.coords[index][0] = x


    def setY(self, index, y): #重置元组第 index 个的纵坐标
        '''sets y coordinate'''

        self.coords[index][1] = y


    def minX(self): #返回横坐标的最小值
        '''returns min x value'''

        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])

        return m


    def maxX(self):
        '''returns max x value'''

        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])

        return m


    def minY(self): #返回纵坐标的最小值
        '''returns min y value'''

        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])

        return m


    def maxY(self):
        '''returns max y value'''

        m = self.coords[0][1]
        for i in range(4):
            m = max(m, self.coords[i][1])

        return m


    def rotateLeft(self): #向左旋转
        '''rotates shape to the left'''

        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):

            result.setX(i, self.y(i))
            result.setY(i, -self.x(i))

        return result


    def rotateRight(self): #向右旋转
        '''rotates shape to the right'''

        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):

            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))

        return result


if __name__ == '__main__':

    app = QApplication([])
    tetris = Tetris()
    sys.exit(app.exec_())