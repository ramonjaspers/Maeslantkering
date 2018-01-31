# Import the right modules to get the GPIO pins and timeouts working
import RPi.GPIO as GPIO
import time
from readingJson import gpioReadServerJson
from writingJson import gpioWriteJson

# Set the numbering mode of the GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup the channels we are going to use for the alarm system
GPIO.setup(2, GPIO.IN)  # Sensor 25
GPIO.setup(3, GPIO.IN)  # Sensor 50
GPIO.setup(4, GPIO.IN)  # Sensor 75
GPIO.setup(17, GPIO.OUT)  # P+oort
gate = GPIO.PWM(17, 50)
GPIO.setup(27, GPIO.OUT)  # Alarm lamp

# Define some global variables that are used throughout the script
gateStatus = "open"
rotations = 27
sensor25 = GPIO.input(2)
sensor50 = GPIO.input(3)
sensor75 = GPIO.input(4)
waitTime = 10
gate.start(0)

# Define some classes:

# De gate class, here the TI stuff gets defined
class gateClass:
    def open_gate(duration):
        global gateStatus, gate
        gateStatus = "opening"
        gpioWriteJson(sensor25,sensor50,sensor75,gateStatus)
        gate.ChangeDutyCycle(5)
        time.sleep(duration)
        gate.ChangeDutyCycle(0)
        gateStatus = "open"

    def close_gate(duration):
        global gateStatus, gate
        gateStatus = "closing"
        gpioWriteJson(sensor25,sensor50,sensor75,gateStatus)
        gate.ChangeDutyCycle(10)
        time.sleep(duration)
        gate.ChangeDutyCycle(0)
        gateStatus = "closed"

    def update_variables():
        global sensor50, sensor25, sensor75
        # variable is 0 when touching water and 1 when dry
        sensor25 = GPIO.input(2)
        sensor50 = GPIO.input(3)
        sensor75 = GPIO.input(4)




# The while loop, main part of the program

while True:
    # The script waits a couple of seconds before executing the while loop again
    gateClass.update_variables()
    gpioWriteJson(sensor25,sensor50,sensor75,gateStatus)
    time.sleep(waitTime)
    print("Sensor 25: " + str(sensor25))
    print("Sensor 50: " + str(sensor50))
    print("Sensor 75: " + str(sensor75))
    print("Gate status: " + gateStatus)
    try:
        instruction = gpioReadServerJson("192.168.42.1","192.168.42.4","serverdata.json")
        print(instruction)
    except TypeError:
        print("No json file from server")
        instruction = "open"
    print(instruction)
    if gateStatus == "closed" and instruction == "open":
        gateClass.open_gate(rotations)
    # If the gate is opened and isnt opening or closing, check if it should close
    elif gateStatus == "open" and instruction == "close":
        gateClass.close_gate(rotations)
