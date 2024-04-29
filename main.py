import cv2
import numpy as np
import socket


def send_to_esp32(message):
    esp_ip = '192.168.176.251'  # Example IP
    esp_port = 12345  # Example port
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((esp_ip, esp_port))
            s.sendall(message.encode())
    except Exception as e:
        print(f"Failed to send data: {e}")


background_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)
homography_matrix = np.load('matrix.npy')

colors_hsv = {
    'yellow': ([10, 161, 131], [26, 255, 255]),
    'red': ([0, 137, 72], [5, 255, 255]),
    'green': ([43, 67, 104], [92, 255, 255]),
}

cap = cv2.VideoCapture(3)


user = False
centers = {'yellow': None, 'red': None, 'green': None}
last_send_time = 0
run = True
while run:
    ret, frame = cap.read()
    if not ret:
        break
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    fg_mask = background_subtractor.apply(frame_hsv)

    for color, (lower, upper) in colors_hsv.items():
        lower_hsv = np.array(lower)
        upper_hsv = np.array(upper)

        mask = cv2.inRange(frame_hsv, lower_hsv, upper_hsv)

        if color != 'green':
            mask = cv2.bitwise_and(mask, mask, mask=fg_mask)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        avg = []
        for cnt in contours:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                avg.append([M["m10"] / M["m00"], M["m01"] / M["m00"]])

        if avg:
            center = np.average(avg, axis=0)
            centers[color] = center
            cv2.circle(frame, (int(center[0]), int(center[1])), 5, (0, 255, 0), -1)
            cv2.putText(frame, f"{color} center", (int(center[0]) - 50, int(center[1]) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    if all(center is not None for center in centers.values()):
        x = (homography_matrix @ np.append(centers['yellow'], 1))
        y = (homography_matrix @ np.append(centers['red'], 1))
        g = (homography_matrix @ np.append(centers['green'], 1))
        x = x[:2] / x[2]
        y = y[:2] / y[2]
        g = g[:2] / g[2]
        direction_vector = y - x
        transformed_direction_point = direction_vector
        if user == True:
            ideal =  user_g - direction_vector
        else:
            ideal = g - direction_vector
        print("Vector")
        print(x)
        print(ideal)
        orientation = np.arctan2(transformed_direction_point[1], transformed_direction_point[0])
        ideal_orientation = np.arctan2(ideal[1], ideal[0])

        current_orientation_deg = np.rad2deg(orientation)
        ideal_orientation_deg = np.rad2deg(ideal_orientation)
        print("Angle")
        print(current_orientation_deg)
        print(ideal_orientation_deg)
        diff = np.abs(x - ideal)
        print(diff)
        if diff[0] < 0.5 and diff[1] < 0.5:
            send_to_esp32("STOP")
            user_g = input("Input point: ")
            user_g = user_g.strip().split(',')
            user_g = np.array(float(user_g[0]),float(user_g[1]))
        else:
            message = f"Current:{current_orientation_deg},Ideal:{ideal_orientation_deg}"
            send_to_esp32(message)
        centers = {'yellow': None, 'red': None, 'green': None}

    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()