import cv2
import datetime
import mediapipe as mp
import math
from collections import deque
import socket

import draw_utils
import gesture_utils
import network_utils

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


# For webcam input:
cap = cv2.VideoCapture(0)

midpoint_q_zoom = deque(maxlen=gesture_utils.queue_size_zoom)
midpoint_q_zoom.clear()

midpoint_q_translate = deque(maxlen=gesture_utils.queue_size_translate)
midpoint_q_translate.clear()

bb_area_q = deque(maxlen=gesture_utils.queue_size_zoom)
bb_area_q.clear()


##initial molecule state
zoom_state = 1
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
              hand_areas.append(horizontal_dist * vertical_dist) 
              quant += 1
              x = (wrist.x)/horizontal_dist
              y = (wrist.y)/vertical_dist

              midpoints.append([x , y])

              mp_drawing.draw_landmarks(
                  image,
                  hand_landmarks,
                  mp_hands.HAND_CONNECTIONS,
                  mp_drawing_styles.get_default_hand_landmarks_style(),
                  mp_drawing_styles.get_default_hand_connections_style())
          midpoint_q_zoom.append(midpoints)
          midpoint_q_translate.append(midpoints)
          bb_area_q.append(hand_areas)
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

          '''
          ### TRANSLATION
          t_vect = gesture_utils.translate(midpoint_q_translate)
          if(t_vect != None):
            network_utils.send_message(conn, "move", "translate", t_vect)
            print("Translator" + str(t_vect))
          else:
            network_utils.send_message(conn, "move", "translate", [0, 0])
          '''
          ### ZOOM 
          #If zoom is detected, clear all data points so that multiple zooms do not occur after first zoom is detected
          factor = gesture_utils.zoom(midpoint_q_zoom)
          area_variance = gesture_utils.boundingBoxVariance(bb_area_q)
          if(factor != None and area_variance != None):
              zoom_state += factor
              if(zoom_state < 0):
                zoom_state = 1
              gesture_utils.printQDesmos(midpoint_q_zoom)
              print("Variance:" + str(area_variance))
              midpoint_q_zoom.clear()
          network_utils.send_message(conn, "move", "zoom", [zoom_state])



          if(len(midpoint_q_zoom) == midpoint_q_zoom.maxlen):
              midpoint_q_zoom.popleft()
          if(len(midpoint_q_translate) == midpoint_q_translate.maxlen):
              midpoint_q_translate.popleft()
          
          # Flip the image horizontally for a selfie-view display.
          cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
          if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()
