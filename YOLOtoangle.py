import cv2
import serial
from ultralytics import YOLO
import numpy as np

cap = cv2.VideoCapture(0)
ser = serial.Serial('COM9', 9600, timeout=1)

model = YOLO("yolov8n.pt")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width = frame.shape[:2]
    center_screen = (width // 2, height // 2)
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

    lower_blue = np.array([0, 100, 200])
    upper_blue = np.array([140, 255, 255])
    
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) > 0:
        cnt = max(contours, key=cv2.contourArea) 

        if cv2.contourArea(cnt) > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2) 
            tx = x + w // 2
            ty = y + h // 2
            cv2.circle(frame, (tx, ty), 5, (0, 255, 0), -1)

    results = model(frame)[0]

    person_detected = False

    for result in results.boxes:
        cls = int(result.cls[0])
        if cls == 67:
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            
            if x2-x1 >= y2-y1:
                r = y2-y1
            else:
                r = x2-x1

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.circle(frame, (cx, cy), r//2, (255, 0, 0), 1)

            cv2.line(frame, center_screen, (cx, cy), (0, 255, 0), 2)
            cv2.putText(frame, "Vector", (center_screen[0]+10, center_screen[1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            rotX = (width / 2) - cx
            serX = (rotX // 3.5) + 90
            ser.write(f"{int(serX)}\n".encode())

            person_detected = True
            break

    cv2.circle(frame, center_screen, 5, (0, 0, 255), -1)


    cv2.imshow("YOLOv8 Human Detection", frame)
    cv2.imshow("..", mask)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()