import copy
import math
from statistics import variance
import numpy as np
from sklearn.linear_model import LinearRegression
from collections import deque


queue_size = 7

queue_size_translate = 7

queue_size_zoom = 12

#tolerable missing data points
missing_data_tolerance = 3

## ZOOM COEFFICIENTS

# Correlation coefficient required for zoom to be performed
coeff_thresh = 0.87

per_coeff_thresh = 0.95

#sensitivity coefficients
zoom_sensitivity = 30 # larger -> lower sensitivity


### TRANSLATION COEFFICIENTS



min_dist_thresh_x = 1

min_dist_thresh_y = 0.37

translation_sensitivity = 25 # larger -> higher sensitivity

num_allowed_deviations = 2

rotate_sensitivity = 25



## print queue
def printQ(my_queue):
    q = copy.deepcopy(my_queue)
    while len(q) > 0:
        print(q.pop())

def printQDesmos(my_queue):
    q = copy.deepcopy(my_queue)
    while len(q) > 0:
        samp = q.popleft()
        for x in samp:
            print("(" + str(x[0]) + ", " + str(x[1]) + ")")

def boundingBoxVariance(my_queue):
    toConvertNd = list()
    q = copy.deepcopy(my_queue)
    count = 0
    sum = 0
    while len(q) > 0:
        samp = q.popleft()
        for x in samp:
            toConvertNd.append(x)
            sum += x
            count += 1
    if(len(toConvertNd) == 0):
        return None
    average = sum/count
    if(average == 0):
        return None
    numpyCorrected = np.array(toConvertNd)
    variance = np.var(numpyCorrected)
    return (variance)/(average)

def queueAverage(my_queue):
    q = copy.deepcopy(my_queue)
    count = 0
    sum = 0
    while len(q) > 0:
        sum += q.pop()
        count += 1
    if count == 0:
        return None
    return ((sum)/count)
    


## Two dimensional euclidean distance calculation
def euclid2Dimension(a, b):
    return math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)

## perform linear regression on set of points of hand
## fixed length zoom window
def zoom(my_queue, hand0_travel, hand1_travel, hands_i, hands_f):
    xs = list()
    ys = list()
    each = [[[],[]],[[],[]]]
    for points in my_queue:
        i = 0
        for samp in points:
            if(i == 2):
                break
            each[i][0].append([samp[0]])
            each[i][1].append([samp[1]])
            xs.append([samp[0]])
            ys.append([samp[1]])
            i += 1
    
    # check if sufficient number of samples due to model losing hands
    # since len(xs) will always be equal to len(ys), we only need to check one
    if(len(xs) < my_queue.maxlen*2 - missing_data_tolerance):
        return None
    #re-format array such that 
    X = np.array(xs)
    Y = np.array(ys)

    X_0 = np.array(each[0][0])
    Y_0 = np.array(each[0][1])
    X_1 = np.array(each[1][0])
    Y_1 = np.array(each[1][1])

    line_fit = LinearRegression().fit(X, Y)
    line_fit_zero = LinearRegression().fit(X_0, Y_0)
    line_fit_one = LinearRegression().fit(X_1, Y_1)
    if(line_fit.score(X, Y) >= coeff_thresh):
        print("zoom detected")
        print("0 score" + str(line_fit_zero.score(X_0, Y_0)))
        print("1 score" + str(line_fit_one.score(X_1, Y_1)))
        if(hands_f > hands_i):
            return (hand0_travel + hand1_travel)/zoom_sensitivity
        else:
            return -((hand0_travel+ hand1_travel)/zoom_sensitivity)
    else:
        return None

def translate(my_queue):
    x_t = (((my_queue[-1][0][0] - my_queue[0][0][0]) + (my_queue[-1][1][0] - my_queue[0][1][0]))/2) * translation_sensitivity
    y_t = (((my_queue[-1][0][1] - my_queue[0][0][1]) + (my_queue[-1][1][1] - my_queue[0][1][1]))/2) * translation_sensitivity
    return [-x_t, y_t]

def rotate(my_queue):
    x_t = (((my_queue[-1][0][0] - my_queue[0][0][0]))/2) * rotate_sensitivity
    y_t = (((my_queue[-1][0][1] - my_queue[0][0][1]))/2) * rotate_sensitivity
    return [-x_t, y_t]

## return linreg 
def grabLinReg(my_queue):
    xs = list()
    ys = list()
    q = copy.deepcopy(my_queue)
    item_count = 0
    while(len(q) != 0):
        points = q.pop()
        for samp in points:
            item_count += 1
            xs.append([samp[0]])
            ys.append([samp[1]])
    if(item_count > 1):
        X = np.array(xs)
        Y = np.array(ys)
        line_fit = LinearRegression().fit(X, Y)
        return line_fit
    else:
        return None
 
    
