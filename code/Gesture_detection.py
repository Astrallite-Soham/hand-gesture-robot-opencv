import cv2
import mediapipe as mp
import socket #Transfer from computer to esp

ESP32_IP = "10.246.151.27"
ESP32_PORT = 4210

mp_hands = mp.solutions.hands #show hands
mp_drawing = mp.solutions.drawing_utils #the lines for hands(hand pattern)

hands = mp_hands.Hands(min_detection_confidence=0.8, #min 80% detection
                       min_tracking_confidence=0.8, #min 80% detection
                       max_num_hands=1) #only one hand can be shown at a time
cap=cv2.VideoCapture(0) #access camera

FINGER_TIPS = [8,12,16,20] #Landmark for fingers {Index, Middle, Ring, Pinky}
THUMB_TIP = 4 # Landmark 4
THUMB_IP = 2 #Thumb joint

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #AF_INET (IP ADDRESS  OF ESP VALUE{IP V4}) , DGRAM (UDP OF ESP PORT)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #filtering color from bgr to rgb
    results = hands.process(rgb_frame)
    
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        landmarks = hand_landmarks.landmark
        hand_label = results.multi_handedness[0].classification[0].label
        fingers_extended = 0
        
        for tip in FINGER_TIPS:
            if landmarks[tip].y < landmarks[tip - 2].y: # y cord of lifted finger is greater than other fingers (whose y cord is 0)
                fingers_extended += 1
                
        if hand_label == "Right": #If the hand is right
            if landmarks[THUMB_TIP].x < landmarks[THUMB_IP].x: 
                fingers_extended += 1
        else:
            if landmarks[THUMB_TIP].x > landmarks[THUMB_IP].x:
                fingers_extended += 1
        
        try:
            sock.sendto(str(fingers_extended).encode(),
               
               (ESP32_IP,ESP32_PORT))
            print(f"Sent data: {fingers_extended}")
        except Exception as e:
            print(f"Error sending data: {e}")
        
        mp_drawing.draw_landmarks(frame, hand_landmarks,
                                  mp_hands.HAND_CONNECTIONS)
        cv2.putText(frame, f"Fingers: {fingers_extended}",
                    (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 2) #Green
        cv2.imshow('Finger Detection', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
cap.release()
cv2.destroyAllWindows()
sock.close()
