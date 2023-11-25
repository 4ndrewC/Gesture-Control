import mediapipe as mp
import cv2
import math

from ctypes import cast, POINTER
from pycaw.pycaw import AudioUtilities
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import GUID

import normalize


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)

class AudioEndpointVolume(IAudioEndpointVolume):
    _iid_ = GUID('{5CDF2C82-841E-4546-9722-0CF74078229A}')
    _methods_ = IAudioEndpointVolume._methods_

def set_speaker_volume(volume):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(GUID('{5CDF2C82-841E-4546-9722-0CF74078229A}'), CLSCTX_ALL, None)
    volume_object = cast(interface, POINTER(AudioEndpointVolume))
    volume_object.SetMasterVolumeLevelScalar(volume, None)

def get_speaker_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_object = cast(interface, POINTER(IAudioEndpointVolume))
    return volume_object.GetMasterVolumeLevelScalar()

distances = []
landmarks_to_draw = [0, 9]
pos = []
with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands: 
    inc = 0
    while cap.isOpened():
        ret, frame = cap.read()        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)        
        image = cv2.flip(image, 1)
        image.flags.writeable = False
        results = hands.process(image)        
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        
        # Rendering results
        if results.multi_hand_landmarks:
            for num, hand in enumerate(results.multi_hand_landmarks):
                # print(hand.landmark)
                for idx, landmark in enumerate(hand.landmark):
                    x = int(landmark.x * image.shape[1])
                    y = int(landmark.y * image.shape[0])
                    if idx in landmarks_to_draw:
                        cv2.circle(image, (x, y), 4, (121, 22, 76), -1)
                    
                
                indexjoint1 = hand.landmark[9]
                wrist = hand.landmark[0]
                
                
                normalized_landmarks = normalize.normalize(hand.landmark)

                # mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS, 
                #                         mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                #                         mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2),
                #                          )
                inc+=1
                # if inc%5==0:
                #     print(angle, "degrees; ", abs(normalized_landmarks[9].y-normalized_landmarks[0].y))
                    # print(hand.landmark[9])
                index = normalized_landmarks[8]
                thumb = normalized_landmarks[4]
                thumbbutt = normalized_landmarks[2]
                middle = normalized_landmarks[12]
                indexjoint1 = normalized_landmarks[9]
                indexjoint2 = normalized_landmarks[6]


                indexpos = [index.x, index.y]
                thumbpos = [thumb.x, thumb.y]
                middlepos = [middle.x, middle.y]
                indexj2pos = [indexjoint2.x, indexjoint2.y]
                dist = indexjoint2.y-index.y
                dist2 = math.dist(middlepos, thumbpos)
                
                if len(distances)>10:
                    distances.pop(0)
                distances.append(dist)

                for i in range(len(distances)):
                    if len(distances)>=9 and distances[i]>0.3 and i<5 and dist<0:
                        print("increase volume")
                        curvol = get_speaker_volume()
                        if 1-curvol<0.05:
                            set_speaker_volume(1)
                        else: 
                            set_speaker_volume(curvol+0.05)
                        distances.clear()
                        break
                
                print(indexjoint2.y-index.y, "; ", indexjoint1.y-wrist.y)
        cv2.imshow('Hand Tracking', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
