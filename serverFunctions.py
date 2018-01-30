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