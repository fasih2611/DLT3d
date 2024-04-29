import cv2

# clicked coordinates are printed on to the terminal can be adjusted to store in an array,file etc.
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'({x},{y}),')

# change 0-2 until you can find the video stream from attached camera 
cap = cv2.VideoCapture(3)

cv2.namedWindow('Video Feed')
cv2.setMouseCallback('Video Feed', click_event)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow('Video Feed', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()