import cv2
import numpy as np

def nothing(x):
    # Callback function for the trackbar, not used here
    pass

# Create a window for the trackbars
cv2.namedWindow('HSV Tuner')

# Create trackbars for each HSV component. Adjust the ranges if necessary.
cv2.createTrackbar('Hue Min', 'HSV Tuner', 0, 179, nothing)
cv2.createTrackbar('Hue Max', 'HSV Tuner', 179, 179, nothing)
cv2.createTrackbar('Sat Min', 'HSV Tuner', 0, 255, nothing)
cv2.createTrackbar('Sat Max', 'HSV Tuner', 255, 255, nothing)
cv2.createTrackbar('Val Min', 'HSV Tuner', 0, 255, nothing)
cv2.createTrackbar('Val Max', 'HSV Tuner', 255, 255, nothing)

cap = cv2.VideoCapture(3)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get the current positions of the trackbars
    h_min = cv2.getTrackbarPos('Hue Min', 'HSV Tuner')
    h_max = cv2.getTrackbarPos('Hue Max', 'HSV Tuner')
    s_min = cv2.getTrackbarPos('Sat Min', 'HSV Tuner')
    s_max = cv2.getTrackbarPos('Sat Max', 'HSV Tuner')
    v_min = cv2.getTrackbarPos('Val Min', 'HSV Tuner')
    v_max = cv2.getTrackbarPos('Val Max', 'HSV Tuner')

    # Define the HSV range from the trackbar positions
    lower_hsv = np.array([h_min, s_min, v_min])
    upper_hsv = np.array([h_max, s_max, v_max])

    # Create a mask for the current HSV range
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)

    # Show the original frame and the mask
    cv2.imshow('Frame', frame)
    cv2.imshow('Mask', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Print final HSV range for user reference
print(f"Final HSV Range: Hue ({h_min}, {h_max}), Saturation ({s_min}, {s_max}), Value ({v_min}, {v_max})")

cap.release()
cv2.destroyAllWindows()