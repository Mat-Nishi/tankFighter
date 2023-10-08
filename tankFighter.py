from tkinter.constants import S, W
from graphics import *
from math import sin, cos, radians, floor
from random import random, randrange
import time
import json
from sys import platform
import os
try:
    import winsound
except:
    pass


class Window(GraphWin):
    def __init__(self, title='myWindow', width=800, height=600, autoflush=True, bgColor='black'):
        super().__init__(title=title, width=width, height=height, autoflush=autoflush)
        self._height = height
        self._width = width
        self._bgColor = bgColor
        self.setBackground(self._bgColor)
        self.bind_all("<KeyPress>",   self._onKeyPress)
        self.bind_all("<KeyRelease>", self._onKeyRelease)
        self.keys = dict()

        if platform == "linux" or platform == "linux2":
            self._os = "linux"

        elif platform == "darwin":
            self._os = "mac"

        elif platform == "win32" or platform == "cygwin":
            self._os = "windows"

    def _onKeyPress(self, event):
        self.keys[event.keysym] = True

    def _onKeyRelease(self, event):
        self.keys[event.keysym] = False

    def playSound(self, soundFile):
        if self._os == 'windows':
            winsound.PlaySound(soundFile, winsound.SND_ASYNC)
        elif self._os == 'linux':
            os.system(f'aplay {soundFile}&')
        elif self._os == 'mac':
            os.system(f'afplay {soundFile}&')

    def clear(self):
        for item in self.items[:]:
            item.undraw()
        self.update()

