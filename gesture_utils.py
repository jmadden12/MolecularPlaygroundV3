import copy
import math
import numpy as np
from sklearn.linear_model import LinearRegression
from collections import deque


queue_size = 7

#tolerable missing data points
missing_data_tolerance = 1

## ZOOM COEFFICIENTS

# Correlation coefficient required for zoom to be performed
coeff_thresh = 0.84


# Expressed in terms of hand lengths
bs_total = 0.7
bs_each = 0.3

#sensitivity coefficients
zoom_sensitivity = 8.6 # larger -> lower sensitivity


### TRANSLATION COEFFICIENTS

pair_thresh = 0.65

min_dist_thresh = 1

translation_sensitivity = 40 # larger -> higher sensitivity

num_allowed_deviations = 2



## print queue
def printQ(my_queue):
    q = copy.deepcopy(my_queue)
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
        '''
        print("zoom detected")
        print("correlation:" + str(line_fit.score(X, Y)))
        print("distance: " + str(dist1 + dist2))
        print("first_L:" + str(first[0]) + "last_L" + str(last[0]))
        print("first_R:" + str(first[1]) + "last_R" + str(last[1]))
        '''
        if(euclid2Dimension(last[0], last[1]) > euclid2Dimension(first[0], first[1])):
            return (dist1 + dist2)/zoom_sensitivity
        else:
            return -((dist1 + dist2)/zoom_sensitivity)
    else:
        return None
def translate(my_queue):
    q = copy.deepcopy(my_queue)
    if(len(q) != q.maxlen):
        return None
    first = q[0]
    last = q[-1]
    if(len(first) != 2 or len(last) != 2):
        print("FLFail")
        return None
    starting_distance = euclid2Dimension(first[0], first[1])
    print("Starting distance:" + str(starting_distance))
    missing_data = 0
    deviation_count = 0
    printQ(q)
    while(len(q) != 0):
        data = q.popleft()
        missing_data +=  2 - len(data)
        if(len(data) != 2):
            continue
        d_dist = euclid2Dimension(data[0], data[1])
        print("Data distance:" + str(d_dist))
        if(((d_dist >= (starting_distance - pair_thresh)) and (d_dist <= (starting_distance + pair_thresh))) == False):
            deviation_count += 1
    if(deviation_count > num_allowed_deviations):
        print("HMTFFail")
        return None
    if(missing_data > missing_data_tolerance):
        print("MDTFail")
        return None
    avg_dist_moved = (euclid2Dimension(first[0], last[0]) + euclid2Dimension(first[1], last[1]))/2
    print("Distance Moved" + str(avg_dist_moved))
    if(avg_dist_moved < min_dist_thresh):
        print("DNFEFail")
        return None
    x_t = (((last[0][0] - first[0][0]) + (last[1][0] - first[1][0]))/2) * translation_sensitivity
    y_t = (((last[0][1] - first[0][1]) + (last[1][1] - first[1][1]))/2) * translation_sensitivity
    return [-x_t, y_t]
    
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
 
    
