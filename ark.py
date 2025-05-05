import cv2
import numpy as np
import serial

url = "http://192.168.1.35:8080/video"
cap = cv2.VideoCapture(0)
ser = serial.Serial('COM9', 115200, timeout=1)

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

    cv2.circle(frame, center_screen, 5, (0, 0, 255), -1)

    if len(contours) > 0:
        cnt = max(contours, key=cv2.contourArea) 

        if cv2.contourArea(cnt) > 500:
            x, y, w, h = cv2.boundingRect(cnt) 
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2) 

            M = cv2.moments(cnt)
            if M["m00"] > 0:
                center_x = int(M["m10"] / M["m00"])
                center_y = int(M["m01"] / M["m00"])
                center_object = (center_x, center_y)

                cv2.circle(frame, center_object, 5, (255, 0, 0), -1)

                cv2.line(frame, center_screen, center_object, (0, 255, 0), 2)
                cv2.putText(frame, "Vector", (center_screen[0] + 10, center_screen[1] - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
            rotX = (width / 2) - center_x
            serX = max(0, min(180, int((rotX // 3.5) + 90)))
            print(f"Gönderilen Açı: {serX}")
            ser.write(f"{serX}\n".encode())

    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()