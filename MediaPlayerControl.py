import cv2
import time
import os
import pyautogui
import math
import numpy as np
import HandTrackingModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 500, 500

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, wCam)
cap.set(4, hCam)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

cTime = 0
pTime = 0

detector = htm.handDetector()

tipIds =[4, 8, 12, 16, 20]

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    # print(lmList)

    if len(lmList) != 0:
        fingers = []

        # Thumb
        if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 Fingers
        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        print(fingers)

        cv2.rectangle(img, (30, 420), (150, 460), (0, 255, 0), cv2.FILLED)

        if fingers == [1,1,1,1,1]:
            cv2.putText(img, "Play", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255), 2)
            pyautogui.hotkey('playpause')
            

        elif fingers == [0,0,0,0,0]:
            cv2.putText(img, "Stop", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255), 2)
            pyautogui.hotkey('stop')
        
        elif fingers == [0,0,0,0,1]:
            cv2.putText(img, "Backword", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255), 2)
            pyautogui.press("left")
        
        elif fingers == [0,1,0,0,0]:
            cv2.putText(img, "Forward", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255), 2)
            pyautogui.press("right")

        elif fingers == [0,1,1,0,0]:
            cv2.putText(img, "Mute", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255), 2)
            pyautogui.hotkey('volumemute')
           

        elif fingers == [1,1,0,0,0]:
            cv2.putText(img, "Volume", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255), 2)
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

            length = math.hypot(x2 - x1, y2 - y1)           

            vol = np.interp(length, [3, 150], [minVol, maxVol])
            volume.SetMasterVolumeLevel(vol, None)

            if length < 50:
                cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

        else:
            pass
         
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()