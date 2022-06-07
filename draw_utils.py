import cv2
import copy
from sklearn.linear_model import LinearRegression
import math

def drawLinearRegressionDebug(my_queue, image_np, fit, color):
    q = copy.deepcopy(my_queue)
    while len(q) > 0:
        elem = q.pop()
        for x in elem:
            cv2.circle(image_np, (int(x[0]), int(x[1])), 2, (121, 28, 227))
    point1 = (0, 0)
    point2 = (0, 0)
    if(fit != None):
        slope = fit.coef_[0]
        intercept = fit.intercept_[0]
        height = image_np.shape[0]
        width = image_np.shape[1]
        if(intercept >= 0):
            point1 = (0, int(intercept))
        else:
            point1 = (int((-intercept/slope)), 0)
        if(int((slope*width) + intercept) <= height):
            point2 = (width, int((slope*width) + intercept))
        else:
            point2 = (int((height - intercept)/slope),height)
        cv2.line(image_np, point1, point2, color, 3)
