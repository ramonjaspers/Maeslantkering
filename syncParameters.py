import json
from readingJson import syncReadServerJson
import urllib.error

def writeParameters(paramFile,paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall):
    """
    This function will take the parameters obtained from the other server and save them to a local file
    """
    try:
        with open(paramFile,"w") as outfile:
            toWrite = {"parameters":{"windDirection":paramWindDirection,"windSpeed":paramWindSpeed,"waterHeight":
                                     paramWaterHeight,"rainFall":paramRainFall}}
            json.dump(toWrite,outfile)
            return "Write successful"
    except IOError:
        return "Unable to write"

def readParameters(paramFile):
    """
    This function will read the contents of the local parameter file and process them into a tuple.
    """
    with open(paramFile,"r") as infile:
        contents = infile.read()
    jsonfile = json.loads(contents)
    paramWindDirection = jsonfile["parameters"]["windDirection"]
    paramWindSpeed = jsonfile["parameters"]["windSpeed"]
    paramWaterHeight = jsonfile["parameters"]["waterHeight"]
    paramRainFall = jsonfile["parameters"]["rain"]
    return paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall


def syncParameters(httpIP,fileName,paramFile):
    """
    Try to connect to the other server if a connection is established it will accept those parameters. When a
    connection is not established the server will look in a local file for the latest saved parameters. When these
    are not available the system will take default parameters. The parameters are returned in a tuple.
    """
    try:                                # try to get the json file from the other server
        if syncReadServerJson(httpIP,fileName) == "Unable to connect":
            raise urllib.error.URLError("Unable to conect")
        paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall = syncReadServerJson(httpIP,fileName)
        print(writeParameters(paramFile,paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall))
        return paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall
    except (urllib.error.URLError):       # if the url doesn't exist
        try:                            # try reading from local file
            paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall = readParameters(paramFile)
            return paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall
        except IOError:                 # if local file doesn't exist
            print("Take default parameters")
            paramWindDirection = "270"
            paramWindSpeed = "20"
            paramWaterHeight = "50"
            paramRainFall = "150"
            print(writeParameters(paramFile, paramWindDirection, paramWindSpeed, paramWaterHeight, paramRainFall))
            return paramWindDirection, paramWindSpeed, paramWaterHeight, paramRainFall

print(syncParameters("http://192.168.42.2","serverdata.json","./parameters.json"))
