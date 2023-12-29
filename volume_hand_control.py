import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#project based on work of Murtaza Hassan

###################################################
wCam, hCam=1080,720

##################################################

cap= cv2.VideoCapture(0,cv2.CAP_DSHOW)

cap.set(3,wCam)
cap.set(4,hCam)
pTime = 0

detector =htm.handDetector()




devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange= (volume.GetVolumeRange())
print(volRange)

minVol=volRange[0]
maxVol=volRange[1]
vol=0
volBar=400
volPerc=0

minPalce=2
maxPalce=115
minSW=60

while True:
    success, img=cap.read()
    img= detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) !=0:
        #print(lmList[4],lmList[8])
        x0, y0 = lmList[0][1], lmList[0][2]
        x20, y20 = lmList[20][1], lmList[20][2]

        x4, y4 = lmList[4][1], lmList[4][2]
        x8, y8 = lmList[8][1], lmList[8][2]
        cx,cy= (x4+x8)//2, (y4+y8)//2

        cv2.circle(img,(x4,y4),7,(255,0,0),cv2.FILLED)
        cv2.circle(img,(x8,y8),7,(255,0,0),cv2.FILLED)
        cv2.line(img, (x4,y4),(x8,y8), (255,0,0),3)
        cv2.circle(img,(cx,cy),7,(255,0,0),cv2.FILLED)
        length = math.hypot(x8-x4,y8-y4)

        length0to20 = math.hypot(x20-x0,y20-y0)
        #print(length0to20)
        #print(length)
        # hande range 50 to  300
        # vol range -64 to 0

        vol= np.interp(length,[minPalce,maxPalce], [minVol, maxVol])
        volBar= np.interp(length,[minPalce,maxPalce], [400, 150])
        volPerc= np.interp(length,[minPalce,maxPalce], [0, 100])

        #print(vol)
        if length0to20 >minSW:
            volume.SetMasterVolumeLevel(vol, None)

        if length < 50:
            cv2.circle(img, (cx, cy), 7, (255, 255, 0), cv2.FILLED)
        if length0to20 > minSW:
            cv2.rectangle(img,(50,150),(85,400),(255,0,0),3)
            cv2.rectangle(img,(50,int(volBar)),(85,400),(255,0,0),cv2.FILLED)
            cv2.putText(img, f' {int(volPerc)} %', (30, 450), cv2.FONT_ITALIC, 1, (255, 0, 0), 3)

            cv2.putText(img, f'VOLUME CONTROL ON', (180, 40), cv2.FONT_ITALIC, 1, (0, 0, 255), 3)

        if length0to20 < minSW:
            cv2.putText(img, f'VOLUME CONTROL OFF', (180, 40), cv2.FONT_ITALIC, 1, (0, 0, 255), 3)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime


    cv2.putText(img,f'FPS: {int(fps)}', (30,40), cv2.FONT_ITALIC,1, (255,0,0),3)
    cv2.imshow("img",img)
    cv2.waitKey(1)