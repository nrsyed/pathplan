#############################################################################
# Name: grassfire.py
# Description: Implements and animates the grassfire path-finding algorithm.
# Author: Najam Syed
# Date: 2016-10-26
#############################################################################

import math
import numpy as np
import matplotlib.pyplot as plt
import random
import time

PI = math.pi

# Grid dimensions.
M = 30
N = 30

# Initializes dispGrid to white.
dispGrid = np.ones((M, N, 3), dtype=np.float)
fig = plt.figure()
gridMap = plt.imshow(dispGrid, interpolation='nearest', origin='lower',
    extent=[0, N, 0, M])
ax = gridMap._axes

# Set appropriate gridlines.
ax.set_xticks(np.arange(0, N+1, 1))
ax.set_yticks(np.arange(0, M+1, 1))
ax.grid(visible=True, ls='solid', color='k', lw=1.5)
ax.invert_yaxis()

# Set default colors for start cell, destination cell, empty unvisited cells,
# empty visited cells, and obstacle cells.
unvisitedColor = np.array([1, 1, 1])
visitedColor = np.array([0, 0, 1])
startColor = np.array([0, .75, 0])
destColor = np.array([0.75, 0, 0])
obstColor = np.array([0, 0, 0])
pathColor = np.array([1, 1, 0])

# Initialize the grid by randomly choosing a start cell, destination
# cell, and obstacle cells. Designate the start cell with 0, destination
# cell with -1, "empty" cells with -2, and obstacle cells with -3.
def initializeGrid():
    obstacleProb = 0.4  # Probability (0 <= p <= 1) of a given cell being an obstacle.
    pathGrid = -2 * np.ones((M, N), dtype=np.int)
    startCellIndex = random.randint(0, M * N - 1)
    destCellIndex = startCellIndex  # Guarantees while loop executes at least once.
    while destCellIndex == startCellIndex:
        destCellIndex = random.randint(0, M * N - 1)

    (firstIndices, secondIndices) = np.unravel_index([startCellIndex, destCellIndex], (M, N))
    pathGrid[firstIndices[0], secondIndices[0]] = 0
    pathGrid[firstIndices[1], secondIndices[1]] = -1

    # Randomly choose obstacle cells based on obstacleProb. Note that we take
    # advantage of short-circuiting in Python with the random float generator.
    for i in range(M):
        for j in range(N):
            if (pathGrid[i][j] < -1) and (random.uniform(0, 1) <= obstacleProb):
                pathGrid[i][j] = -3

    return pathGrid

def updateDispGrid():
    startIndices = np.where(pathGrid == 0)
    destIndices = np.where(pathGrid == -1)
    unvisitedIndices = np.where(pathGrid == -2)
    visitedIndices = np.where(pathGrid > 0)
    obstIndices = np.where(pathGrid == -3)
    pathIndices = np.where(pathGrid == -4)

    dispGrid[startIndices[0], startIndices[1], :] = startColor
    dispGrid[destIndices[0], destIndices[1], :] = destColor
    dispGrid[unvisitedIndices[0], unvisitedIndices[1], :] = unvisitedColor
    dispGrid[visitedIndices[0], visitedIndices[1], :] = visitedColor
    dispGrid[obstIndices[0], obstIndices[1], :] = obstColor
    dispGrid[pathIndices[0], pathIndices[1], :] = pathColor

    gridMap.set_data(dispGrid)
    fig.canvas.draw()

pathGrid = initializeGrid()
updateDispGrid()
plt.ion()
#mng = plt.get_current_fig_manager()
#mng.resize(*mng.window.maxsize())
plt.show()

def getCellInfo(rowToCheck, colToCheck):
    # Return value of -5 indicates invalid cell.
    if (rowToCheck < 0) or (rowToCheck >= M) or (colToCheck < 0) or (colToCheck >= N): return -5
    else: return pathGrid[rowToCheck, colToCheck]

def modifyAdjacent(row, col):
    global destFound
    adjacentVisitable = False
    for i in range(4):
        # Note how we use sin and cos to check surrounding cells!
        rowToCheck = row + int(math.sin((PI/2) * i))
        colToCheck = col + int(math.cos((PI/2) * i))
        adjacentCellValue = getCellInfo(rowToCheck, colToCheck)

        if adjacentCellValue == -1:
            # If checked cell is destination, stop and return.
            destFound = True
            return False
        elif adjacentCellValue == -2:
            pathGrid[rowToCheck][colToCheck] = currentDepth + 1
            adjacentVisitable = True
    return adjacentVisitable

def backtrack():
    global currentDepth
    destIndices = np.where(pathGrid == -1)
    currentRow = destIndices[0]
    currentCol = destIndices[1]

    while currentDepth > 0:
        #print(currentDepth)
        for i in range(4):
            rowToCheck = currentRow + int(math.sin((PI/2) * i))
            colToCheck = currentCol + int(math.cos((PI/2) * i))
            if getCellInfo(rowToCheck, colToCheck) == currentDepth:
                pathGrid[rowToCheck, colToCheck] = -4
                currentDepth -= 1
                currentRow = rowToCheck
                currentCol = colToCheck
                break
        updateDispGrid()

destFound = False
currentDepth = 0

def findPath():
    global currentDepth, destFound
    currentDepth = 0
    destFound = False
    cellsExhausted = False  # False if there remain visitable cells, else True

    iteration = 0
    while (destFound == False and cellsExhausted == False):
        cellsExhausted = True
        for i in range(M):
            for j in range(N):
                if pathGrid[i][j] == currentDepth and modifyAdjacent(i, j):
                    cellsExhausted = False
                if destFound: break
            if destFound: break
        updateDispGrid()
        if destFound:
            break
        else:
            currentDepth += 1
        time.sleep(0.25)

    updateDispGrid()
    if destFound:
        print("Path found in {:d} iterations.".format(currentDepth))
        backtrack()
    else: print("No path found.")
    waitforkey()

def waitforkey():
    try:
        input()
    except:
        pass

findPath()
