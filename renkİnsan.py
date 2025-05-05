import cv2
import serial
from ultralytics import YOLO
import numpy as np

cap = cv2.VideoCapture(0)
ser = serial.Serial('COM9', 115200, timeout=1)

model = YOLO("yolov8n.pt")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width = frame.shape[:2]
    center_screen = (width // 2, height // 2)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([0, 100, 200])
    upper_blue = np.array([140, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    
    cv2.circle(frame, center_screen, 5, (0, 0, 255), -1)

    results = model(frame)[0]
    for result in results.boxes:
        cls = int(result.cls[0])
        if cls == 0:  
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.line(frame, center_screen, (cx, cy), (0, 255, 0), 2)
            cv2.putText(frame, "Vector", (center_screen[0]+10, center_screen[1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            for cnt in contours:
                if cv2.contourArea(cnt) > 500:
                    rx, ry, rw, rh = cv2.boundingRect(cnt)
                    tx = rx + rw // 2
                    ty = ry + rh // 2

                    cv2.rectangle(frame, (rx, ry), (rx + rw, ry + rh), (255, 0, 255), 2)
                    cv2.circle(frame, (tx, ty), 5, (0, 255, 255), -1)

                    if x1 <= tx <= x2 and y1 <= ty <= y2:
                        serX = (((width / 2) - cx) // 3.5) + 90
                        ser.write(f"{int(serX)}\n".encode())
                        cv2.putText(frame, f"Servo: {int(serX)}", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        break

            break

    cv2.imshow("YOLOv8 Human Detection", frame)
    cv2.imshow("Color Mask", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()