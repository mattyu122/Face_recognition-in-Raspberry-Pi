import face_recognition
import cv2
import numpy as np
import os 
import multiprocessing
from sense_hat import SenseHat
import RPi.GPIO as GPIO
import time
from time import sleep
import threading
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from datetime import datetime

def get_credentials():
    token_path = 'token.json'
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/home/matt641879225/Desktop/client_secret_461618973832-0111jkgls8laillr5pbck6himcm4b7qo.apps.googleusercontent.com.json', ['https://www.googleapis.com/auth/gmail.send'])
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds


def send_email(to, subject, body):
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)

    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject

    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    send_message = (service.users().messages().send(userId="me", body=create_message).execute())
    print(F'sent message to {to} Message Id: {send_message["id"]}')
red = [255,0,0] # Red
green = [0,255,0] # Green
minute_color = [0,255,255] # Cyan
empty = [0,0,0] # Black

redImage=[
red,red,red,red,red,red,red,red,
red,red,red,red,red,red,red,red,
red,red,red,red,red,red,red,red,
red,red,red,red,red,red,red,red,
red,red,red,red,red,red,red,red,
red,red,red,red,red,red,red,red,
red,red,red,red,red,red,red,red,
red,red,red,red,red,red,red,red,
]

greenImage=[
green,green,green,green,green,green,green,green,
green,green,green,green,green,green,green,green,
green,green,green,green,green,green,green,green,
green,green,green,green,green,green,green,green,
green,green,green,green,green,green,green,green,
green,green,green,green,green,green,green,green,
green,green,green,green,green,green,green,green,
green,green,green,green,green,green,green,green,
]

def senseHatDisplay(conn):	    
    SERVO_PIN = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PIN,GPIO.OUT)
    pwm = GPIO.PWM(SERVO_PIN,50)
    pwm.start(0)
    def set_servo_angle(angle):
	    duty = angle/18+2
	    GPIO.output(SERVO_PIN,True)
	    pwm.ChangeDutyCycle(duty)
	    sleep(1)
	    GPIO.output(SERVO_PIN,False)
	    pwm.ChangeDutyCycle(0)
    set_servo_angle(180)
    while True:
	    while (not conn.poll()):
		    lastestTime = time.strftime("%y/%m/%d %H:%M")
		    sense.show_message(lastestTime)
	    data = conn.recv()
	    if(data == -1):
		    print("receiving -1")
		    while conn.poll():
			    conn.recv()
		    sense.set_pixels(redImage)
		    set_buzzer(3)
	    elif(data == 1):
		    while conn.poll():
			    conn.recv()
		    print("receiving 1")
		    #sense.set_pixels(greenImage)
		    sense.set_pixels(greenImage)
		    set_buzzer(1)
		    sleep(0.5)
		    set_servo_angle(90)
		    print("before 3")
		    sleep(3) 
		    print("after 3")
		    set_servo_angle(180)

	
def set_buzzer(time = 1):
    tmp = 0
    while tmp<time:
	    GPIO.output(buzzer_pin,GPIO.HIGH)
	    print("Beep")
	    sleep(0.1)
	    GPIO.output(buzzer_pin,GPIO.LOW)
	    sleep(0.1)
	    tmp+=1

if __name__ == "__main__":
    last_authorized = 0
    authorized_interval = 5
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    buzzer_pin = 23
    GPIO.setup(buzzer_pin,GPIO.OUT)
    
    sense = SenseHat()

    parent_conn, child_conn = multiprocessing.Pipe()
    process = multiprocessing.Process(target=senseHatDisplay, args = (child_conn,))
    process.start()
    
    to = 'eziowong0513@gmail.com'
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Format the current time as a string
    subject = f'WARNING!!! Unauthorized Access Attempt - {current_time}'
    body = f"""\
    Security Alert:

    An unauthorized user was detected in front of the door at {current_time}. 
    They remained in front of the door for an extended period, triggering this security alert.

    Please review the security footage and take appropriate action.

    Regards,
    Your Facial Recognition Door System
    CENG4480
    """
    
    # Load the images and learn how to recognize them.
    matt_image = face_recognition.load_image_file("Matt.jpg")
    matt_encoding = face_recognition.face_encodings(matt_image)[0]

    #ezio_image = face_recognition.load_image_file("Ezio.jpg")
    #ezio_encoding = face_recognition.face_encodings(ezio_image)[0]

    known_face_encodings = [matt_encoding]
    known_face_names = ["Matt"]

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    # Start the webcam
    video_capture = cv2.VideoCapture(0)

    while True:
            parent_conn.send(0)
            # Grab a single frame of video
            ret, frame = video_capture.read()

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    # Use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    
                    threshold = 0.5
                    current_time = time.time()
                    if(current_time - last_authorized > authorized_interval):
                        last_authorized = current_time
                        if matches[best_match_index] and face_distances[best_match_index] <= threshold:
                            #Sense hat show unauhorized visitor
                            print("sending 1 to sensehat")
                            parent_conn.send(1)
                            name = known_face_names[best_match_index]
                        else:
                            print("sending -1 to sensehat")
                            parent_conn.send(-1)
                            send_email(to, subject, body)
                    face_names.append(name)

            process_this_frame = not process_this_frame

        # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

            # Display the resulting image
            cv2.imshow('Video', frame)

            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    process.join()


    # Release handle to the webcam
