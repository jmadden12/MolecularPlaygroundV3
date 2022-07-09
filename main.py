import cv2
import datetime
import mediapipe as mp
import math
from collections import deque
import socket

import draw_utils
import gesture_utils
import network_utils
import playlist_utils

## MEDIAPIPE INITIALIZATION
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands




## HAND DETECTION ACTIVE
hand_detection_active = False


## DECISION TREE COEFFICIENTS
## Distances are expressed in terms of hand lengths
## ALL
global_dist_threshold = 1

## 1 HAND

## 2 HANDS
each_hand_dist_thresh = global_dist_threshold * 0.37

zoom_dist_thresh_total = 1
zoom_dist_thresh_each = 0.5

translate_fl_delta_thresh = 0.8

# For webcam input:
cap = cv2.VideoCapture(0)

midpoint_q = deque(maxlen=gesture_utils.queue_size)
midpoint_q.clear()

normalization_factors_q = deque(maxlen=gesture_utils.queue_size)
normalization_factors_q.clear()


playlist_utils.cleanup_script_files()

playlist_name = "amino_acids"

if(len(playlist_name) > 0):
  playlist_utils.create_playlist_script_file(playlist_name)



##initial molecule state
zoom_state = 100

translate_state_x = 0
translate_state_y = 0

zoom_mult = 1


