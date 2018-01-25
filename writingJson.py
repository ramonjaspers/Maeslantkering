import json

def serverWriteJson(serverNumber, serverStatus, instruction, waterHeight, windDirection, windSpeed, rain):
    """
    This function takes some imputs to write to the JSON file on the webserver. The server number is a 1 or a 2. The
    server status is active or inactive. The instruction is what the gpio pi should do with the gate. The parameters
    are the criteria for the gate to open or close. waterHeight is the sensor at which it will close (25, 50 or 75).
    windDirection is the wind direction. windSpeed is the wind speed. rain is the amount of rain
    """
    toWrite = {"system":{"server":{"name":serverNumber,"status":serverStatus},"instruction":instruction,"parameters":
        {"waterHeight":waterHeight, "windDirection":windDirection, "windSpeed":windSpeed,"rain":rain}}}
    try:
        with open("/var/www/html/serverdata.json","w") as outfile:
            json.dump(toWrite,outfile)
        log = "Write Successful"
    except IOError:
        log = "Couldn't write to file"
    return log

def gpioWriteJson(sensor25,sensor50,sensor75,gateStatus):
    """
    This function takes the data from the sensors and the current status of the gate. This data is written to a json
    file on the webserver. The sensors return a 0 if they are touching water and a 1 if they aren't. The gateStatus is
    open/opening/close/closing.
    """
    toWrite = {"system":{"sensors":{"25":sensor25,"50":sensor50,"75":sensor75},"gateStatus":gateStatus}}
    try:
        with open("/var/www/html/gpiodata.json","w") as outfile:
            json.dump(toWrite,outfile)
        log = "Write Successful"
    except IOError:
        log = "Couldn't write to file"
    return log

#print(serverWriteJson("1","active","open","50","270","6","50")) # testline
#print(gpioWriteJson("0","1","1","open")) # testline