class Player:
    def __init__(self, x, y, direction, window, id, cFile="stg.json", size=15):
        with open(cFile, 'r') as config:
            data = json.load(config)
        data = data[id]

        self._color = data["color"]
        self._upKey = data["upKey"]
        self._downKey = data["downKey"]
        self._leftKey = data["leftKey"]
        self._rightKey = data["rightKey"]
        self._shootKey = data["shootKey"]

        self._id = id
        self._win = window
        self._radius = size
        self._direction = direction
        self._x = x
        self._y = y
        self._body = Circle(Point(x,y), self._radius)
        self._cannon = Line(Point(x+(self._radius*Player.getSin(self)),y+(self._radius*Player.getCos(self)))
                        ,   Point(x+(self._radius*2*Player.getSin(self)),y+(self._radius*2*Player.getCos(self))))
        self._bullets = {}
        self._bulletId = 0
        self._lastShot = 0
        self._onCooldown = False
        #self.create()

    def updateSettings(self, cFile='stg.json'):
        with open(cFile, 'r') as config:
            data = json.load(config)
        data = data[self._id]

        self._color = data["color"]
        self._upKey = data["upKey"]
        self._downKey = data["downKey"]
        self._leftKey = data["leftKey"]
        self._rightKey = data["rightKey"]
        self._shootKey = data["shootKey"]

    def create(self):
        if self._win.isOpen():
            self._body.setFill(self._color)
            self._body.draw(self._win)
            self._cannon.setFill(self._color)
            self._cannon.setWidth(5)
            self._cannon.draw(self._win)
    
    def createCannon(self):
        if self._win.isOpen():
            self._cannon.setFill(self._color)
            self._cannon.setWidth(5)
            self._cannon.draw(self._win)

    def getCenterTuple(self):
        x = self._body.getCenter().getX()
        y = self._body.getCenter().getY()
        return x, y

    def getPos(self):
        x,y = self.getCenterTuple()
        return x, y, self._direction
    
    def getBullets(self):
        return self._bullets

    def getKey(self, key, value, file='stg.json'):
        with open(file, 'r') as sFile:
            data = json.load(sFile)

        if self._id == "p1":
            data["p1"][key] = value
        else:
            data["p2"][key] = value

        with open(file, 'w') as sFile:
            json.dump(data, sFile)

    def getColor(self, color, file='stg.json'):
        with open(file, 'r') as sFile:
            data = json.load(sFile)

        if self._id == "p1":
            data["p1"]["color"] = color
        else:
            data["p2"]["color"] = color

        with open(file, 'w') as sFile:
            json.dump(data, sFile)

    def setPosition(self, x, y):
        currentX, currentY = self.getCenterTuple()
        self._body.move(x-currentX, y-currentY)
        self._x = x
        self._y = y
        self.updateCannon()
    
    def updateCannon(self):
        x, y = self.getCenterTuple()
        self._cannon.undraw()
        self._cannon = Line(Point(x+(self._radius*Player.getSin(self)),y+(self._radius*Player.getCos(self)))
                        ,   Point(x+(self._radius*2*Player.getSin(self)),y+(self._radius*2*Player.getCos(self))))
        self.createCannon()

    def checkCooldown(self, cd=5):
        if time.time() - self._lastShot > cd:
            self._onCooldown = False

    def isOutOfBounds_y(self, direction):
        y = self.getCenterTuple()[1]

        if direction:

            if y-self._radius < 0 and Player.getCos(self) < 0:
                return 0

            elif y+self._radius > self._win._height and Player.getCos(self) > 0:
                return 0

            else: 
                return 1
        
        else:

            if y-self._radius < 0 and Player.getCos(self) > 0:
                return 0

            elif y+self._radius > self._win._height and Player.getCos(self) < 0:
                return 0

            else: 
                return 1

    def isOutOfBounds_x(self, direction):
        x = self.getCenterTuple()[0]

        if direction:

            if x-self._radius < 0 and Player.getSin(self) < 0:
                return 0

            elif x+self._radius > self._win._width and Player.getSin(self) > 0:
                return 0

            else: 
                return 1

        else:

            if x-self._radius < 0 and Player.getSin(self) > 0:
                return 0

            elif x+self._radius > self._win._width and Player.getSin(self) < 0:
                return 0

            else: 
                return 1


    def movement(self, step=4):
        x, y = self.getCenterTuple()

        if self._win.keys.get(self._upKey):
            self._body.move(step*Player.getSin(self)*self.isOutOfBounds_x(1), step*Player.getCos(self)*self.isOutOfBounds_y(1))
            
        if self._win.keys.get(self._downKey):
            self._body.move(-step*Player.getSin(self)*self.isOutOfBounds_x(0), -step*Player.getCos(self)*self.isOutOfBounds_y(0))

        if self._win.keys.get(self._rightKey):
            self._direction -= 5

        if self._win.keys.get(self._leftKey):
            self._direction += 5

        if self._win.keys.get(self._shootKey):
            if not self._onCooldown:
                self._onCooldown = True
                self._lastShot = time.time()
                self._bullets[self._bulletId] = Bullet(self, x+(self._radius*2*Player.getSin(self)), y+(self._radius*2*Player.getCos(self)), self._bulletId, self._win)
                self._bullets[self._bulletId].create()
                self._bulletId = (self._bulletId + 1) % 10

        for bullet in self._bullets:
            b = self._bullets[bullet]
            b.movement(5)

            if b._delete:
                b._body.undraw()

        self.updateCannon()
        self.checkCooldown(1)

    @staticmethod
    def getSin(self):
        return sin(radians(self._direction))

    @staticmethod
    def getCos(self):
        return cos(radians(self._direction))


class Bullet:
    def __init__(self, player, x, y, id, window, size=5, lt=8):
        self._win = window
        self._color = player._color
        self._size = size
        self._spawnTime = time.time()
        self._delete = False
        self._isActive = True
        self._id = id
        self._radius = size
        self._lastingTime = lt
        self._body = Circle(Point(x,y), self._radius)
        self._xSpeed = Player.getSin(player)
        self._ySpeed = Player.getCos(player)


    def create(self):
        if self._win.isOpen():
            self._body.setFill(self._color)
            self._body.draw(self._win)


    def getCenterTuple(self):
        x = self._body.getCenter().getX()
        y = self._body.getCenter().getY()
        return x, y

    def getPos(self):
        x,y = self.getCenterTuple()
        return x, y, self._xSpeed, self._ySpeed

    def getTimeLeft(self):
        return self._lastingTime - time.time() + self._spawnTime

    def changeParams(self, lt, xSpd, ySpd):
        self._lastingTime = lt
        self._xSpeed = xSpd
        self._ySpeed = ySpd

    def setPosition(self, x, y):
        currentX, currentY = self.getCenterTuple()
        self._body.move(x-currentX, y-currentY)

    def movement(self, step):
        x, y = self.getCenterTuple()
        self._body.move(step* self._xSpeed, step*self._ySpeed)

        if x > self._win._width:
            self.setPosition(0, y)

        elif x < 0:
            self.setPosition(self._win._width, y)

        if y > self._win._height:
            self.setPosition(x, 0)

        elif y < 0:
            self.setPosition(x, self._win._height)

        if time.time() - self._spawnTime > self._lastingTime:
            self._delete = True
            self._isActive = False

    def checkCollision(self, enemy):
        x1, y1 = self.getCenterTuple()
        x2, y2 = enemy.getCenterTuple()
        r1, r2 = self._radius, enemy._radius
        distance = (x1-x2)**2 + (y1-y2)**2
        tRadius = (r1+r2)**2

        if (distance <= tRadius) and self._isActive:
            self._delete = True
            self._isActive = False
            self._win.playSound('sfx/hit.wav')
            return True

        else:
            return False

