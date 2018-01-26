import httpRequests
import writingJson
import readingJson
import syncParameters
import ping

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
    return syncParameters.syncParameters(serverIP,"serverdata.json","./parameters.json")

def getParameters():
    paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall = syncParameters.readParameters("./parameters.json")
    return paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall

def giveInstruction(serverNum,gpioIP,primaryServerIP):
    if serverNum == 1:
        activity = "active"
    else:
        activity = ping.ping(primaryServerIP)

    waterHeight,gateStatus = gpioRequest(gpioIP)
    paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall = getParameters()
    buienradarAPI = httpRequests.buienradarApiCall()
    windSpeed = buienradarAPI["windsnelheidMS"]
    windDirection = buienradarAPI["windrichtingGR"]
    rainFall = buienradarAPI["regenMMPU"]
    buienradarAPI = None # clear variable
    windRange = range(paramWindDirection-45,paramWindDirection+45)
    windDirectionBoolean = windDirection in windRange
    if waterHeight > paramWaterHeight | (windDirectionBoolean & windSpeed > paramWindSpeed) | rainFall > paramRainFall:
        instruction = "close"
    else:
        instruction = "open"
    return writingJson.serverWriteJson(serverNum,activity,instruction,paramWaterHeight,paramWindDirection,paramWindSpeed,paramRainFall)
