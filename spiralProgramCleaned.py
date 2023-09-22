# This program takes the idea of the 2-dimensional Ulam Sprial and 
# converts it to 3 dimensions.  I've searched for interesting 
# features in the resulting structure but haven't found any.  
# Generate the points with this program and the plot with the other.  
# Because it is impossible to traverse a 3x3x3 cube by moving distances
# of 1 after starting at the origin (this can be understood by counting 
# the number of points 0, 1, 2, and 3 spots from the origin); and noting
# that each move will be between a point an even number of units away 
# from the origin and an odd number of units from the origin) we must fill
# successive cubes of even size.  This algorithm fills points within
# the xy-plane by spiraling in a 2D fashion before moving in the z
# direction.  It  spirals clockwise for even values of z and
# counterclockwise for odd values of z, and fills numbers 
# from the inner cube outwards, so when the cube size increases,
# we end up filling the top or bottom planes, then progressively
# filling shells around the smaller cube in successive values of z,
# before spiraling back inwards at the other z boundary to complete 
# the current cube.

# Each new cube of even size begins by moving clockwise, and ends on 
# the opposite side (z-wise) by completing the inner shell in a 
# counterclockwise rotation.

import pickle
import numpy as np

# myList will store the tuples of coordinates of the numbers
myList = []

# store current values of x, y, z
curX = 0
curY = 0
curZ = 0

# iterMax which iteration to go up to.
# numbers go up to (2*(iterMax-1))^3 
# for iterMax = 3, creates up to 4x4x4
# for iterMax = 4, cretes up to 6x6x6
# for iterMax = 5, creates up to 8x8x8
# for itermax = 31, creates up to 60x60x60
iterMax = 16
oldN = -1

# choose a filename for the output
fileNameOutput = "myList" + str((2*(iterMax-1))**3) + ".p"

# maxIterations counts not only valid placements of a number
# but also counts times when the inner loop runs but doesn't 
# place a number, which can happen when the direction changes.
# This variable is used when you need to prevent infinite looping 
# in case the cube never completes (this should not occur if the 
# code isn't changed).  If the iteration counter i exceeds this 
# value both the inner and outer loops will exit.
maxIterations = 100000000
i = 0

# gridSize: create a grid in which to store the values created by the spiral
# occupationStatus is zero if the grid at that point is unoccupied, and 1 if
# it is occupied.  occupationStatusNums is the number occupying that grid point.
# curDxn is the current direction in which we wish to fill the next number.
# However, this direction can change based on the current occupancy of the grid. 
gridSize = 2*(iterMax+1)+1
occupationStatus = np.zeros((gridSize, gridSize, gridSize))
occupationStatusNums = np.zeros((gridSize, gridSize, gridSize))
curDxn = (1, 0, 0)

# these 3x3 matrices are used to change the current direction in which we are
# filling the grid, within the x-y plane
counterClockwiseRotationMatrix = np.matrix([[0, -1, 0], [1, 0, 0], [0, 0, 0]])
clockwiseRotationMatrix = np.matrix([[0, 1, 0], [-1, 0, 0], [0, 0, 0]])

# current Z direction should always either be 1 for up or -1 for down
# lastNMax is set to 2 which is the first value at which n reaches a max
# in X or Y
curZDxn = 1
lastNMaxXY = 2

# The filling algorithm stays within the same 2D square at same value of z 
# if possible
current2DSquareComplete = False



