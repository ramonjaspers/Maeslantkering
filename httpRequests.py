import urllib.request
import urllib.parse
import urllib.error
import json

def getRequestJson(ip,fileName):
    """
    Return the data from a json file, requested from a local webserver running on another device. A url is formed from
    the webserver IP and the filename on the webserver. This url is used to request the file.
    """
    httpIP = "http://"+ip # create url
    url = urllib.parse.urljoin(httpIP,fileName)
    try:
        response = urllib.request.urlopen(url,None,4)
    except (TimeoutError,urllib.error.URLError):
        return "Timed out"
    contents = response.read()
    contents = "".join(map(chr, contents)) # convert binary to string
    jsonfile = json.loads(contents)
    return jsonfile

def buienradarApiCall():
    """
    Return the data obtained from the buienradar API. The function makes a request and finds the appropriate station.
    This uses a fair amount of memory as the entire json file is stored in memory and processed multiple times so some
    of the variables are reset to None after use.
    """
    try:
        response = urllib.request.urlopen("https://api.buienradar.nl/data/public/1.1/jsonfeed",None,4)
    except (TimeoutError,urllib.error.URLError):
        return "Timed out"
    contents = response.read()
    contents = "".join(map(chr, contents)) # convert binary to string
    response = None # Clear variable to save memory
    jsonfile = json.loads(contents)
    contents = None # Clear variable to save memory
    weerstations = jsonfile["buienradarnl"]["weergegevens"]["actueel_weer"]["weerstations"]["weerstation"]
    j=0
    for i in weerstations:
        if i["@id"] == "6344":
            break
        else:
            j += 1
    i,weerstations = None,None # Clear variable to save memory
    weersdata = jsonfile["buienradarnl"]["weergegevens"]["actueel_weer"]["weerstations"]["weerstation"][j]
    j,jsonfile = None,None # Clear variables to save memory
    return weersdata

#print(getRequestJson("http://192.168.42.4","serverdata.json"))
#print(buienradarApiCall())
