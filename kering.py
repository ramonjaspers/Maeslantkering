# Import the right modules to get the GPIO pins and timeouts working
import RPi.GPIO as GPIO
import time
import os
import json

# Set the numbering mode of the GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup the channels we are going to use for the alarm system
GPIO.setup(2, GPIO.IN)  # Sensor 25
GPIO.setup(3, GPIO.IN)  # Sensor 50
GPIO.setup(4, GPIO.IN)  # Sensor 75
GPIO.setup(17, GPIO.OUT)  # Poort
gate = GPIO.PWM(17, 50)
GPIO.setup(27, GPIO.OUT)  # Alarm lamp

# Define some global variables that are used throughout the script
counter = 0
gateStatus = "open"
sensorLevel = 0
rotations = 2
sensor25 = GPIO.input(2)
sensor50 = GPIO.input(3)
sensor75 = GPIO.input(4)
primary = sensor25
wetSensors = []
dry = True
wet = False
waitTime = 5
operating = True
json_post = "pad"
json_get = "pad"

# Define some classes:

# De gate class, here the TI stuff gets defined | ToDo: Vragen of we er ook nog een lampje bij willen + volledigheid
class gateClass:
    def open_gate(duration):
        global gateStatus
        gateStatus = "opening"
        gate.start(10)
        time.sleep(duration)
        gate.stop()
        gateStatus = "open"

    def close_gate(duration):
        global gateStatus
        gateStatus = "closing"
        gate.ChangeDutyCycle(5)
        time.sleep(duration)
        gate.stop()
        gateStatus = "closed"

    def change_parameters(newValue):
        global gateSensor, sensor25, sensor50, sensor75
        if newValue in (sensor25, sensor50, sensor75):
            gateSensor = newValue
        else:
            #Straks kan dit weg
            print("wrong value")

# The communication class, here the json stuff gets defined | ToDo: Achterkomen of Ramon dit nou al gedaan had
class communicationClass:
    def post_json(location):
        data = {
            "system": {
                "75": str(sensor75),
                "50": str(sensor50),
                "25": str(sensor25) },
            "keringstatus": gateStatus
            }
        with open("data_kering.json", "w") as saveLocation:
            json_kering = json.dumps(data, saveLocation)

    def get_json(saveLocation):
        with open("data_server.json") as readLocation:
            data = json.load(readLocation)
            # Stuff

# The while loop, main part of the program | ToDo: bespreken met iedereen wat hier nog aan toegevoegd moet worden

while True:
    # The script waits a couple of seconds before executing the while loop again
    time.sleep(waitTime)
    gateSensor = primary
    print("checking")
    print(gateStatus)
    print(gateSensor)
    # Post the json with the current information
    #communicationClass.post_json(json_post)
    # Get the json with new instructions / parameter changes
    #communicationClass.get_json(json_get)
    # If de gate is closed and the sensor(which defines when to close) is dry, open the gate
    if gateStatus == "closed" and gateSensor == dry:
        gateClass.open_gate(rotations)
    # If the gate is opened and isnt opening or closing, check if it should close
    elif gateStatus ==  "open":
        if gateSensor == wet:
            print("hi")
            gateClass.close_gate(rotations)