# Define an initialPoint in which we place the number 1,
# then initialize n, which will be the counter for points.
# #I.e. if we have a 4x4x4 cube, n will go up to 64
initialPoint = (gridSize//2, gridSize//2+1, gridSize//2, 1)
currentPoint = initialPoint[:]
n = 2

# Keep track of the bounds of the numbers placed within the grid
curXMin = initialPoint[0]
curYMin = initialPoint[1]
curZMin = initialPoint[2]
curXMax = initialPoint[0]
curYMax = initialPoint[1]
curZMax = initialPoint[2]

# myList keeps track of where each number is placed within the grid
# and is the ultimate deliverable
myList.append(initialPoint[:])
occupationStatus[gridSize//2, gridSize//2+1, gridSize//2] = 1
occupationStatusNums[gridSize//2, gridSize//2+1, gridSize//2] = 1


# Keep track of whether we've just completed a cube.  If we have, then we can go out
# start filling points on the grid outside of the current cube boundary.  resetDxn
# is used to reset the direction to clockwise at the start of each new cube.  
justCompletedCube = False
resetDxn = True

# Define both corners and perimeter XY-coords of each "square shell" within each plane
# These are populated when we call defineTheCorners and defineThePerims
theCorners = []
thePerims = []


# Finds the unique elements in a list
def unique(inputList):

    # intilize a null list
    unique_list = []

    # traverse for all elements
    for x in inputList:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


# Changes the current direction within the xy-plane.  If the current 
# point has an even value of Z, we change the direction by moving 
# clockwise; if z is odd then we change the direction by moving 
# counterclockwise.  This strategy ends up 'mirroring' actions more often
def changeDxnInPlane(currentPointInput, curDxnInput):
    curDxnVector = np.matrix(
        [[curDxnInput[0]], [curDxnInput[1]], [curDxnInput[2]]])

    if(currentPointInput[2] % 2 == 1):
        newDxnVector = clockwiseRotationMatrix * curDxnVector
        return tuple([newDxnVector[0, 0], newDxnVector[1, 0], newDxnVector[2, 0]])
    else:
        newDxnVector = counterClockwiseRotationMatrix * curDxnVector
        return tuple([newDxnVector[0, 0], newDxnVector[1, 0], newDxnVector[2, 0]])

# Determines if the current point lies at a higher or lower value of z than 
# the previous boundaries
def isNewZBoundary(currentPointInput):
    if(currentPointInput[2] > curZMax or currentPointInput[2] < curZMin):
        return True
    else:
        return False

# Determines if the grid is already occupied at that point using occupationStatus
def isOccupied(wouldBeNextPointInput):
    return occupationStatus[wouldBeNextPointInput[0]][wouldBeNextPointInput[1]][wouldBeNextPointInput[2]] != 0

# Determines whether the proposed next number placed lies within the current cube boundaries
def isInCurrentCube(wouldBeNextPointInput):
    if(wouldBeNextPointInput[0] < curXMin):
        if((initialPoint[0] - wouldBeNextPointInput[0]) > curCubeSide/2 or (curXMax - wouldBeNextPointInput[0]) >= curCubeSide):
            return False
        else:
            return True
    elif(wouldBeNextPointInput[0] > curXMax):
        if((wouldBeNextPointInput[0]-initialPoint[0]) > curCubeSide/2 or (wouldBeNextPointInput[0]-curXMin) >= curCubeSide):
            return False
        else:
            return True
    elif(wouldBeNextPointInput[1] < curYMin):
        if((initialPoint[1] - wouldBeNextPointInput[1]) > curCubeSide/2 or (curYMax - wouldBeNextPointInput[1]) >= curCubeSide):
            return False
        else:
            return True
    elif(wouldBeNextPointInput[1] > curYMax):
        if((wouldBeNextPointInput[1] - initialPoint[1]) > curCubeSide/2 or (wouldBeNextPointInput[1] - curYMin) >= curCubeSide):
            return False
        else:
            return True

    elif(wouldBeNextPointInput[2] < curZMin):
        if((wouldBeNextPointInput[2] - initialPoint[2]) > curCubeSide/2 or (curZMax - wouldBeNextPointInput[2]) >= curCubeSide):
            return False
        else:
            return True

    elif(wouldBeNextPointInput[2] > curZMax):
        if((initialPoint[2]-wouldBeNextPointInput[2]) > curCubeSide/2 or (wouldBeNextPointInput[2] - curZMin) >= curCubeSide):
            return False
        else:
            return True

    return True


# Checks whether sum of occupancies within plane is greater than currentCubeSideInput**2
def isCurrent2DSquareComplete(currentZInput, currentCubeSideInput):
    currentSumInPlaneVec = np.sum(occupationStatus, axis=(0, 1))
    currentSumInPlane = currentSumInPlaneVec[initialPoint[2]+currentZInput]
    if currentSumInPlane >= currentCubeSideInput**2:
        return True
    else:
        return False


# Updates the current boundaries if applicable based on the next point
def updateCurrentMinMax(nextPointInput):
    global curXMin, curXMax, curYMin, curYMax, lastNMaxXY

    if nextPointInput[0] < curXMin:
        curXMin = nextPointInput[0]
        lastNMaxXY = n
    if nextPointInput[0] > curXMax:
        curXMax = nextPointInput[0]
        lastNMaxXY = n
    if nextPointInput[1] < curYMin:
        curYMin = nextPointInput[1]
        lastNMaxXY = n
    if nextPointInput[1] > curYMax:
        curYMax = nextPointInput[1]
        lastNMaxXY = n


# Determines whether the proposed next point lies within the 2D shell
# that the current point lies in.  The shell is the outer square of the
# current XY plane.
def isInCurrent2DShell(wouldBeNextPointInput, currentPointInput):
    wouldBeXY = wouldBeNextPointInput[0:2]
    currentXY = currentPointInput[0:2]

    theShell = whichShell(currentXY)
    if(wouldBeXY in thePerims[theShell]):
        return True
    else:
        return False

# Determines whether the current 2D shell has been completely filled
def isCurrent2DShellComplete(curZInput, curCubeSideInput, currentPointInput):
    currentXY = currentPointInput[0:2]

    theShell = whichShell(currentXY)
    if(currentXY in thePerims[theShell]):
        isShellComplete = True
        for sq in thePerims[theShell]:
            if(occupationStatus[sq[0], sq[1], currentPointInput[2]] == 0):
                isShellComplete = False
    return isShellComplete


# Determines if the occupancy of the current shell is one, i.e. if the current
# shell has just been filled with its first value.
def isOccupancyShellOne(wouldBeNextPointInput):
    zInput = wouldBeNextPointInput[2]
    theOcc = 0
    theShell = whichShell(wouldBeNextPointInput[0:2])

    for sq in thePerims[theShell]:
        if(occupationStatus[sq[0], sq[1], zInput] == 1):
            theOcc = theOcc + 1
    if (theOcc == 1):
        return True
    else:
        return False

# Determines which shell the proposed point would fall into.  Shell zero 
# is the innermost 2x2 square
def whichShell(wouldBeXYInput):
    n = 0
    while n < iterMax:
        if wouldBeXYInput in thePerims[n]:
            return n
        n = n+1

# Determines whether we are spiraling outwards towards a corner, or inwards
def isTowardGeneralCorner(wouldBeNextPointInput, currentPointInput):
    currentXY = currentPointInput[0:2]
    shellNo = whichShell(currentXY)

    leastDistance = gridSize
    curDistance = 0

    for corner in theCorners[shellNo]:
        curDistance = (abs(corner[1]-wouldBeNextPointInput[1]) +
                       abs(corner[0]-wouldBeNextPointInput[0]))
        if(curDistance < leastDistance):
            leastDistance = curDistance

    if leastDistance > shellNo-1:
        return False
    else:
        return True

# Computes the XY values of the corners of the each shell of each cube
# theCorners[0] stores the corner XY values of the initial 2x2 square
# and theCorners[1] stores the corner XY values of the 4x4 square
def defineTheCorners(cubeSideInput):
    initialXY = initialPoint[0:2]

    for i in range(1, cubeSideInput+1):
        theCorners.append([])
        theCorners[i-1].append(
            (initialXY[0]-(i-1), initialXY[1]+i-1))
        theCorners[i-1].append(
            (initialXY[0]-(i-1), initialXY[1]-i))
        theCorners[i-1].append(
            (initialXY[0]+(i), initialXY[1]-i))
        theCorners[i-1].append(
            (initialXY[0]+(i), initialXY[1]+i-1))


# Computes which XY values on the grid will define the perimeter each 
# shell of the cube
def defineThePerims(cubeSideInput):
    initialXY = initialPoint[0:2]

    for i in range(1, cubeSideInput+1):
        thePerims.append([])
        # choose two opposing corners and create all points between them
        for j in range(0, 4):
            currentCorner = theCorners[i-1][j]
            if(j == 0 or j == 2):
                continue
            if(j == 1):
                for k in range(0, (2*(i-1)+2)):
                    thePerims[i -
                              1].append((currentCorner[0]+k, currentCorner[1]))
                    thePerims[i-1].append((currentCorner[0],
                                           currentCorner[1]+k))
            if(j == 3):
                for k in range(0, (2*(i-1)+2)):
                    thePerims[i -
                              1].append((currentCorner[0]-k, currentCorner[1]))
                    thePerims[i-1].append((currentCorner[0],
                                           currentCorner[1]-k))

        thePerims[i-1] = unique(thePerims[i-1])


# Populate the values of the corners and perimeters lists, which store only XY values
defineTheCorners(iterMax)
defineThePerims(iterMax)


print("Number of iterations will be greater than size of cube.  Size of cube is:", (2*(iterMax-1))**3)

# currentCubeSideMultiplier is half the current cube side
for curCubeSideMultiplier in range(1, iterMax):

    # If we've just completed a cube, we reset the direction to clockwise.
    if (n > 2):
        justCompletedCube = True
        resetDxn = True
        curDxn = (1, 0, 0)

    # Only want to flip Z direction at most once per new cube formed
    hasFlippedZ = False
    curCubeSide = 2*(curCubeSideMultiplier)
    curSquareArea = curCubeSide**2

    if(i > maxIterations):
        break

    while(n <= curCubeSide ** 3):
        passedInner = False

        if(n==oldN):
            passedInner = True
        oldN = n

        i = i + 1
        if(i > maxIterations):
            break

        if (i % 1000 == 0):
            print("Iteration is", i, "n is", n)

        # If current 2D square is complete, or if the last cube was just completed, move in Z
        if (isCurrent2DSquareComplete(curZ, curCubeSide) or (justCompletedCube and isCurrent2DSquareComplete(curZ, curCubeSide-2))):
            justCompletedCube = False
            resetDxn = False

            # if we've just completed a square and are at the Z boundary, then 
            # move once more and place a point before flipping the z direction
            if(isNewZBoundary(currentPoint) and not(hasFlippedZ)):

                
                curPointList = list(currentPoint[0:2])
                curPointList.append(currentPoint[2]+curZDxn)
                curPointList.append(n)
                wouldBeNextPoint = tuple(curPointList)

                currentPoint = wouldBeNextPoint[:]
                occupationStatus[currentPoint[0],
                                 currentPoint[1], currentPoint[2]] = 1
                occupationStatusNums[currentPoint[0],
                                     currentPoint[1], currentPoint[2]] = n
                updateCurrentMinMax(currentPoint)

                curZ = curZ + curZDxn
                myList.append(currentPoint[:])
                n = n + 1

                # change Z direction
                curZDxn = curZDxn * -1
                hasFlippedZ = True

                continue
            else:
                # move In Z
                curPointList = list(currentPoint[0:2])
                curPointList.append(currentPoint[2]+curZDxn)
                curPointList.append(n)
                wouldBeNextPoint = tuple(curPointList)

                currentPoint = wouldBeNextPoint[:]
                occupationStatus[currentPoint[0],
                                 currentPoint[1], currentPoint[2]] = 1
                occupationStatusNums[currentPoint[0],
                                     currentPoint[1], currentPoint[2]] = n
                updateCurrentMinMax(currentPoint)
                curZ = curZ + curZDxn
                myList.append(currentPoint[:])
                n = n + 1
                continue

        # If current 2D square is incomplete, move in the xy-plane
        else:
            resetDxn = False
            justCompletedCube = False
            wouldBeNextPoint = tuple(
                map(lambda i, j: i + j, currentPoint[0:3], curDxn))

            # There are five conditions that will make the direction rotate in the XY plane, not place a point, then continue.
            # 1) If would be next point is occupied
            # 2) If the would be next point is not in the current cube
            # 3) If the would be next point isn't in the current shell and the current shell isn't complete
            # 4) If we're looking to place the second point in a non-inner shell, and the current direction isn't towards a general corner 
            # (if we don't do this, we'll drift and eventually get stuck and won't be able to place points)
            # 5) If we're filling an inner shell, but not one in a newly-expanded cube (i.e. we didn't just reset the direction)
            if((isOccupied(wouldBeNextPoint)) or (not isInCurrentCube(wouldBeNextPoint)) or ((not isInCurrent2DShell(wouldBeNextPoint, currentPoint)) and (not isCurrent2DShellComplete(curZ, curCubeSide, currentPoint))) or (isOccupancyShellOne(currentPoint) and not isTowardGeneralCorner(wouldBeNextPoint, currentPoint) and whichShell(wouldBeNextPoint[0:2])>0) or (isOccupancyShellOne(currentPoint) and passedInner == False and resetDxn == True)):
                resetDxn = False
                curDxn = changeDxnInPlane(currentPoint, curDxn)[:]
                continue
            # If we didn't change directions, then just place the next point
            else:
                currentPoint = wouldBeNextPoint[:]
                occupationStatus[currentPoint[0],
                                 currentPoint[1], currentPoint[2]] = 1
                occupationStatusNums[currentPoint[0],
                                     currentPoint[1], currentPoint[2]] = n
                updateCurrentMinMax(currentPoint)

                currentPointNewList = list(currentPoint)
                currentPointNewList.append(n)
                currentPointNewTup = tuple(currentPointNewList)
                myList.append(currentPointNewTup)
                n = n + 1
                continue


print(myList)

pickle.dump(myList, open(fileNameOutput, "wb"))

