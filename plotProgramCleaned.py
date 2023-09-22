# This program is used to view the primes in the Ulam cube
# within a given plane with normal vector defined by a, b, and c
# Make sure that iterMax matches that which you used in the
# spiral program that generated it.  Also, change the pickled file 
# as necessary.

# All points can be plotted by setting a=b=c=0.  
# The only feature I've noticed is when a=1, b=0, c=0 
# and offsetX = {0, 1} the primes only occur where 
# abs(Y-y0)>abs(Z-z0).  However, this is due to the values 
# not satisfying this condition being multiples of a prime.
# Multiples of a single prime along a given vertical line of 
# constant Y; different primes are found at different Y values.
# Aside from that, certain <111> planes have no primes due to
# taking even values only.

from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from itertools import islice
from sympy import isprime
import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans
import pickle
import math

iterMax = 16
gridSize = 2*(iterMax+1)+1
x0 = gridSize//2
y0 = gridSize//2+1
z0 = gridSize//2

initialPoint = (x0, y0, z0)


myList = pickle.load(open("myList27000.p", "rb"))
myListZ0 = []
myNewList = []
myNewListPrime = []

# Equation of the plane is:
# a(x-x0)+b(y-y0)+c(z-z0) = 0
# REMEMBER: this implies the normal vector = (a, b, c)

a = 2
b = 0
c = 2

print("Relative points (setting the starting point to the origin):")
for ele in myList[0:100]:
    print((ele[0]-x0, ele[1]-y0, ele[2]-z0, ele[3]))


offsetX = 1
offsetY = 0
offsetZ = -1

def liesInPlane(inputPoint):
    if((a*(inputPoint[0]-x0-offsetX))+(b*(inputPoint[1]-y0-offsetY))+(c*(inputPoint[2]-z0-offsetZ)) == 0):
        return True
    else:
        return False


for j in range(len(myList)):
    # it is possble to run a loop over offsets here
    # at this level of indentation
        if(liesInPlane(myList[j])):
            myNewList.append(myList[j])

for tup in myNewList:
    if isprime(tup[3]):
        myNewListPrime.append(tup)


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for tup in myNewListPrime:
    ax.scatter(tup[0], tup[1], tup[2], c='b', marker='o')

ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

plt.show()