with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

    with socket.socket() as s: 
      s.bind((network_utils.HOST, network_utils.PORT))
      print('Waiting for connection on Host: %s, Port: %s'%(network_utils.HOST, network_utils.PORT))
      s.listen(1)
      conn, addr = s.accept()
      with conn:
        #network_utils.send_command(conn, "source \"" + playlist_utils.TEMPFILE_DIRECTORY + playlist_name + playlist_utils.SCRIPT_FILE_EXT + "\"")
        network_utils.send_command(conn, "script genericscript.spt")
        while cap.isOpened():
          success, image = cap.read()
          if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue
          ## test fps

          # To improve performance, optionally mark the image as not writeable to
          # pass by reference.
          image.flags.writeable = False
          image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
          results = hands.process(image)

          # Grab image height and width to de-normalize x, y values
          image_height, image_width, _ = image.shape

          # Draw the hand annotations on the image.
          image.flags.writeable = True
          image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
          midpoints = list()
          norm_factors = list()
          hand_areas = list()
          quant = 0
          avg_hz = 0
          avg_vt = 0
          

          if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
              #for vertical normalization
              middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
              wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

              vertical_dist = gesture_utils.euclid2Dimension([middle_finger_tip.x, middle_finger_tip.y], [wrist.x, wrist.y])

              #for horizontal normalization
              palm_thumbside = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
              palm_pinkyside = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]

              horizontal_dist = gesture_utils.euclid2Dimension([palm_thumbside.x, palm_thumbside.y], [palm_pinkyside.x, palm_pinkyside.y])
              avg_hz += horizontal_dist
              avg_vt += vertical_dist

              quant += 1

              x = (wrist.x)
              y = (wrist.y)

              midpoints.append([x , (1/0.37)*y])
              norm_factors.append([horizontal_dist, vertical_dist])
              

              mp_drawing.draw_landmarks(
                  image,
                  hand_landmarks,
                  mp_hands.HAND_CONNECTIONS,
                  mp_drawing_styles.get_default_hand_landmarks_style(),
                  mp_drawing_styles.get_default_hand_connections_style())
          midpoint_q.append(midpoints)
          normalization_factors_q.append(norm_factors)
          if(quant > 0):
            avg_hz /= quant
            avg_vt /= quant
            horizontal_draw_dist = math.ceil(avg_hz * image_width)
            vertical_draw_dist = math.ceil(avg_vt * image_height)
            i = 0
            while(i < image_width):
              cv2.line(image, (i, 0), (i, image_height), (0, 0, 255), 4)
              i += horizontal_draw_dist
            i  = 0
            while(i < image_height):
              cv2.line(image, (0, i), (image_width, i), (0, 0, 255), 4)
              i += vertical_draw_dist

          
          if(hand_detection_active):
            t_vect = [0, 0]
            r_vect = [0, 0]
            if len(midpoint_q) == midpoint_q.maxlen:
              ##                   hands in latest frame  hands in newest frame ##
              hands_detected = min(len(midpoint_q[0]), len(midpoint_q[-1]))
              if hands_detected == 1:
                norm_initial_0 = [midpoint_q[0][0][0]/normalization_factors_q[0][0][0], midpoint_q[0][0][1]/normalization_factors_q[0][0][1]]
                norm_final_0 = [midpoint_q[-1][0][0]/normalization_factors_q[0][0][0], midpoint_q[-1][0][1]/normalization_factors_q[0][0][1]]
                hand0_first_last_dist = gesture_utils.euclid2Dimension(norm_initial_0, norm_final_0)
                if(hand0_first_last_dist > global_dist_threshold):                  
                  ## ROTATE ##
                  zoom_mult = 1
                  r_vect = gesture_utils.rotate(midpoint_q, normalization_factors_q)
                  network_utils.send_move(conn, "rotate", r_vect)
                  print(r_vect)
              if hands_detected == 2:
                x_normalization_0 = (normalization_factors_q[0][0][0])
                y_normalization_0 = (normalization_factors_q[0][0][1])

                x_normalization_1 = (normalization_factors_q[0][1][0])
                y_normalization_1 = (normalization_factors_q[0][1][1])
                
                norm_initial_0_0 = [midpoint_q[0][0][0]/x_normalization_0, midpoint_q[0][0][1]/y_normalization_0]
                norm_final_0_0 = [midpoint_q[-1][0][0]/x_normalization_0, midpoint_q[-1][0][1]/y_normalization_0]
                
                norm_initial_1_0 = [midpoint_q[0][1][0]/x_normalization_1, midpoint_q[0][1][1]/y_normalization_1]
                norm_final_1_0 = [midpoint_q[-1][1][0]/x_normalization_1, midpoint_q[-1][1][1]/y_normalization_1]

                ## ZOOM OR TRANSLATE ##
                hand0_first_last_dist = gesture_utils.euclid2Dimension(norm_initial_0_0, norm_final_0_0)
                hand1_first_last_dist = gesture_utils.euclid2Dimension(norm_initial_1_0, norm_final_1_0)
                if hand0_first_last_dist + hand1_first_last_dist > global_dist_threshold:
                  if hand0_first_last_dist > each_hand_dist_thresh and hand1_first_last_dist > each_hand_dist_thresh:
                    ## Check change in distance between hands, if distance between hands has changed over n frames significantly, is not translate ##
                    avg_x_norm = (x_normalization_0 + x_normalization_1)/2
                    avg_y_norm = (y_normalization_0 + y_normalization_1)/2

                    norm_initial_0_1 = [midpoint_q[0][0][0]/avg_x_norm, midpoint_q[0][0][1]/avg_y_norm]
                    norm_final_0_1 = [midpoint_q[-1][0][0]/avg_x_norm, midpoint_q[-1][0][1]/avg_y_norm]
                    
                    norm_initial_1_1 = [midpoint_q[0][1][0]/avg_x_norm, midpoint_q[0][1][1]/avg_y_norm]
                    norm_final_1_1 = [midpoint_q[-1][1][0]/avg_x_norm, midpoint_q[-1][1][1]/avg_y_norm]
                    hands_initial_dist = gesture_utils.euclid2Dimension(norm_initial_0_1, norm_initial_1_1)
                    hands_final_dist = gesture_utils.euclid2Dimension(norm_final_0_1, norm_final_1_1)
                    if abs(hands_final_dist - hands_initial_dist) > translate_fl_delta_thresh:
                      ## ZOOM ##
                      zoom_delta = gesture_utils.zoom(midpoint_q, normalization_factors_q, hand0_first_last_dist, hand1_first_last_dist, hands_initial_dist, hands_final_dist)
                      if(zoom_delta != None):
                        zoom_mult += 0.03
                        zoom_state += (zoom_delta * 100 * zoom_mult)
                        if(zoom_state < 30):
                          zoom_state = 30
                        if(zoom_state > 300):
                          zoom_state = 300
                        network_utils.send_move(conn, "zoom", [zoom_state])
                        network_utils.send_move(conn, "translate", [translate_state_x, translate_state_y])
                    else:
                      ## TRANSLATE ##
                      zoom_mult = 1
                      t_vect = gesture_utils.translate(midpoint_q, normalization_factors_q)
                      translate_state_x += t_vect[0]
                      translate_state_y += t_vect[1]
                      if(abs(translate_state_x) > 100):
                        translate_state_x = 0
                      if(abs(translate_state_y) > 100):
                        translate_state_y = 0
                      
                      network_utils.send_move(conn, "translate", [translate_state_x, translate_state_y])
                      print("Translate")
      
          if(len(midpoint_q) == midpoint_q.maxlen):
            midpoint_q.popleft()
          if(len(normalization_factors_q) == normalization_factors_q.maxlen):
            normalization_factors_q.popleft()
          
          # Flip the image horizontally for a selfie-view display.
          cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
          if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()
playlist_utils.cleanup_script_files()