class UI:
    def __init__(self, window, p1, p2, upKey='Up', downKey='Down', rightKey='Right', leftKey='Left', cFile='stg.json', p1Score=0, p2Score=0):
        self._win = window
        with open(cFile, 'r') as config:
            data = json.load(config)
        data = data["ui"]

        self._win._bgColor = data["bgColor"]
        self._hlColor = data["hlColor"]
        self._menuColor = data["menuColor"]
        self._font = data["font"]
        self._pauseKey = data["pauseKey"]
        self._confirmKey = data["confirmKey"]
        self._win.setBackground(self._win._bgColor)

        self._upKey = upKey
        self._downKey = downKey
        self._leftKey = leftKey
        self._rightKey = rightKey

        self._p1 = p1
        self._p2 = p2
        self._timeLeft = 120
        self._p1Score = p1Score
        self._p2Score = p2Score
        self._scoreBody = Text(Point(self._win._width/2, 30),
                               f'Player One: {p1Score}    Player Two: {p2Score}')
        #self.createScore()

    def createScore(self):
        if self._win.isOpen():
            if self._win._bgColor != 'white':
                self._scoreBody.setTextColor('white')
            else:
                self._scoreBody.setTextColor('black')
            self._scoreBody.setSize(16)
            self._scoreBody.setFace(self._font)
            self._scoreBody.draw(self._win)

    def updateScore(self):
        for bullet in self._p1._bullets:
            b = self._p1._bullets[bullet]
            if b.checkCollision(self._p2):
                self._p1Score += 1

        for bullet in self._p2._bullets:
            b = self._p2._bullets[bullet]
            if b.checkCollision(self._p1):
                self._p2Score += 1

        self._scoreBody.setText(f'Player One: {self._p1Score}    Player Two: {self._p2Score}\n{floor(self._timeLeft/60):02} : {self._timeLeft%60:02}')

        if self._timeLeft <= 0:
            if self._p1Score > self._p2Score:
                self.winScreen(1)
            elif self._p2Score > self._p1Score:
                self.winScreen(2)
            else:
                self.winScreen(0)
            self._timeLeft = 120

    def updateSettings(self, cFile='stg.json'):
        with open(cFile, 'r') as config:
            data = json.load(config)
        data = data["ui"]

        self._win._bgColor = data["bgColor"]
        self._hlColor = data["hlColor"]
        self._menuColor = data["menuColor"]
        self._font = data["font"]
        self._pauseKey = data["pauseKey"]
        self._confirmKey = data["confirmKey"]
        self._win.setBackground(self._win._bgColor)

    def getColor(self, obj, color, file='stg.json'):
        with open(file, 'r') as sFile:
            data = json.load(sFile)

        data["ui"][obj] = color

        with open(file, 'w') as sFile:
            json.dump(data, sFile)   

    def getKey(self, key, value, file='stg.json'):
        with open(file, 'r') as sFile:
            data = json.load(sFile)

            data["ui"][key] = value

        with open(file, 'w') as sFile:
            json.dump(data, sFile)   

    def getFont(self, font, file='stg.json'):
        with open(file, 'r') as sFile:
            data = json.load(sFile)

            data["ui"]["font"] = font

        with open(file, 'w') as sFile:
            json.dump(data, sFile)  

    def drawNewGame(self):
        self._win.clear()
        self._p1Score = 0
        self._p2Score = 0
        self._timer = time.time()
        self._timeLeft = 120
        self._p1 = Player(self._win._width/4, self._win._height/4, 0, self._win, "p1")
        self._p2 = Player(self._win._width - self._win._width/4, self._win._height - self._win._height/4, 180, self._win, "p2")
        self._p1.create()
        self._p2.create()
        self.createScore()

    def drawGame(self, file='sav.json'):
        self._win.clear()
        self._timer = time.time()

        try:
            with open(file, 'r') as sFile:
                data = json.load(sFile)

            p1 = data['p1']
            p2 = data['p2']
            p1b = data['p1b']
            p2b = data['p2b']
            self._timeLeft = data['timeLeft']
            
            self._p1 = Player(p1['x'], p1['y'], p1['d'], self._win, "p1")
            self._p2 = Player(p2['x'], p2['y'], p2['d'], self._win, "p2")

            for b in p1b:
                bullet = Bullet(self._p1, p1b[b]['x'], p1b[b]['y'], b, self._win)
                bullet.changeParams(p1b[b]["lt"], p1b[b]["xSpd"], p1b[b]["ySpd"])
                bullet.create()
                self._p1._bullets[b] = bullet

            for b in p2b:
                bullet = Bullet(self._p2, p2b[b]['x'], p2b[b]['y'], b, self._win)
                bullet.changeParams(p2b[b]["lt"], p2b[b]["xSpd"], p2b[b]["ySpd"])
                bullet.create()
                self._p2._bullets[b] = bullet

            self._p1._bulletId = len(p1b)
            self._p2._bulletId = len(p2b)
            self._p1.create()
            self._p2.create()
            self._p1Score = p1['score']
            self._p2Score = p2['score']
            self.createScore()

        except:
            pass

    def runGame(self):
        cTime = time.time()
        self._p1.movement()
        self._p2.movement()
        self.updateScore()

        if self._win.keys.get(self._pauseKey):
            self.pauseScreen()

        if cTime - self._timer >= 1:
            self._timer = cTime
            self._timeLeft -= 1

        self._win.update()
        time.sleep(0.01)

    def winScreen(self, winner):
        try:
            os.remove('sav.json')
        except:
            pass
        self._win.clear()
        self._win.playSound('sfx/win.wav')
        winText = Text(Point(self._win._width / 2, self._win._height / 2),
                       f'Player {winner} wins!!!\nPress "{self._confirmKey}" to continue.')
        winText.setFace(self._font)
        winText.setSize(16)
        if self._win._bgColor != 'white':
            winText.setTextColor('white')
        else:
            winText.setTextColor('black')
        winText.draw(self._win)

        if winner == 0:
            winText.setText(f'Its a draw!!!\nPress "{self._confirmKey}" to continue.')

        while not self._win.isClosed():
            if self._win.keys.get(self._confirmKey):
                self._win.keys[self._confirmKey] = False
                break
            self._win.update()

        self.menuScreen()

    def menuScreen(self, boxWidth=140, boxHeight=50):
        self._win.clear()
        action = 0
        gameName = Text(Point(self._win._width/2,
                              self._win._height/4), 'Tank Fighter')
        continueText = Text(Point(self._win._width/2,
                                  self._win._height/2 - boxHeight*3/4), 'Continue')
        continueBox = Rectangle(Point(self._win._width/2 - boxWidth/2, self._win._height/2 - boxHeight/4),
                                Point(self._win._width/2 + boxWidth/2, self._win._height/2 - boxHeight*5/4))
        newGameText = Text(Point(self._win._width/2,
                                 self._win._height/2 + boxHeight*3/4), 'New Game')
        newGameBox = Rectangle(Point(self._win._width/2 - boxWidth/2, self._win._height/2 + boxHeight/4),
                               Point(self._win._width/2 + boxWidth/2, self._win._height/2 + boxHeight*5/4))
        configText = Text(Point(self._win._width/2,
                                self._win._height/2 + boxHeight*9/4), 'Settings')
        configBox = Rectangle(Point(self._win._width/2 - boxWidth/2, self._win._height/2 + boxHeight*7/4),
                              Point(self._win._width/2 + boxWidth/2, self._win._height/2 + boxHeight*11/4))

        boxes = [continueBox, newGameBox, configBox]
        texts = [continueText, newGameText, configText, gameName]
        items = boxes + texts

        for box in boxes:
            box.setFill(self._menuColor)
        
        for text in texts:
            text.setFace(self._font)
            text.setSize(16)
            
        if self._win._bgColor != "white":
            gameName.setFill('white')
        else:
            gameName.setFill('black')

        if not os.path.isfile('sav.json'):
            if self._menuColor != "white":
                continueText.setFill('white')
            else:
                continueText.setFill('grey')

        for item in items:
            if self._win.isOpen():
                item.draw(self._win)

        while not self._win.isClosed():
            if self._win.keys.get(self._upKey):
                action -= 1
                action = abs(action % 3)
                self._win.keys[self._upKey] = False

            if self._win.keys.get(self._downKey):
                action += 1
                action = abs(action % 3)
                self._win.keys[self._downKey] = False

            for i in range(3):
                if i != action:
                    boxes[i].setFill(self._menuColor)
                else:
                    boxes[i].setFill(self._hlColor)

            if self._win.keys.get(self._confirmKey):
                self._win.keys[self._confirmKey] = False
                if action == 0 and not os.path.isfile('sav.json'):
                    pass

                else:
                    break

        for item in items:
            item.undraw()

        if action == 0:
            self.drawGame()
            
        elif action == 1:
            #self.modeSelection()
            self.drawNewGame()
        else:
            self.settingsScreen()

    def settingsScreen(self, boxWidth=140, boxHeight=50):
        self._win.clear()
        p1Box = Rectangle(Point(self._win._width/2 - boxWidth/2 - 5, self._win._height/8), 
                          Point(self._win._width/2 - boxWidth*3/2 - 5, self._win._height/8 + boxHeight))
        p2Box = Rectangle(Point(self._win._width/2 - boxWidth/2, self._win._height/8), 
                          Point(self._win._width/2 + boxWidth/2, self._win._height/8 + boxHeight))
        winBox = Rectangle(Point(self._win._width/2 + boxWidth/2 + 5, self._win._height/8), 
                          Point(self._win._width/2 + boxWidth*3/2 + 5, self._win._height/8 + boxHeight))
        
        p1Text = Text(Point(self._win._width/2 - boxWidth - 5, self._win._height/8 + boxHeight/2), 'Player 1')
        p2Text = Text(Point(self._win._width/2, self._win._height/8 + boxHeight/2), 'Player 2')
        winText = Text(Point(self._win._width/2 + boxWidth + 5, self._win._height/8 + boxHeight/2), 'Interface')
        
        box1 = Rectangle(Point(self._win._width/2 - boxWidth*3/2 - 5, self._win._height/8 + boxHeight + 5), 
                          Point(self._win._width/2 + boxWidth*3/2 + 5, self._win._height/8 + 2*boxHeight + 5))
        box2 = Rectangle(Point(self._win._width/2 - boxWidth*3/2 - 5, self._win._height/8 + 2*boxHeight + 10), 
                          Point(self._win._width/2 + boxWidth*3/2 + 5, self._win._height/8 + 3*boxHeight + 10))
        box3 = Rectangle(Point(self._win._width/2 - boxWidth*3/2 - 5, self._win._height/8 + 3*boxHeight + 15), 
                          Point(self._win._width/2 + boxWidth*3/2 + 5, self._win._height/8 + 4*boxHeight + 15))
        box4 = Rectangle(Point(self._win._width/2 - boxWidth*3/2 - 5, self._win._height/8 + 4* boxHeight + 20), 
                          Point(self._win._width/2 + boxWidth*3/2 + 5, self._win._height/8 + 5*boxHeight + 20))
        box5 = Rectangle(Point(self._win._width/2 - boxWidth*3/2 - 5, self._win._height/8 + 5*boxHeight + 25), 
                          Point(self._win._width/2 + boxWidth*3/2 + 5, self._win._height/8 + 6*boxHeight + 25))
        box6 = Rectangle(Point(self._win._width/2 - boxWidth*3/2 - 5, self._win._height/8 + 6*boxHeight + 30), 
                          Point(self._win._width/2 + boxWidth*3/2 + 5, self._win._height/8 + 7*boxHeight + 30))

        box1Text = Text(Point(self._win._width/2, self._win._height/8 + 3/2*boxHeight + 5), '')
        box2Text = Text(Point(self._win._width/2, self._win._height/8 + 5/2*boxHeight + 10), '')
        box3Text = Text(Point(self._win._width/2, self._win._height/8 + 7/2*boxHeight + 15), '')
        box4Text = Text(Point(self._win._width/2, self._win._height/8 + 9/2*boxHeight + 20), '')
        box5Text = Text(Point(self._win._width/2, self._win._height/8 + 11/2*boxHeight + 25), '')
        box6Text = Text(Point(self._win._width/2, self._win._height/8 + 13/2*boxHeight + 30), '')

        fbText = Text(Point(self._win._width/2, self._win._height/8 + 15/2*boxHeight + 50), 'Press "esc" to return to menu')
        
        boxes = [p1Box, p2Box, winBox, box1, box2, box3, box4, box5, box6]
        texts = [p1Text, p2Text, winText, box1Text, box2Text, box3Text, box4Text, box5Text, box6Text, fbText]
        items = boxes + texts

        for box in boxes:
            box.setFill(self._menuColor)

        for text in texts:
            text.setFace(self._font)
            text.setSize(16)
        
        if self._win._bgColor != 'white':
            fbText.setFill('white')
        else:
            fbText.setFill('black')

        for item in items:
            if self._win.isOpen():
                item.draw(self._win)

        action1 = 0
        action2 = 0

        vBoxes = [box1, box2, box3, box4, box5, box6]
        wBoxes = [p1Box, p2Box, winBox]
        keys = ["upKey", "leftKey", "downKey", "rightKey", "shootKey"]
        arrows = ["up", "down", "left", "right"]
        colors = ["black", "grey", "red", "orange", "yellow", "green", "blue", "purple", "pink", "white"]
        fonts = ["helvetica", "courier", "times roman", "arial"]

        while not self._win.isClosed():
            if self._win.keys.get(self._leftKey):
                action1 -= 1
                action1 = abs(action1 % 3)
                self._win.keys[self._leftKey] = False
                action2 = 0
                fbText.setText('Press "esc" to return to menu')

            if self._win.keys.get(self._rightKey):
                action1 += 1
                action1 = abs(action1 % 3)
                self._win.keys[self._rightKey] = False
                action2 = 0
                fbText.setText('Press "esc" to return to menu')

            if self._win.keys.get(self._upKey):
                action2 -= 1
                action2 = abs(action2 % 6)
                self._win.keys[self._upKey] = False
                fbText.setText('Press "esc" to return to menu')

            if self._win.keys.get(self._downKey):
                action2 += 1
                action2 = abs(action2 % 6)
                self._win.keys[self._downKey] = False
                fbText.setText('Press "esc" to return to menu')

            for i in range(6):
                    if i != action2:
                        vBoxes[i].setFill(self._menuColor)
                    else:
                        vBoxes[i].setFill(self._hlColor)
            
            for i in range(3):
                    if i != action1:
                        wBoxes[i].setFill(self._menuColor)
                    else:
                        wBoxes[i].setFill(self._hlColor)

            if action1 == 2:
                box1Text.setText('Bg Color')
                box2Text.setText('Menu Color')
                box3Text.setText('Highlight')
                box4Text.setText('Font')
                box5Text.setText('Pause Key')
                box6Text.setText('Confirm Key')
            else:
                box1Text.setText('Up Key')
                box2Text.setText('Left Key')
                box3Text.setText('Down Key')
                box4Text.setText('Right Key')
                box5Text.setText('Shoot Key')
                box6Text.setText('Color')

            if self._win.keys.get(self._confirmKey):
                self._win.keys[self._confirmKey] = False
                aux = (action1, action2)

                if action1 == 0 or action1 == 1:

                    if action2 <= 4:
                        fbText.setText('Press the key you want to bind')

                        time.sleep(0.2)
                        from keyboard import read_key
                        val = read_key()
                        if val in arrows:
                            val = val.capitalize()
                        elif val == "esc":
                            val = "Escape"
                        elif val == "enter":
                            val = "Return"
                        if action1 == 0:
                            self._p1.getKey(keys[action2], val)
                        else:
                            self._p2.getKey(keys[action2], val)

                        fbText.setText(f'"{val}" is now binded')

                        for key in self._win.keys:
                            self._win.keys[key] = False

                    else:
                        action3 = 0
                        fbText.setText('<Choose the color with the arrows>')
                        colorText = Text(Point(self._win._width/2, self._win._height/8 + 15/2*boxHeight + 75),"")
                        colorText.setFace(self._font)
                        colorText.setSize(16)
                        colorText.draw(self._win)

                        while self._win.isOpen():
                            if self._win.keys.get(self._leftKey):
                                action3 -= 1
                                action3 = abs(action3 % len(colors))
                                colorText.setText(f'{colors[action3]}')
                                colorText.setFill(colors[action3])
                                self._win.keys[self._leftKey] = False

                            if self._win.keys.get(self._rightKey):
                                action3 += 1
                                action3 = abs(action3 % len(colors))
                                colorText.setText(f'{colors[action3]}')
                                colorText.setFill(colors[action3])
                                self._win.keys[self._rightKey] = False
                            
                            if self._win._bgColor == colors[action3]:
                                colorText.setFill(colors[abs((action3 + 1) % len(colors))])

                            if self._win.keys.get(self._confirmKey):
                                fbText.setText(f'You selected "{colors[action3]}"')
                                colorText.undraw()
                                if action1 == 0:
                                    self._p1.getColor(colors[action3])
                                else:
                                    self._p2.getColor(colors[action3])
                                break

                            self._win.update()

                else:

                    if action2 <= 2:

                        action3 = 0
                        fbText.setText('<Choose the color with the arrows>')
                        colorText = Text(Point(self._win._width/2, self._win._height/8 + 15/2*boxHeight + 75),"")
                        colorText.setFace(self._font)
                        colorText.setSize(16)
                        colorText.draw(self._win)

                        while self._win.isOpen():
                            if self._win.keys.get(self._leftKey):
                                action3 -= 1
                                action3 = abs(action3 % len(colors))
                                colorText.setText(f'{colors[action3]}')
                                colorText.setFill(colors[action3])
                                self._win.keys[self._leftKey] = False

                            if self._win.keys.get(self._rightKey):
                                action3 += 1
                                action3 = abs(action3 % len(colors))
                                colorText.setText(f'{colors[action3]}')
                                colorText.setFill(colors[action3])
                                self._win.keys[self._rightKey] = False
                            
                            if self._win._bgColor == colors[action3]:
                                colorText.setFill(colors[abs((action3 + 1) % len(colors))])

                            if self._win.keys.get(self._confirmKey):
                                fbText.setText(f'You selected "{colors[action3]}"')
                                if action2 == 0:
                                    self.getColor("bgColor", colors[action3])
                                elif action2 == 1:
                                    if action3 != 0:
                                        self.getColor("menuColor", colors[action3])
                                    else:
                                        fbText.setText("Menu color can't be black\nplease choose a diferent color")
                                else:
                                    self.getColor("hlColor", colors[action3])

                                colorText.undraw()
                                break

                            self._win.update()

                    elif action2 == 3:

                        action3 = 0
                        fbText.setText(f'<Choose the font with the arrows>\nCurrently showing "{fonts[action3]}"')
                        fbText.setFace(fonts[action3])

                        while self._win.isOpen():
                            if self._win.keys.get(self._leftKey):
                                action3 -= 1
                                action3 = abs(action3 % len(fonts))
                                fbText.setText(f'<Choose the font with the arrows>\nCurrently showing "{fonts[action3]}"')
                                fbText.setFace(fonts[action3])
                                self._win.keys[self._leftKey] = False

                            if self._win.keys.get(self._rightKey):
                                action3 += 1
                                action3 = abs(action3 % len(fonts))
                                fbText.setText(f'<Choose the font with the arrows>\nCurrently showing "{fonts[action3]}"')
                                fbText.setFace(fonts[action3])
                                self._win.keys[self._rightKey] = False

                            if self._win.keys.get(self._confirmKey):
                                fbText.setText(f'You selected "{fonts[action3]}"')    
                                self.getFont(fonts[action3])
                                break

                            self._win.update()
                    else:
                        fbText.setText('Press the key you want to bind')
                        time.sleep(0.2)
                        from keyboard import read_key
                        val = read_key()

                        if val in arrows:
                            val = val.capitalize()
                        elif val == "esc":
                            val = "Escape"
                        elif val == "enter":
                            val = "Return"
                        if action2 == 4:
                            self.getKey("pauseKey", val)
                        else:
                            self.getKey("confirmKey", val)

                        fbText.setText(f'"{val}" is now binded')

                        for key in self._win.keys:
                            self._win.keys[key] = False

                time.sleep(0.2)
                action1, action2 = aux
                
            if self._win.keys.get("Escape"):
                self._win.keys["Escape"] = False
                break

            self._win.update()
            time.sleep(0.01)
        
        self._p1.updateSettings()
        self._p2.updateSettings()
        self.updateSettings()
        self.menuScreen()
        

    def pauseScreen(self, boxWidth=140, boxHeight=50):
        self.saveState()
        self._win.clear()
        time.sleep(0.1)
        action = 0
        pauseText = Text(Point(self._win._width/2,
                               self._win._height/4), 'Game paused')
        resumeText = Text(Point(self._win._width/2,
                                self._win._height/2 - boxHeight*3/4), 'Resume')
        resumeBox = Rectangle(Point(self._win._width/2 - boxWidth/2, self._win._height/2 - boxHeight/4),
                              Point(self._win._width/2 + boxWidth/2, self._win._height/2 - boxHeight*5/4))
        menuText = Text(Point(self._win._width/2,
                              self._win._height/2 + boxHeight*3/4), 'Menu')
        menuBox = Rectangle(Point(self._win._width/2 - boxWidth/2, self._win._height/2 + boxHeight/4),
                            Point(self._win._width/2 + boxWidth/2, self._win._height/2 + boxHeight*5/4))

        boxes = [resumeBox, menuBox]
        texts = [pauseText, menuText, resumeText]
        items = boxes + texts

        for box in boxes:
            box.setFill(self._menuColor)

        for text in texts:
            text.setFace(self._font)
            text.setSize(16)

        pauseText.setTextColor('white')

        for item in items:
            if self._win.isOpen():
                item.draw(self._win)

        while not self._win.isClosed():
            if self._win.keys.get(self._upKey):
                action -= 1
                action = abs(action % 2)
                self._win.keys[self._upKey] = False

            if self._win.keys.get(self._downKey):
                action += 1
                action = abs(action % 2)
                self._win.keys[self._downKey] = False

            for i in range(2):
                if i != action:
                    boxes[i].setFill(self._menuColor)
                else:
                    boxes[i].setFill(self._hlColor)

            if self._win.keys.get(self._confirmKey):
                self._win.keys[self._confirmKey] = False
                break

            if self._win.keys.get(self._pauseKey):
                action = 0
                self._win.keys[self._pauseKey] = False
                break

        for item in items:
            item.undraw()

        if action == 1:
            self.menuScreen()

        else:
            self.drawGame()
    
    
    def saveState(self):
        p1x, p1y, p1d = self._p1.getPos()
        p2x, p2y, p2d = self._p2.getPos()
        p1bb = self._p1.getBullets()
        p2bb = self._p2.getBullets()
        p1b, p2b = {}, {}

        p1 = {'x': p1x,
              'y': p1y,
              'd': p1d,
              'score' : self._p1Score}

        p2 = {'x': p2x,
              'y': p2y,
              'd': p2d,
              'score': self._p2Score}

        for bullet in p1bb:
            if p1bb[bullet]._isActive:
                x, y, xSpd, ySpd = p1bb[bullet].getPos()
                lt = p1bb[bullet].getTimeLeft()
                p1b[bullet] = {'x': x,
                               'y': y,
                               'xSpd': xSpd,
                               'ySpd': ySpd,
                               'lt': lt}

        for bullet in p2bb:
            if p2bb[bullet]._isActive:
                x, y, xSpd, ySpd = p2bb[bullet].getPos()
                lt = p2bb[bullet].getTimeLeft()
                p2b[bullet] = {'x': x,
                               'y': y,
                               'xSpd': xSpd,
                               'ySpd': ySpd,
                               'lt': lt}

        saveFile = {'p1': p1,
                    'p2': p2,
                    'p1b': p1b,
                    'p2b': p2b,
                    'timeLeft': self._timeLeft
                    }
        
        with open('sav.json', 'w') as sFile:
            json.dump(saveFile, sFile)


def main():
    height, width = 600, 880
    win = Window("tankFighter", width, height)
    p1 = Player(width/4, height/4, 0, win, "p1")
    p2 = Player(width - width/4, height - height/4, 180, win, "p2")
    ui = UI(win, p1, p2)
    ui.menuScreen()
    st = time.time()
    while not win.isClosed():
        ui.runGame()
    try:
        if ui._timeLeft < 120:
            ui.saveState()
    except:
        pass


if __name__ == '__main__':
    main()


    
        