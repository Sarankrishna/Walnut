#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import picamera
import datetime
import subprocess
import dropbox
import os

# Get your app key and secret from the Dropbox developer website
app_key = 'xk1ddgnrj6tyng8'
app_secret = 'eib3ccv5rylgmq3'

def getFileName():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.h264")

def dropboxAuth():
    accessTokenFileOverwrite = open("accessToken.txt", "w+")
    
    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
    authorize_url = flow.start()
    
    # Have the user sign in and authorize this token
    authorize_url = flow.start()
    print '1. Go to: ' + authorize_url
    print '2. Click "Allow" (you might have to log in first)'
    print '3. Copy the authorization code.'
    code = raw_input("Enter the authorization code here: ").strip()

    try:
        # This will fail if the user enters an invalid authorization code
        access_token, user_id = flow.finish(code)
        accessTokenFileOverwrite.write(access_token)
    except:
        print "failed authorization, restart"
        accessTokenFileOverwrite.close()
        os.remove("accessToken.txt")

    accessTokenFileOverwrite.close()

def dropboxUpload(fileToUpload):
    if not os.path.isfile("accessToken.txt"):
        dropboxAuth()

    #get access token from file
    accessTokenFileRead = open("accessToken.txt", "r")
    access_token = accessTokenFileRead.read()
    accessTokenFileRead.close()

    # make client
    client = dropbox.client.DropboxClient(access_token)

    #upload file
    fileToUploadObject = open(fileToUpload, "rb")
    response = client.put_file(fileToUpload, fileToUploadObject)
    fileToUploadObject.close()


sensorPin = 7 

GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensorPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

prevState = False
currState = False

cam = picamera.PiCamera()

while True:
    time.sleep(0.1)
    prevState = currState
    currState = GPIO.input(sensorPin)
    if currState != prevState:
        newState = "HIGH" if currState else "LOW"
        print "GPIO pin %s is %s" % (sensorPin, newState)
        if currState:
            fileName = getFileName()
            print "Starting Recording..."
            cam.start_preview()
            cam.start_recording(fileName)
            print (fileName)
        else:
            cam.stop_preview()
            cam.stop_recording()
            print "Stopped Recording"
            strconvert = "MP4Box -fps 30 -add " + fileName + " " + fileName + ".mp4"
            print strconvert
	    subprocess.call(strconvert, shell=True)
            print "Sending Mail Notification..."
            subprocess.call("mail -s 'Motion Detected' saran.rk@gmail.com < /home/pi/motion-sensor/message.txt", shell=True)
            print "Complete"
            print "Uploading footage to Dropbox..."
            dropboxUpload(fileName+".mp4")
            print "Complete"

