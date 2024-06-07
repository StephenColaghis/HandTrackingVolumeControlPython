import cv2
import HandTrackingModule as htm
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import time
import math
import numpy as np

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)

cap.set(3, wCam)
cap.set(4, hCam)
pTime=0

detector = htm.handDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0

while True:
    success, img=cap.read()

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if lmList != ([], []):
        x1, y1 = lmList[0][4][1], lmList[0][4][2]  # το 4 είναι ο αντίχειρας
        x2, y2 = lmList[0][20][1], lmList[0][20][2]  # το 20 είναι το μικρό δάχτυλο
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # τα κέντρα τους

        # παράμετροι: (εικόνα, κέντρο, διάμετρος, χρώμα, thickness)
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)  # Κύκλος στο π΄ρωτο δάχτυλο
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)  # κύκλος στο δεύτερο δάχτυλο

        # παράμετροι: (εικόνα, πρώτο σημείο, δεύτερο σημείο, χρώμα, thickness)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)  # γραμμή μεταξύ των 2 σημείων
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)  # κύκλος στο κέντρο

        length = math.hypot(x2 - x1, y2 - y1)  # υπολογισμός απόστασης σημείων δαχτύλων

        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        volPer = np.interp(length, [50, 300], [0, 100])

        print("length: "+str(length)+", vol: "+str(vol))

        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, "FPS: "+str(int(fps)), (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow("Gesture Volume Control", img)

    k = cv2.waitKey(1)
    if k%256 == 27:
        print("Escape hit, closing...")
        break
cap.release()
cv2.destroyAllWindows()