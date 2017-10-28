#############################################################################
# Name: bestfirst.py
# Description: Implements and animates a best-first path-finding algorithm.
#   This algorithm will NOT necessarily find the shortest path, but if at
#   least one path to the destination exists, it is guaranteed to find it.
# Author: Najam Syed
# Date: 2016-10-27
#############################################################################

import math
import numpy as np
import matplotlib.pyplot as plt
import random
import time

saveFigs = 1
PI = math.pi

# Grid dimensions.
M = 35
N = 35

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
startCellIndices = [0, 0]
destCellIndices = [0, 0]
def initializeGrid():
    global startCellIndices, destCellIndices
    obstacleProb = 0.35  # Probability (0 <= p <= 1) of a given cell being an obstacle.
    pathGrid = -2 * np.ones((M, N), dtype=np.int)
    startCellIndex = random.randint(0, M * N - 1)
    destCellIndex = startCellIndex  # Guarantees while loop executes at least once.
    while destCellIndex == startCellIndex:
        destCellIndex = random.randint(0, M * N - 1)

    (firstIndices, secondIndices) = np.unravel_index([startCellIndex, destCellIndex], (M, N))
    startCellIndices = [firstIndices[0], secondIndices[0]]
    destCellIndices = [firstIndices[1], secondIndices[1]]

    pathGrid[startCellIndices[0], startCellIndices[1]] = 0 
    pathGrid[destCellIndices[0], destCellIndices[1]] = -1

    # Randomly choose obstacle cells based on obstacleProb. Note that we take
    # advantage of short-circuiting in Python with the random float generator.
    for i in range(M):
        for j in range(N):
            if (pathGrid[i][j] < -1) and (random.uniform(0, 1) <= obstacleProb):
                pathGrid[i][j] = -3

    return pathGrid

figNum = 0
def updateDispGrid():
    global figNum
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
    if saveFigs:
        plt.savefig("./img/" + str(figNum) + ".png")
        figNum += 1

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

def moveAdjacent(row, col):
    global destFound, startCellIndices, destCellIndices, M, N, pathGrid, currentDepth
    adjacentVisitable = False
    pathGrid[row, col] = currentDepth

    distances = list()
    for i in range(4):
        rowToCheck = row + int(math.sin((PI/2) * i))
        colToCheck = col + int(math.cos((PI/2) * i))
        adjacentCellValue = getCellInfo(rowToCheck, colToCheck)

        if adjacentCellValue == -1:
            destFound = True
            return True
        elif adjacentCellValue == -2:
            # If adjacent visitable, store its distance from destination in
            # distances list.
            distances.append([math.sqrt((destCellIndices[0] - rowToCheck)**2 + 
                (destCellIndices[1] - colToCheck)**2), i])
            adjacentVisitable = True

    if adjacentVisitable:
        updateDispGrid()
        # Sort and iterate through distance list in order of increasing distance.
        distances = sorted(distances, key=lambda x: x[0])
        for distanceElement in distances:
            rowToVisit = row + int(math.sin((PI/2) * distanceElement[1]))
            colToVisit = col + int(math.cos((PI/2) * distanceElement[1]))
            currentDepth += 1
            if moveAdjacent(rowToVisit, colToVisit):
                return True
            else:
                currentDepth -= 1

    return False

# If the destination has been found, find the shortest path among the visited
# cells from the start cell to the destination cell by renumbering the
# visited cells with the shortest path (akin to the grassfire algorithm).
# NOTE: This is NOT guaranteed to find the shortest overall path, only the
# shortest path amongst the visited cells!
def findShortest():
    print("Finding shortest.")
    global currentDepth, startCellIndices
    currentDepth = 0
    pathToDestFound = False

    while ~pathToDestFound:
        currentDepthIndices = np.where(pathGrid == currentDepth)
        for i in range(len(currentDepthIndices[0])):
            currentRow = currentDepthIndices[0][i]
            currentCol = currentDepthIndices[1][i]
            for j in range(4):
                rowToCheck = currentRow + int(math.sin((PI/2) * j))
                colToCheck = currentCol + int(math.cos((PI/2) * j))
                if getCellInfo(rowToCheck, colToCheck) > currentDepth:
                    pathGrid[rowToCheck, colToCheck] = currentDepth + 1
                elif getCellInfo(rowToCheck, colToCheck) == -1:
                    pathToDestFound = True
                    break
        if pathToDestFound:
            break
        else:
            currentDepth += 1

def backtrack():
    global currentDepth
    destIndices = np.where(pathGrid == -1)
    currentRow = destIndices[0]
    currentCol = destIndices[1]

    while currentDepth > 0:
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
    global currentDepth, destFound, startCellIndices, destCellIndices
    currentDepth = 0
    destFound = False
    cellsExhausted = False  # False if there remain visitable cells, else True

    iteration = 0
    moveAdjacent(startCellIndices[0], startCellIndices[1])

    updateDispGrid()
    if destFound:
        print("Path found in {:d} iterations.".format(currentDepth))
        findShortest()
        backtrack()
    else: print("No path found.")
    waitforkey()

def waitforkey():
    try:
        input()
    except:
        pass

findPath()
