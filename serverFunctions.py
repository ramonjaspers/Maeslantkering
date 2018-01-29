import httpRequests
import writingJson
import readingJson
import syncParameters
import ping
import database

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

def gpioRequest(gpioIP):
    """ This function will return a tuple containing the water height integer and gate status string. """
    waterHeight,gateStatus = readingJson.serverReadGpioJson(gpioIP,"gpiodata.json")
    return waterHeight,gateStatus

def synchroniseParameters(serverIP):
    """ This function synchronises the parameters. """
    return syncParameters.syncParameters(serverIP,"serverdata.json","./parameters.json")

def getParameters():
    """ This function reads the parameters that are stored on the device """
    paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall = syncParameters.readParameters("./parameters.json")
    return paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall

def giveInstruction(serverNum,gpioIP,primaryServerIP):
    """
    This function checks if the server is the primary server. If so it will always be active. If the server is secundary
    it will set itself to inactive. All the data is gathered from the gpio pi and the web api and the parameters are
    obtained from the local file. A calculation is made based on the gathered data and the parameters. This calculation
    will result in an instruction for the gpio pi. The instruction is written to the local webserver. Afterwards a
    connection will be made with the database to write the gathered data to it.
    """
    if serverNum == 1:
        activity = "active"
    else:
        activity = serverCheck(primaryServerIP)
    waterHeight,gateStatus = gpioRequest(gpioIP)
    paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall = getParameters()
    buienradarAPI = httpRequests.buienradarApiCall()
    windSpeed = buienradarAPI["windsnelheidMS"]
    windDirection = buienradarAPI["windrichtingGR"]
    rainFall = buienradarAPI["regenMMPU"]
    buienradarAPI = None # clear variable
    if paramWaterHeight == "-": # check if the parameter should be disabled
        waterHeightBoolean = False
    else:
        waterHeightBoolean = waterHeight > paramWaterHeight
    if paramRainFall == "-": # check if parameter should be disabled
        rainFallBoolean = False
    else:
        rainFallBoolean = rainFall > paramRainFall
    windRange = range(paramWindDirection - 45, paramWindDirection + 45)
    windDirectionBoolean = windDirection in windRange
    if paramWindSpeed == "-": # check if the parameter should be disabled
        windSpeedBoolean = False
    else:
        windSpeedBoolean = windSpeed > paramWindSpeed
    if waterHeightBoolean | (windDirectionBoolean & windSpeedBoolean) | rainFallBoolean:
        instruction = "close"
    else:
        instruction = "open"
    writingJson.serverWriteJson(serverNum,activity,instruction,paramWaterHeight,paramWindDirection,paramWindSpeed,paramRainFall)
    if activity == "active":
        database.makeDatabaseConnection()
        database.insertIntoDatabase(gateStatus,waterHeight,windSpeed,windDirection,serverNum,rainFall)
        database.closeDatabaseConnection()
