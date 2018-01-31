from httpRequests import getRequestJson
import urllib.error

def gpioReadServerJson(httpIP1,httpIP2,fileName):
    """
    This function is run on the gpio pi and processes the json file that is obtained from the webserver. The httpIP1 is
    the IP of the primary server. httpIP2 is the IP of the secundary. It checks if the server is active, if so it will
    follow its instructions.
    """
    try:
        jsonfile1 = getRequestJson(httpIP1,fileName)
        jsonfile2 = getRequestJson(httpIP2,fileName)
        if jsonfile2["system"]["server"]["status"] == "active":
            instruction = jsonfile2["system"]["instruction"]
        elif jsonfile1["system"]["server"]["status"] == "active":
            instruction = jsonfile1["system"]["instruction"]
        else:
            print("No instructions could be obtained")
            instruction = "open"
    except urllib.error.URLError:
        print("No instructions could be obtained")
        instruction = "open"
    return instruction

def serverReadGpioJson(httpIP,fileName):
    """
    This function is run on the server. It requests the json file from the gpio pi and processes the contents.
    The function returns a tuple containing the waterHeight integer and gateStatus.
    """
    jsonfile = getRequestJson(httpIP,fileName)
    waterHeight = 0
    gateStatus = "open"
    try:
        print("sensordata right after obtaining values:")
        print(jsonfile["system"]["sensors"]["75"])
        print(jsonfile["system"]["sensors"]["50"])
        print(jsonfile["system"]["sensors"]["25"])
        if jsonfile["system"]["sensors"]["75"] == "0":
            waterHeight = 75
        elif jsonfile["system"]["sensors"]["50"] == "0":
            waterHeight = 50
        elif jsonfile["system"]["sensors"]["25"] == "0":
            waterHeight = 25
        else:
            waterHeight = 0
        gateStatus = jsonfile["system"]["gateStatus"]
    except TypeError:
        print("No gpio json file could be obtained, returning default height and status.")
    print("Water Height after processing:",str(waterHeight))
    print("Gate status after processing:",gateStatus)
    return waterHeight,gateStatus

def syncReadServerJson(httpIP,fileName):
    """
    This function takes an IP and checks if the parameters can be synced.
    The function returns the wind direction parameter, the wind speed parameter, the water height parameter and the
    rainfall parameter. It is returned in a tuple in the order listed above.
    """
    try:
        jsonfile = getRequestJson(httpIP,fileName)
        paramWindDirection = str(jsonfile["system"]["parameters"]["windDirection"])
        paramWindSpeed = str(jsonfile["system"]["parameters"]["windSpeed"])
        paramWaterHeight = str(jsonfile["system"]["parameters"]["waterHeight"])
        paramRainFall = str(jsonfile["system"]["parameters"]["rain"])
        return paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall
    except (urllib.error.URLError,TypeError):
        return "Unable to connect"

#print(serverReadGpioJson("http://192.168.42.4","gpiodata.json"))
#print(syncReadServerJson("http://192.168.42.4","serverdata.json"))
