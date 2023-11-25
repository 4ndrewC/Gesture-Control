import mediapipe as mp
import cv2
import numpy as np
import os
import math


class Handd:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

def dist(x1, y1, x2, y2):
    return math.sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1))

def calculate_angle(point1, point2, point3, point4):
    vector1 = (point3[0] - point4[0], point3[1] - point4[1])
    vector2 = (point1[0] - point2[0], point1[1] - point2[1])
    dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
    cross_product = vector1[0] * vector2[1] - vector1[1] * vector2[0]
    angle_radians = math.atan2(cross_product, dot_product)
    angle_degrees = math.degrees(angle_radians)

    return angle_degrees

def normalize(hand_landmarks):

    indexjoint1 = hand_landmarks[9]
    wrist = hand_landmarks[0]
    distance = dist(indexjoint1.x, indexjoint1.y, wrist.x, wrist.y)
    normalized_factor = 1/distance
    
    #normalize the angle
    above_wrist = (wrist.x, wrist.y+(0.3))
    angle = math.radians(calculate_angle((wrist.x, wrist.y), above_wrist, (wrist.x, wrist.y), (indexjoint1.x, indexjoint1.y)))

    #shifting
    xdist = dist(hand_landmarks[0].x, 0, 0, 0)
    ydist = dist(0, hand_landmarks[0].y, 0, 0)
    for i in range(len(hand_landmarks)):
        hand_landmarks[i].x -= xdist
        hand_landmarks[i].y -= ydist

    indexjoint1 = hand_landmarks[9]
    wrist = hand_landmarks[0]


    #rotation
    A = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])

    for i in range(len(hand_landmarks)):
        v = np.array([hand_landmarks[i].x, hand_landmarks[i].y])
        b = np.dot(A, v)
        hand_landmarks[i].x = b[0]
        hand_landmarks[i].y = b[1] 
    

    #flip matrix
    A = np.array([[-1, 0], [0, -1]])

    for i in range(len(hand_landmarks)):
        v = np.array([hand_landmarks[i].x, hand_landmarks[i].y])
        b = np.dot(A, v)
        hand_landmarks[i].x = b[0]
        hand_landmarks[i].y = b[1] 

    #unshift
    for i in range(len(hand_landmarks)):
        hand_landmarks[i].x += xdist
        hand_landmarks[i].y += ydist
    

    #scale each landmark
    for i in range(len(hand_landmarks)):
        hand_landmarks[i].x*=normalized_factor
        hand_landmarks[i].y*=normalized_factor
    
    return hand_landmarks
