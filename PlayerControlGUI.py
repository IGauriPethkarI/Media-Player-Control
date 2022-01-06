import cv2
import time
import os
import pyautogui
import math
import numpy as np
import tkinter as tk
from tkinter import font as tkFont
import PIL.Image, PIL.ImageTk

import HandTrackingModule as htm

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def mediaControlSystem():
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
            
            cv2.rectangle(img, (30, 420), (170, 460), (195,195,195), cv2.FILLED)

            if fingers == [1,1,1,1,1]:
                cv2.putText(img, "Play-Pause", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,0), 2)
                pyautogui.hotkey('playpause')
                pyautogui.PAUSE = 1.5

            elif fingers == [0,0,0,0,0]:
                cv2.putText(img, "Stop", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,0), 2)
                pyautogui.hotkey('stop')
            
            elif fingers == [0,0,0,0,1]:
                cv2.putText(img, "Backword", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,0), 2)
                pyautogui.press("left")
            
            elif fingers == [0,1,0,0,0]:
                cv2.putText(img, "Forward", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,0), 2)
                pyautogui.press("right")

            elif fingers == [0,1,1,0,0]:
                cv2.putText(img, "Mute", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,0), 2)
                pyautogui.hotkey('volumemute')
                pyautogui.PAUSE = 1.5

            elif fingers == [1,1,0,0,0]:
                cv2.putText(img, "Volume", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,0), 2)
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

    
window = tk.Tk()
window.title("Media Player Control System")
window.geometry('640x360')
window.resizable(width = False, height = False)
window.configure(background = "#839dc6")

title = tk.Label(text = "Media Player Control System")
title.configure(background='#3f5d8a', foreground='white', font = ('times', 18, 'bold'), width = 900, height = 2)
title.pack()

canvas3 = tk.Canvas(window, width = 610, height = 220)
canvas3.pack()
canvas3.configure(background = "#3f5d8a")
canvas3.place(x = 15, y = 70)

img1 = PIL.Image.open("Control Options.jpg")
img1 = img1.resize((590,200), PIL.Image.ANTIALIAS)
img1 = PIL.ImageTk.PhotoImage(img1)
canvas = tk.Label(window, image = img1)
canvas.image = img1
canvas.pack()
canvas.place(x = 25, y = 80)

start = tk.Button(window, text="Start", command= mediaControlSystem, padx=10, pady=5)
start.configure(background='#3f5d8a', foreground='white',font=('times',15,'bold'))
start.pack()
start.place(x = 180, y = 300)

exit = tk.Button(window, text="Exit",command = window.destroy, padx = 20, pady=5)
exit.configure(background='#3f5d8a', foreground = 'white',font=('times',15,'bold'))  
exit.pack()
exit.place(x = 320, y = 300)

window.mainloop()