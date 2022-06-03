import copy
import math
import numpy as np
from sklearn.linear_model import LinearRegression
from collections import deque


queue_size = 2

# Correlation coefficient required for zoom to be performed
coeff_thresh = 0.93


# Expressed in terms of hand lengths
bs_total = 0.5
bs_each = 0.2

#tolerable missing data points
missing_data_tolerance = 3

#sensitivity coefficients
zoom_sensitivity = 10




## print queue
def printQ(my_queue):
    q = copy.deepcopy(q)
    while len(q) > 0:
        print(q.pop())


## Two dimensional euclidean distance calculation
def euclid2Dimension(a, b):
    return math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)

## perform linear regression on set of points of hand
## fixed length zoom window
def zoom(my_queue):
    q = copy.deepcopy(my_queue)
    if(len(q) != q.maxlen):
        return None
    xs = list()
    ys = list()
    last = [[0, 0],[0, 0]]
    first = [[0, 0],[0, 0]]
    while(len(q) != 0):
        points = q.pop()
        #The earliest starting position of the hands is
        if(len(points) == 2):
            first = points
        # Since the queue has the latest elements at the right side, 
        # the first item popped (with datapoints from both hands)
        # will be the final position of the hands for the possible zoom
        if(len(points) == 2 and np.array_equal(last, [[0, 0],[0, 0]])):
            last = points
        for samp in points:
            xs.append([samp[0]])
            ys.append([samp[1]])
    # check if sufficient number of samples due to model losing hands
    # since len(xs) will always be equal to len(ys), we only need to check one
    if(len(xs) < q.maxlen*2 - missing_data_tolerance):
        return None
    #calculate euclidean distance between final points of hands
    dist1 = euclid2Dimension(last[0], first[0]) 
    dist2 = euclid2Dimension(last[1], first[1])
    #re-format array such that 
    X = np.array(xs)
    Y = np.array(ys)
    line_fit = LinearRegression().fit(X, Y)
    if(line_fit.score(X, Y) >= coeff_thresh and (dist1 + dist2) > bs_total and dist1 > bs_each and dist2 > bs_each):
        print("zoom detected")
        print("correlation:" + str(line_fit.score(X, Y)))
        print("distance: " + str(dist1 + dist2))
        print("first_L:" + str(first[0]) + "last_L" + str(last[0]))
        print("first_R:" + str(first[1]) + "last_R" + str(last[1]))
        if(euclid2Dimension(last[0], last[1]) > euclid2Dimension(first[0], first[1])):
            return (dist1 + dist2)/zoom_sensitivity
        else:
            return -((dist1 + dist2)/zoom_sensitivity)
    else:
        return None
## return linreg 
def grabLinReg(my_queue):
    xs = list()
    ys = list()
    q = copy.deepcopy(my_queue)
    while(len(q) != 0):
        points = q.pop()
        for samp in points:
            xs.append([samp[0]])
            ys.append([samp[1]])
    X = np.array(xs)
    Y = np.array(ys)
    line_fit = LinearRegression().fit(X, Y)
    return line_fit.score(X, Y)
 
    
