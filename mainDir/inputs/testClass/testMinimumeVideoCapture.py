import cv2

capture = cv2.VideoCapture(7)
while True:
    ret, frame = capture.read()
    cv2.imshow("Video", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break