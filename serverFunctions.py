import httpRequests
import writingJson
import readingJson
import syncParameters
import ping
import database
import mysql.connector.errors
from time import sleep

# These functions setup the functions for the main program

def serverCheck(primaryServerIP):
    """
    This function is run on the secundary server. It checks if the primary server is online and switches activity if it
    is/isn't.
    """
    if ping.ping(primaryServerIP) == "Online":
        activity = "inactive"
    else:
        activity = "active"
    return activity

def gpioRequest():
    """ This function will return a tuple containing the water height integer and gate status string. """
    waterHeight,gateStatus = readingJson.serverReadGpioJson("http://192.168.42.3","gpiodata.json")
    return waterHeight,gateStatus

def synchroniseParameters(serverIP):
    """ This function synchronises the parameters. """
    return syncParameters.syncParameters(serverIP,"serverdata.json","./parameters.json")

def getParameters():
    """ This function reads the parameters that are stored on the device """
    paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall = syncParameters.readParameters("./parameters.json")
    return paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall

# These functions should be run in the main program
def giveInstruction(serverNum,primaryServerIP):
    """
    This function checks if the server is the primary server. If so it will always be active. If the server is secundary
    it will set itself to inactive. All the data is gathered from the gpio pi and the web api and the parameters are
    obtained from the local file. A calculation is made based on the gathered data and the parameters. This calculation
    will result in an instruction for the gpio pi. The instruction is written to the local webserver. Afterwards a
    connection will be made with the database to write the gathered data to it.
    """
    while True:
        if serverNum == 1:
            activity = "active" # primary server is always active
        else:
            activity = serverCheck(primaryServerIP)
        waterHeight,gateStatus = gpioRequest()
        paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall = getParameters()
        global buienradarAPI
        while True: # wait for API call if call is not yet made
            try:
                print(buienradarAPI)
                break
            except NameError:
                sleep(1)
                continue
        windSpeed = buienradarAPI["windsnelheidMS"]
        windDirection = buienradarAPI["windrichtingGR"]
        rainFall = buienradarAPI["regenMMPU"]
        buienradarAPI = None # clear variable
        if paramWaterHeight == "-": # check if the parameter should be disabled
            waterHeightBoolean = False
        else:
            waterHeightBoolean = int(waterHeight) > int(paramWaterHeight)
        if paramRainFall == "-": # check if parameter should be disabled
            rainFallBoolean = False
        else:
            if rainFall == "-":
                rainFall = 0
            rainFallBoolean = float(rainFall) > int(paramRainFall)
        windRange = range(int(paramWindDirection) - 45, int(paramWindDirection) + 45)
        windDirectionBoolean = int(windDirection) in windRange
        if paramWindSpeed == "-": # check if the parameter should be disabled
            windSpeedBoolean = False
        else:
            windSpeedBoolean = float(windSpeed) > int(paramWindSpeed)
        if waterHeightBoolean | (windDirectionBoolean & windSpeedBoolean) | rainFallBoolean:
            instruction = "close"
        else:
            instruction = "open"
        writingJson.serverWriteJson(serverNum,activity,instruction,paramWaterHeight,paramWindDirection,paramWindSpeed,paramRainFall)
        if activity == "active":
            try:
                database.makeDatabaseConnection()
                database.insertIntoDatabase(gateStatus,waterHeight,windSpeed,windDirection,serverNum,rainFall)
                database.closeDatabaseConnection()
            except (TimeoutError,mysql.connector.errors.InterfaceError):
                print("Could not connect to database")
        sleep(15)
