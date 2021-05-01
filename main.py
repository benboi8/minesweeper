import pygame as pg
from pygame import gfxdraw
import numpy as np
import random
import datetime as dt
import json

pg.init()

clock = pg.time.Clock()
fps = 60

sf = 2
width, height = 640 * sf, 360 * sf
screen = pg.display.set_mode((width, height))

black = (0, 0, 0)
white = (255, 255, 255)
red = (205, 0, 0)
green = (0, 205, 0)
blue = (0, 0, 205)
lightBlue = (0, 167, 205)
yellow = (205, 205, 0)
darkGreen = (60, 200, 60)
darkGray = (55, 55, 55)
lightGray = (205, 205, 205)

running = True
gameOver = False
gameWin = False
gameOverObjs = []
leaderboardObjs = []
settingsObjs = []
allSliders = []

difficulties = 2

boardColorPack = 0
gameColorPack = 0

saveFileName = "leaderboard.json"

def DrawRectOutline(surface, color, rect, width=1, outWards=False):
	x, y, w, h = rect
	width = max(width, 1)  # Draw at least one rect.
	width = min(min(width, w//2), h//2)  # Don't overdraw.

	# This draws several smaller outlines inside the first outline
	# Invert the direction if it should grow outwards.
	if outWards:
		for i in range(int(width)):
			pg.gfxdraw.rectangle(surface, (x-i, y-i, w+i*2, h+i*2), color)
	else:
		for i in range(int(width)):
			pg.gfxdraw.rectangle(surface, (x+i, y+i, w-i*2, h-i*2), color)


def DrawObround(surface, color, rect, filled=False, additive=True, vertical=False):
	if not vertical:
		x, y, w, h = rect
		radius = h // 2	
		# check if semicircles are added to the side or replace the side
		if not additive:
			x += radius
			w -= radius * 2
		# checks if it should be filled
		if not filled:
			pg.draw.aaline(surface, color, (x, y), (x + w, y), 3 * sf)
			pg.draw.aaline(surface, color, (x, y + h), (x + w, y + h), 3 * sf)
			pg.gfxdraw.arc(surface, x, y + radius, radius, 90, -90, color)
			pg.gfxdraw.arc(surface, x + w, y + radius, radius, -90, 90, color)
		else:
			pg.gfxdraw.filled_circle(surface, x, y + radius, radius, color)	
			pg.gfxdraw.filled_circle(surface, x + w, y + radius, radius, color)	
			pg.draw.rect(surface, color, (x, y, w, h))	
	else:
		x, y, w, h = rect
		radius = w // 2	
		# check if semicircles are added to the side or replace the side
		if not additive:
			y += radius
			h -= radius * 2
		# checks if it should be filled
		if not filled:
			pg.draw.aaline(surface, color, (x, y), (x, y + h), 3 * sf)
			pg.draw.aaline(surface, color, (x + w, y), (x + w, y + h), 3 * sf)
			pg.gfxdraw.arc(surface, x + radius, y, radius, 180, 360, color)
			pg.gfxdraw.arc(surface, x + radius, y + h, radius, 0, 180, color)
		else:
			pg.gfxdraw.filled_circle(surface, x + radius, y, radius, color)	
			pg.gfxdraw.filled_circle(surface, x + radius, y + h, radius, color)	
			pg.draw.rect(surface, color, (x, y, w, h))	


class Label:
	def __init__(self, surface, rect, colors, textData=["", "arial", 8, black, "none"], drawData=[False, False, True, True], lists=[]):
		self.surface = surface
		self.originalRect = pg.Rect(rect)
		self.borderColor = colors[0]
		self.backgroundColor = colors[1]

		self.text = textData[0]
		self.fontName = textData[1]
		self.fontSize = textData[2]
		self.textColor = textData[3]
		self.alignText = textData[4]

		self.roundedEdges = drawData[0]
		self.additive = drawData[1]
		self.filled = drawData[2]
		self.drawBorder = drawData[3]

		self.Rescale()

		for listToAppend in lists:
			listToAppend.append(self)

	def Rescale(self):
		self.rect = pg.Rect(self.originalRect.x * sf, self.originalRect.y * sf, self.originalRect.w * sf, self.originalRect.h * sf)
		self.font = pg.font.SysFont(self.fontName, self.fontSize * sf)
		self.textSurface = self.font.render(self.text, True, self.textColor)
		if self.alignText == "center-center":
			self.textRect = pg.Rect((self.rect.x + self.rect.w // 2) - self.textSurface.get_width() // 2, (self.rect.y + self.rect.h // 2) - self.textSurface.get_height() // 2, self.rect.w, self.rect.h)
		elif self.alignText == "top-center":
			self.textRect = pg.Rect((self.rect.x + self.rect.w // 2) - self.textSurface.get_width() // 2, self.rect.y + 2.5 * sf, self.rect.w, self.rect.h)
		else:
			self.textRect = pg.Rect(self.rect.x + 5 * sf, self.rect.y + 2.5 * sf, self.rect.w, self.rect.h)

	def Draw(self):
		if self.drawBorder:
			if self.roundedEdges:
				DrawObround(self.surface, self.backgroundColor, self.rect, self.filled, self.additive)
				DrawObround(self.surface, self.borderColor, (self.rect.x + 3 * sf, self.rect.y + 3 * sf, self.rect.w - 6 * sf, self.rect.h - 6 * sf), self.filled, self.additive)
			else:
				pg.draw.rect(self.surface, self.backgroundColor, self.rect)
				DrawRectOutline(self.surface, self.borderColor, self.rect, 1.5 * sf)
		self.surface.blit(self.textSurface, self.textRect)

	def UpdateText(self, textData):
		self.text = textData[0]
		self.fontName = textData[1]
		self.fontSize = textData[2]
		self.textColor = textData[3]
		self.alignText = textData[4]
		self.Rescale()


class HoldButton:
	def __init__(self, surface, rect, action, colorData, textData, drawData=[False, False], lists=[]):
		"""
		Parameters: 
			action: string of what the button does
			colorData: tuple of active color and inactive color
			textData: tuple of text, text color, font name, font size 
			lists: list of lists to add self too
		"""
		self.surface = surface
		self.originalRect = rect
		self.action = action
		self.active = False
		self.activeColor = colorData[0]
		self.inactiveColor = colorData[1]
		self.currentColor = self.inactiveColor
		self.text = textData[0]
		self.fontName = textData[1]
		self.fontSize = textData[2]

		self.filled = drawData[0]
		self.roundedEdges = drawData[0]

		for listToAppend in lists:
			listToAppend.append(self)
		
		self.Rescale()

	# rescale all elements
	def Rescale(self):
		self.rect = pg.Rect(self.originalRect[0] * sf, self.originalRect[1] * sf, self.originalRect[2] * sf, self.originalRect[3] * sf)
		self.font = pg.font.SysFont(self.fontName, self.fontSize * sf)
		self.textSurface = self.font.render(self.text, True, self.currentColor)

	def Draw(self):
		if self.roundedEdges:
			DrawObround(self.surface, self.currentColor, self.rect, self.filled)
		else:
			if self.filled:
				pg.draw.rect(self.surface, self.currentColor, self.rect)
			else:
				DrawRectOutline(self.surface, self.currentColor, self.rect, 2 * sf)

		self.textSurface = self.font.render(self.text, True, self.currentColor)
		self.surface.blit(self.textSurface, ((self.rect.x + self.rect.w // 2) - self.textSurface.get_width() // 2, (self.rect.y + self.rect.h // 2) - self.textSurface.get_height() // 2, self.textSurface.get_width() // 2, self.textSurface.get_height() // 2))

	def HandleEvent(self, event):
		# check for left mouse down
		if event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1:
				if self.rect.collidepoint(pg.mouse.get_pos()):
					self.active = True

		# check for left mouse up
		if event.type == pg.MOUSEBUTTONUP:
			if event.button == 1:
				self.active = False
		
		# change color
		if self.active:
			self.currentColor = self.activeColor
		else:
			self.currentColor = self.inactiveColor
		
		if not self.rect.collidepoint(pg.mouse.get_pos()):
			self.active = False

	def UpdateText(self, text):
		self.text = text


class Board:
	def __init__(self, surface, rect, colors, textData, boardData, gameData):
		self.surface = surface
		self.originalRect = pg.Rect(rect)
		self.borderColor = colors[0]
		self.backgroundColor = colors[1]
		self.cellColor = colors[2]
		self.hoverCellColor = colors[3]
		self.flagColor = colors[4]
		self.hoverFlagColor = colors[5]
		self.hoverFlagCellColor = colors[6]
		self.mineColor = colors[7]

		self.text = textData[0]
		self.fontName = textData[1]
		self.fontSize = textData[2]
		self.textColor = textData[3]

		self.cellWidth, self.cellHeight = boardData[0], boardData[1]

		self.headerWidth, self.headerHeight = boardData[2], boardData[3]

		self.difficulty = gameData["difficulty"]
		self.numOfMines = gameData["numOfMines"] * (self.difficulty + 1)
		self.mines = []
		self.cellsNextToMines = []
		self.maxNumOFlags = self.numOfMines

		self.board = []
		self.boardHeader = []
		self.flags = []
		self.flagMode = False

		self.startTime = dt.datetime.utcnow()
		self.timeElapsed = dt.datetime.utcnow() - self.startTime
		self.hours = 0
		self.minutes = 0
		self.seconds = 0
		self.countTime = False

		self.saveData = {}
		for i in range(difficulties + 1):
			self.saveData[str(i)] = {"time": []}

		self.Rescale()
		self.CreateBoard()
		self.CreateBoardHeader()
		self.CreateMines()

	def Rescale(self):
		self.rect = pg.Rect(self.originalRect.x * sf, self.originalRect.y * sf, self.originalRect.w * sf, self.originalRect.h * sf)
		self.font = pg.font.SysFont(self.fontName, self.fontSize * sf)
		self.textSurface = self.font.render(self.text, True, self.textColor)
		self.cellWidth *= sf
		self.cellHeight *= sf
		self.headerWidth *= sf
		self.headerHeight *= sf

	def CreateBoard(self):
		board = []
		for x in range(self.rect.w):
			for y in range(self.rect.h):
				if x % self.cellWidth == 0:
					if y % self.cellHeight == 0:
						board.append((self.rect.x + x, self.rect.y + y))

		self.board = np.array(board)

	def CreateBoardHeader(self):
		boardHeader = []
		headerRect = pg.Rect((self.originalRect.x + self.originalRect.w // 2) - (self.headerWidth // sf) // 2, self.originalRect.y - self.headerHeight // sf, self.headerWidth // sf, self.headerHeight // sf)
		boardHeader.append(Label(self.surface, headerRect, (self.borderColor, self.backgroundColor), ["", "arial", 8, lightGray, "none"]))
		boardHeader.append(Label(self.surface, (headerRect.x, headerRect.y, headerRect.w, 20), (self.borderColor, self.backgroundColor), ["number of mines: {}".format(self.numOfMines), "arial", 8, lightGray, "none"], [False, False, True, False]))
		boardHeader.append(Label(self.surface, (headerRect.x + headerRect.w - 80, headerRect.y, headerRect.w, 20), (self.borderColor, self.backgroundColor), ["Flags avaliable: {}".format(self.maxNumOFlags - len(self.flags)), "arial", 8, lightGray, "none"], [False, False, True, False]))
		boardHeader.append(Label(self.surface, (headerRect.x + headerRect.w - 80, headerRect.y + 10, headerRect.w, 20), (self.borderColor, self.backgroundColor), ["Flags used: ", "arial", 8, lightGray, "none"], [False, False, True, False]))
		boardHeader.append(Label(self.surface, (headerRect.x + headerRect.w // 2 - 20, headerRect.y + 10, 20, 20), (self.borderColor, self.backgroundColor), ["00:00:00", "arial", 12, lightGray, "center-center"], [False, False, True, False]))
		boardHeader[-1].UpdateText(["00:00:00", "arial", 12, lightGray, "none"])
		self.boardHeader = np.array(boardHeader)

	def CreateMines(self):
		mines = []
		while len(mines) < min(max(self.numOfMines, 1), len(self.board)):
			pos = self.board[random.randint(0, len(self.board) - 1)]
			if (pos[0], pos[1]) not in mines:
				mines.append((pos[0], pos[1]))

		board = []
		for pos in self.board:
			board.append((pos[0], pos[1], self.cellWidth, self.cellHeight))

		cellsNextToMines = []
		for mine in mines:
			rect = pg.Rect(mine[0], mine[1], self.cellWidth, self.cellHeight)
			indexs = []
			for x in range(-1, 2):
				for y in range(-1, 2):
					comparisonRect = pg.Rect(rect.x + (self.cellWidth * x), rect.y + (self.cellHeight * y), self.rect.w, self.rect.h)

					if comparisonRect.collidelist(board) not in indexs:
						indexs.append(comparisonRect.collidelist(board))
						cellToAdd = board[comparisonRect.collidelist(board)]
						if comparisonRect.collidelist(board) != -1:
							if (cellToAdd[0], cellToAdd[1]) not in mines:
								cellsNextToMines.append(cellToAdd)

		self.mines = np.array(mines)
		cells = []
		for cell in cellsNextToMines:
			cells.append((cell[0], cell[1], cellsNextToMines.count(cell)))
		self.cellsNextToMines = np.array(cells)

	def Draw(self):
		self.UpdateBoardHeader()
		
		DrawRectOutline(self.surface, self.borderColor, self.rect, 4, True)

		for obj in self.boardHeader:
			obj.Draw()

		for pos in self.cellsNextToMines:
			self.textSurface = self.font.render(str(pos[2]), True, white)
			self.surface.blit(self.textSurface, (pos[0] + (self.cellWidth // 2) - self.textSurface.get_width() // 2, pos[1] + self.cellHeight // 2 - self.textSurface.get_height() // 2, self.cellWidth, self.cellHeight))

		for mine in self.mines:
			pg.draw.rect(self.surface, self.mineColor, (mine[0] + (self.cellWidth // 4), mine[1] + (self.cellHeight // 4), self.cellWidth // 2, self.cellHeight // 2))
	
		for pos in self.board:
			rect = pg.Rect(pos[0], pos[1], self.cellWidth, self.cellHeight)
			if rect.collidepoint(pg.mouse.get_pos()):
				if self.flagMode:
					pg.draw.rect(self.surface, self.hoverFlagCellColor, rect)
				else:
					pg.draw.rect(self.surface, self.hoverCellColor, rect)
			else:
				pg.draw.rect(self.surface, self.cellColor, rect)
			if (pos[0], pos[1]) in self.flags:
				if rect.collidepoint(pg.mouse.get_pos()):
					pg.draw.rect(self.surface, self.hoverFlagColor, rect)

			DrawRectOutline(self.surface, self.backgroundColor, rect)

		for flag in self.flags:
			rect = pg.Rect(flag[0] + self.cellWidth // 4, flag[1] + self.cellHeight // 4, self.cellWidth // 2, self.cellHeight // 2)
			pg.draw.rect(self.surface, self.flagColor, rect)
			DrawRectOutline(self.surface, self.backgroundColor, rect)

		if gameOver:
			for mine in self.mines:
				pg.draw.rect(self.surface, self.mineColor, (mine[0] + (self.cellWidth // 4), mine[1] + (self.cellHeight // 4), self.cellWidth // 2, self.cellHeight // 2))

	def CheckCellClick(self):
		cellCheck = False
		cell = None
		for pos in self.board:
			rect = pg.Rect(pos[0], pos[1], self.cellWidth, self.cellHeight)
			if rect.collidepoint(pg.mouse.get_pos()):
				cellCheck = True
				cell = pos
				break
			else:
				cellCheck = False

		return cellCheck, cell

	def PlaceFlag(self, cell):
		if (cell[0], cell[1]) in self.flags:
			self.flags.remove((cell[0], cell[1]))
		else:
			if len(self.flags) + 1 <= self.maxNumOFlags:
				self.flags.append((cell[0], cell[1]))

	def UncoverCell(self, cell):
		flags = []
		for flag in self.flags:
			flags.append((flag[0], flag[1]))
		
		board = []
		for pos in self.board:
			if (pos[0], pos[1]) != (cell[0], cell[1]):
				board.append((pos[0], pos[1]))

		if (cell[0], cell[1]) in flags and (cell[0], cell[1]) not in board:
			board.append((cell[0], cell[1]))
		else:
			self.board = np.array(board)
			self.CheckCellForMine(cell)
			if not gameOver:
				self.UncoverConnectedCells([(cell[0], cell[1])])

	def CheckCellForMine(self, cell):
		for mine in self.mines:
			if (mine[0], mine[1]) == (cell[0], cell[1]):
				self.countTime = False
				EndGame()

	def UncoverConnectedCells(self, visitedCells):
		board = []
		for pos in self.board:
			board.append((pos[0], pos[1], self.cellWidth, self.cellHeight))

		mines = []
		for mine in self.mines:
			mines.append((mine[0], mine[1]))

		cellsNextToMines = []
		for cell in self.cellsNextToMines:
			cellsNextToMines.append((cell[0], cell[1]))

		flags = []
		for flag in self.flags:
			flags.append((flag[0], flag[1]))

		for cell in visitedCells:
			rect = pg.Rect(cell[0], cell[1], self.cellWidth, self.cellHeight)
			for x in range(-1, 2):
				for y in range(-1, 2):
					comparisonRect = pg.Rect(rect.x + (self.cellWidth * x), rect.y + (self.cellHeight * y), rect.w, rect.h)
					
					if len(board) != 0:
						cellToRemove = board[comparisonRect.collidelist(board)]
						if comparisonRect.collidelist(board) != -1:
							if (cellToRemove[0], cellToRemove[1]) not in flags:
								if (cellToRemove[0], cellToRemove[1]) not in mines:
									if (cellToRemove[0], cellToRemove[1]) not in visitedCells:
										if (cellToRemove[0], cellToRemove[1]) not in cellsNextToMines:
											visitedCells.append((cellToRemove[0], cellToRemove[1]))
											board.remove((cellToRemove[0], cellToRemove[1], self.cellWidth, self.cellHeight))
										else:
											board.remove((cellToRemove[0], cellToRemove[1], self.cellWidth, self.cellHeight))


		self.board = np.array(board)

		if len(self.board) == len(self.mines):
			self.Win()

	def UpdateBoardHeader(self):
		numOfMines = self.boardHeader[1]
		avaliableFlags = self.boardHeader[2]
		flagsUsed = self.boardHeader[3]
		time = self.boardHeader[4]

		numOfMines.UpdateText(["Total number of mines: {}".format(len(self.mines)), "arial", 8, lightGray, "none"])
		avaliableFlags.UpdateText(["Flags avaliable: {}".format(self.maxNumOFlags - len(self.flags)), "arial", 8, lightGray, "none"])
		flagsUsed.UpdateText(["Flags used: {}".format(len(self.flags)), "arial", 8, lightGray, "none"])
		
		if self.countTime:
			self.timeElapsed = dt.datetime.utcnow() - self.startTime
			self.seconds = self.timeElapsed.seconds%60
			self.minutes = (self.timeElapsed.seconds//60)%60
			self.hours = self.timeElapsed.seconds//3600
			if len(str(self.hours)) < 2:
				hours = "0" + str(self.hours)
			else:
				hours = str(self.hours)
			if len(str(self.minutes)) < 2:
				minutes = "0" + str(self.minutes)
			else:
				minutes = str(self.minutes)
			if len(str(self.seconds)) < 2:
				seconds = "0" + str(self.seconds)
			else:
				seconds = str(self.seconds)
			time.UpdateText(["{hour}:{min}:{sec}".format(hour=hours, min=minutes, sec=seconds), "arial", 12, lightGray, "none"])

	def Win(self):
		global gameWin
		self.countTime = False
		gameWin = True
		try:
			with open(saveFileName, "x") as saveFile:
				saveFile.close()
			with open(saveFileName, "w") as saveFile:
				json.dump(self.saveData, fp=saveFile, indent=2)
				saveFile.close()
		except:
			pass

		with open(saveFileName, "r") as saveFile:
			saveFileData = json.load(saveFile)
			for difficulty in range(difficulties + 1):
				times = saveFileData[str(difficulty)]["time"]
				if self.difficulty == difficulty:
					times.append([self.hours, self.minutes, self.seconds])
				times.sort()
				self.saveData[str(difficulty)]["time"] = times
			saveFile.close()

		with open(saveFileName, "w") as saveFile:
			json.dump(self.saveData, fp=saveFile, indent=2)

	def ChangeDifficulty(self):
		if not gameWin and not gameOver and not self.countTime:
			if self.difficulty + 1 <= difficulties:
				self.difficulty += 1
			else:
				self.difficulty = 0

			self.numOfMines = gameData["numOfMines"] * (self.difficulty + 1)
			self.maxNumOFlags = self.numOfMines	
			self.CreateMines()
			self.UpdateBoardHeader()


	def HandleEvent(self, event):
		if event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1:

				cellCheck, cell = self.CheckCellClick()
				if cellCheck:
					if not self.countTime:
						self.countTime = True
						self.startTime = dt.datetime.utcnow()
					if self.flagMode:
						self.PlaceFlag(cell)
					else:
						self.UncoverCell(cell)

			if event.button == 3:

				cellCheck, cell = self.CheckCellClick()
				if cellCheck:
					if not self.countTime:
						self.countTime = True
						self.startTime = dt.datetime.utcnow()
					self.PlaceFlag(cell)

		if event.type == pg.KEYDOWN:
			if event.key == pg.K_f:
				self.flagMode = not self.flagMode


gameData = {
	"numOfMines": 20,
	"difficulty": 1
}


def CreateSettings():
	global settingsObjs
	settingsObjs = []
	HoldButton(screen, ((width // sf // 2) - 310, (height // sf // 2) - 165, 150, 20), "difficulty", (white, lightGray), ["Difficulty: regular", "arial", 8], lists=[settingsObjs])
	HoldButton(screen, ((width // sf // 2) - 310, (height // sf // 2) + 145, 150, 20), "restart", (white, lightGray), ["Restart", "arial", 8], lists=[settingsObjs])
	HoldButton(screen, ((width // sf // 2) - 310, (height // sf // 2) - 140, 150, 20), "boardColor", (white, lightGray), ["Board style: Blue", "arial", 8], lists=[settingsObjs])
	HoldButton(screen, ((width // sf // 2) - 310, (height // sf // 2) - 115, 150, 20), "gameColor", (white, lightGray), ["Game style: Normal", "arial", 8], lists=[settingsObjs])
	
	UpdateSettings()


def UpdateSettings():
	difficulty = board.difficulty
	difficulties = {
		"0": "Easy",
		"1": "Regular",
		"2": "Hard"
	}
	settingsObjs[0].UpdateText("Difficulty: {}".format(difficulties[str(difficulty)]))

	boardColors = {
		"0": "Blue",
		"1": "Red",
		"2": "Green",
	}
	settingsObjs[2].UpdateText("Board style: {}".format(boardColors[str(boardColorPack)]))
	
	gameColors = {
		"0": "Normal",
		"1": "Black and white",
		"2": "Inverted",
	}
	settingsObjs[3].UpdateText("Game style: {}".format(gameColors[str(gameColorPack)]))
	UpdateLeaderBoards()


def CreateLeaderBoards():
	global leaderboardObjs
	leaderboardObjs = []
	# time
	Label(screen, ((width // sf // 2) + 160, (height // sf // 2) - 165, 150, 330), (lightGray, darkGray), ["Best times.", "arial", 10, lightGray, "top-center"], lists=[leaderboardObjs])

	UpdateLeaderBoards()


def UpdateLeaderBoards():
	global leaderboardObjs
	difficulties = {
	"0": "easy",
	"1": "regular",
	"2": "hard"
	}
	difficulty = difficulties[str(board.difficulty)]

	time = leaderboardObjs[0]
	time.UpdateText(["Best times for {} difficulty.".format(difficulty), "arial", 10, lightGray, "top-center"])
	leaderboardObjs = [time]
	try:
		with open(saveFileName, "r") as saveFile:
			saveFileData = json.load(saveFile)
			times = saveFileData[str(board.difficulty)]["time"]
			for i in range(min(12, len(times))):
				hours = times[i][0]
				if len(str(hours)) < 2:
					hours = "0" + str(hours)
				minutes = times[i][1]
				if len(str(minutes)) < 2:
					minutes = "0" + str(minutes)
				seconds = times[i][2]
				if len(str(seconds)) < 2:
					seconds = "0" + str(seconds)
				time = "{}:{}:{}".format(hours, minutes, seconds)
				Label(screen, ((width // sf // 2) + 165, (height // sf // 2) - 165 + 25 * (i + 1), 140, 20), (lightGray, darkGray), [time, "arial", 12, lightGray, "center-center"], lists=[leaderboardObjs])
				saveFile.close()
	except:
		pass


def EndGame():
	global gameOver
	gameOver = True


def DrawLoop():
	global board
	screen.fill(darkGray)

	board.Draw()

	for obj in leaderboardObjs:
		obj.Draw()

	for obj in settingsObjs:
		obj.Draw()

	pg.display.update()


def Restart():
	global board, gameOver, gameWin
	gameOver = False
	gameWin = False
	try:
		gameData["difficulty"] = board.difficulty
	except:
		pass
	try:
		board.__del__()
	except:
		pass

	board = Board(screen, ((width // sf // 2) - 150, (height // sf // 2) - 135, 300, 300), (lightGray, darkGray, lightBlue, red, yellow, darkGreen, blue, red), ("", "arial", 8, black), (20, 20, 300, 30), gameData)


def ChangeColor():
	global darkGray, lightGray, lightBlue, red, white
	if boardColorPack == 0:
		lightBlue = (0, 167, 205)
		red = (205, 0, 0)
	elif boardColorPack == 1:
		lightBlue = (205, 0, 0)
		red = (0, 167, 205)
	elif boardColorPack == 2:
		lightBlue = (0, 205, 0)
		red = (205, 0, 0)

	if gameColorPack == 0:
		darkGray = (55, 55, 55)
		lightGray = (205, 205, 205)
		white = (255, 255, 255)
	elif gameColorPack == 1:
		darkGray = (0, 0, 0)
		lightGray = (255, 255, 255)
		white = (255, 255, 255)
	elif gameColorPack == 2:
		darkGray = (205, 205, 205)
		lightGray = (55, 55, 55)
		white = (0, 0, 0)

	Restart()
	CreateLeaderBoards()
	CreateSettings()


def ButtonPress():
	global boardColorPack, gameColorPack
	if settingsObjs[0].active:
		board.ChangeDifficulty()
		settingsObjs[0].active = False
	if settingsObjs[1].active:
		Restart()
		settingsObjs[1].active = False

	if gameOver or gameWin or not board.countTime:
		if settingsObjs[2].active:
			if boardColorPack + 1 <= 2:
				boardColorPack += 1
			else:
				boardColorPack = 0
			ChangeColor()
		if settingsObjs[3].active:
			if gameColorPack + 1 <= 2:
				gameColorPack += 1
			else:
				gameColorPack = 0
			ChangeColor()
	UpdateSettings()

ChangeColor()
while running:
	clock.tick(fps)

	for event in pg.event.get():
		if event.type == pg.QUIT:
			running = False
		if event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				running = False
			if event.key == pg.K_r:
				Restart()

		ButtonPress()

		for obj in settingsObjs:
			obj.HandleEvent(event)

		if not gameOver and not gameWin:
			board.HandleEvent(event)

	if gameWin:
		UpdateLeaderBoards()

	DrawLoop()
