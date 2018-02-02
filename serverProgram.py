from tkinter import Tk, Canvas, PhotoImage, Label, SUNKEN, RAISED, Frame, Button, Scale, Checkbutton, IntVar, Entry, Toplevel, Text
import random, time, threading, mysql.connector.errors

import writingJson, database, httpRequests, serverFunctions, readingJson
from ping import ping
from syncParameters import writeParameters
from httpRequests import buienradarApiCall

def doApiCall():
    """ This function does the API call. It is separate so it can run asynchronous with the giveInstruction function"""
    global buienradarAPI
    while True:
        buienradarAPI = httpRequests.buienradarApiCall()
        try:
            time.sleep(600)
        except KeyboardInterrupt: # catch keyboard interrupts
            print("Stopped")
            break

# These functions should be run in the main program
def giveInstruction(serverNum,primaryServerIP,secundaryServerIP):
    """
    This function checks if the server is the primary server. If so it will always be active. If the server is secundary
    it will set itself to inactive. All the data is gathered from the gpio pi and the web api and the parameters are
    obtained from the local file. A calculation is made based on the gathered data and the parameters. This calculation
    will result in an instruction for the gpio pi. The instruction is written to the local webserver. Afterwards a
    connection will be made with the database to write the gathered data to it.
    """
    global buienradarAPI  # set buienradarAPI to be global variable
    # on the secundary server sync parameters with primary
    if serverNum == 2:
        if ping(primaryServerIP) == "Online":
            serverFunctions.synchroniseParameters(primaryServerIP)
    # on the primary server sync parameters with the secundary
    elif serverNum == 1:
        if ping (secundaryServerIP) == "Online":
            serverFunctions.synchroniseParameters(secundaryServerIP)
    while True: # loop until the program gets interrupted
        if serverNum == 1:
            activity = "active" # primary server is always active
        elif serverNum == 2: # sync parameters if the server is inactive
            activity = serverFunctions.serverCheck(primaryServerIP)
            if activity == "active":
                print("server active")
            elif activity == "inactive":
                print("server inactive")
                serverFunctions.synchroniseParameters(primaryServerIP)
        waterHeight,gateStatus = serverFunctions.gpioRequest() # request gpio data
        paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall = serverFunctions.getParameters() # get parms
        # print parameters obtained obtained by this function
        print("Main obtained parameters: ",paramWindDirection,paramWindSpeed,paramWaterHeight,paramRainFall)
        while True: # wait for API call if call is not yet made
            try:
                print(buienradarAPI) # try to print buienradarAPI (raises exception if its None)
                break
            except (NameError,ValueError,TypeError):
                print("API call not yet made")
                time.sleep(1)
                continue
        # get data from API (API call is made asynchronous on another thread, see function doApiCall())
        windSpeed = buienradarAPI["windsnelheidMS"]
        windDirection = buienradarAPI["windrichtingGR"]
        rainFall = buienradarAPI["regenMMPU"]
        if paramWaterHeight == "-": # check if the parameter should be disabled
            waterHeightBoolean = False
        else:
            waterHeightBoolean = int(waterHeight) >= int(paramWaterHeight)
        if paramRainFall == "-": # check if parameter should be disabled
            rainFallBoolean = False
        else:
            if rainFall == "-":
                rainFall = 0
            rainFallBoolean = float(rainFall) >= int(paramRainFall)
        # set up a boolean for wind data to be in range with parameters
        windRange = range(int(paramWindDirection) - 45, int(paramWindDirection) + 45)
        windDirectionBoolean = int(windDirection) in windRange
        if paramWindSpeed == "-": # check if the parameter should be disabled
            windSpeedBoolean = False
        else:
            windSpeedBoolean = float(windSpeed) >= int(paramWindSpeed)
        # give instruction
        if waterHeightBoolean | (windDirectionBoolean & windSpeedBoolean) | rainFallBoolean:
            instruction = "close"
        else:
            instruction = "open"
        # write instruction to webserver
        writingJson.serverWriteJson(serverNum,activity,instruction,paramWaterHeight,paramWindDirection,paramWindSpeed,paramRainFall)
        # save data to database if server is active server
        if activity == "active":
            try:
                database.makeDatabaseConnection()
                database.insertIntoDatabase(gateStatus,waterHeight,windSpeed,windDirection,serverNum,rainFall)
                database.closeDatabaseConnection()
            except (TimeoutError,mysql.connector.errors.InterfaceError): # except connection errors
                print("Could not connect to database")
        try: # catch keyboard interrupts
            time.sleep(10)
        except KeyboardInterrupt:
            print("Stopped")
            break

def validDateString(dateTimeString):
    try:
        time.strptime(dateTimeString, '%Y-%m-%d %H:%M')
        returnValue = True
    except:
        returnValue = False

    return returnValue


#gui class
class Gui(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        self.pack()
        global buienradarAPI

        #define master variables (geometry and background)
        master.geometry('{}x{}'.format(1600, 900))
        master.resizable(width=False, height=False)

        master.filename = PhotoImage(file="achtergrond.png")
        master.background_label = Label(master, image=master.filename)
        master.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        #define variables needed to get information from checkboxes in the gui
        self.IntVarWaterHeight = IntVar()
        self.IntVarRainLevel = IntVar()
        self.IntVarWindDirection = IntVar()
        self.IntVarWindSpeed = IntVar()

        #define graph dimensions
        self.graphHeight = 178
        self.graphWidth = 698
        self.startYvar = self.graphHeight + 2
        self.startYvar = self.graphHeight + 2
        self.waterLevelCoords = [0, 0, 0, 0, 0, 0, 0, 0]
        self.rainLevelCoords = [0, 0, 0, 0, 0, 0, 0, 0]
        self.windDirectionCoords = [0, 0, 0, 0, 0, 0, 0, 0]
        self.windSpeedCoords = [0, 0, 0, 0, 0, 0, 0, 0]
        self.keringStatus = 'OPEN'

        #define frame for gui
        box = Frame(master, relief=SUNKEN, borderwidth=2).pack()
        #define gui elements (graphs, buttons, checkboxes, sliders)
        self.waterLevelGraph = Canvas(box, height=self.graphHeight, width=self.graphWidth, relief=SUNKEN, borderwidth=1)
        self.waterLevelGraph.place(x=10, y=30)

        self.rainLevelGraph = Canvas(box, height=self.graphHeight, width=self.graphWidth, relief=SUNKEN, borderwidth=1)
        self.rainLevelGraph.place(x=10, y=250)

        self.windDirectionGraph = Canvas(box, height=self.graphHeight, width=self.graphWidth, relief=SUNKEN, borderwidth=1)
        self.windDirectionGraph.place(x=10, y=470)

        self.windSpeedGraph = Canvas(box, height=self.graphHeight, width=self.graphWidth, relief=SUNKEN, borderwidth=1)
        self.windSpeedGraph.place(x=10, y=690)

        self.statusLabel = Label(box, text=self.keringStatus, font=('Helvetica', 16), relief=SUNKEN, borderwidth=5)
        self.statusLabel.place(x=890, y=50, width=700, height=100)

        self.exitButton = Button(box, text='Afsluiten', font=('Helvetica', 16), command=exit, borderwidth=2)
        self.exitButton.place(x=1245, y=800, height=90, width=345)

        self.historyButton = Button(box, text='Historie', font=('Helvetica', 16), borderwidth=2, command=lambda:self.showHistoryWindow())
        self.historyButton.place(x=890, y=800, height=40, width=345)

        self.historyStartEntry = Entry(box, borderwidth=2)
        self.historyStartEntry.insert(0,'jjjj-mm-dd uu:mm')
        self.historyStartEntry.place(x=890, y=850, height=40, width=170)

        self.historyEndEntry = Entry(box, borderwidth=2)
        self.historyEndEntry.insert(0,'jjjj-mm-dd uu:mm')
        self.historyEndEntry.place(x=1065, y=850, height=40, width=170)

        self.waterLevelSlider = Scale(box, from_=0, to=75, resolution=25, relief=RAISED)
        self.waterLevelSlider.place(x=910, y=230, height = 265)
        self.waterLevelCheck = Checkbutton(box, variable=self.IntVarWaterHeight)
        self.waterLevelCheck.place(x=1120, y=350)

        self.rainLevelSlider = Scale(box, from_=0, to=250, resolution=10, relief=RAISED)
        self.rainLevelSlider.place(x=910, y=505, height=265)
        self.rainLevelCheck = Checkbutton(box, variable=self.IntVarRainLevel)
        self.rainLevelCheck.place(x=1140, y=626)

        self.windDirectionSlider = Scale(box, from_=0, to=350, resolution=10, relief=RAISED)
        self.windDirectionSlider.place(x=1245, y=230, height=265)

        self.windSpeedSlider = Scale(box, from_=0, to=35, relief=RAISED)
        self.windSpeedSlider.place(x=1245, y=505, height=265)
        self.windSpeedCheck = Checkbutton(box, variable=self.IntVarWindSpeed)
        self.windSpeedCheck.place(x=1505, y=485)

        self.applyConfigButton = Button(box, text='toepassen', font=('Helvetica', 16), command=self.updateConfig)
        self.applyConfigButton.place(x=1462, y=180, height=30, width=117)

    #function used to test checkboxes
    def getConfig(self):
        waterHeightConfigCheck =  self.IntVarWaterHeight.get()
        rainLevelConfigCheck = self.IntVarRainLevel.get()
        windDirectionConfigCheck = self.IntVarWindDirection.get()
        windSpeedConfigCheck = self.IntVarWindSpeed.get()
        checksList = []
        checksList.append(waterHeightConfigCheck)
        checksList.append(rainLevelConfigCheck)
        checksList.append(windDirectionConfigCheck)
        checksList.append(windSpeedConfigCheck)
        return checksList

    #function use to create window with title and text as argument
    def create_window(self, title, text):
        t = Toplevel(self)
        t.wm_title(title)
        i = Text(t, relief="flat", height=50, width=93)
        i.insert(1.0, text)
        i.config(state='disabled')
        print(text)
        i.pack()

    #function used to show the historywindow
    def showHistoryWindow(self):
        string = self.getHistoryString()
        self.create_window('Historie', string)

    #function used to format the data from the database into a string for the database
    def getHistoryWindowTextString(self, data):
        formatString = '| {:17}| {:9}| {:12}| {:11}| {:13}| {:7}| {:9}|'
        string = ''
        titles = formatString.format('Tijd', 'Status', 'Waterstand', 'Windkracht', 'Windrichting', 'Server', 'Neerslag')
        string += titles + '\n'

        for item in data:
            string += formatString.format(data[data.index(item)]['Tijd'], data[data.index(item)]['Status'],
                                          str(data[data.index(item)]['Waterstand']),
                                          str(data[data.index(item)]['Windkracht']),
                                          str(data[data.index(item)]['Windrichting']),
                                          str(data[data.index(item)]['Instantie']),
                                          str(data[data.index(item)]['Neerslag'])) + '\n'

        return string

    #function used to generate the textstring for the history window
    def getHistoryString(self):
        self.startEntryString = self.historyStartEntry.get()
        self.endEntryString = self.historyEndEntry.get()
        returnValue = 'beginwaarde'

        if validDateString(self.startEntryString) == True:
            if validDateString(self.endEntryString) == True:
                if time.mktime(time.strptime(self.startEntryString, '%Y-%m-%d %H:%M')) < time.mktime(time.strptime(self.endEntryString, '%Y-%m-%d %H:%M')):
                    dateTuple = (self.startEntryString, self.endEntryString)
                    historyData = database.getHistory(dateTuple)
                    returnValue = self.getHistoryWindowTextString(historyData)

                else:
                    returnValue = 'Begintijd gelijk aan of later dan eindtijd'
                    print(validDateString(self.endEntryString))
            else:

                returnValue = 'Eindtijd onjuist'
        else:
            returnValue = 'Begintijd onjuist'
        print('functie doorlopen')
        print(returnValue)
        return returnValue


    #function used to read config from the GUI and write to file
    def updateConfig(self):
        print('config updated')
        if self.IntVarWaterHeight.get() == 0:
            waterheightParameter = '-'
        else:
            waterheightParameter = self.waterLevelSlider.get()

        if self.IntVarWindSpeed.get() == 0:
            windSpeedParameter = '-'
        else:
            windSpeedParameter = self.windSpeedSlider.get()

        if self.IntVarRainLevel.get() == 0:
            rainLevelParameter = '-'
        else:
            rainLevelParameter = self.rainLevelSlider.get()

        windDirectionParameter = self.windDirectionSlider.get()

        writeParameters('./parameters.json', windDirectionParameter,windSpeedParameter,  waterheightParameter,rainLevelParameter)

    #function used to update the list with y-coordinates for the tkinter canvaess
    def updateYCoordList(self, list, type):
        if type == 'rainLevel':
            list.append(self.getRainLevelYCoord())
            list.remove(list[0])

        elif type == 'waterLevel':
            list.append(self.getWaterLevelYCoord())
            list.remove(list[0])

        elif type == 'windDirection':
            list.append(self.getWindDirectionYCoord())
            list.remove(list[0])

        elif type == 'windSpeed':
            list.append(self.getWindSpeedYCoord())
            list.remove(list[0])

        else:
            list.append(36)
            list.remove(list[0])
        return list

    #function used to draw a graph using tkinter canvas module with a list of y-coordinates and a canvas as arguments
    def drawGraph(self, list, canvas):
        canvas.delete('all')
        startX = 0
        for index in range(len(list) - 1):
            startY = self.startYvar - list[index]
            try:
                endY = self.startYvar - list[index + 1]
            except:
                print('error')
                pass
            endX = startX + 100
            canvas.create_line(startX, startY, endX, endY)
            startX += 100

    #function used to update graph with graph type and update interval as arguments
    def updateGraph(self, list, canvas, type, miliseconds):
        self.drawGraph(self.updateYCoordList(list, type), canvas)
        canvas.after(miliseconds, self.updateGraph, list, canvas, type, miliseconds)

    #function used to update statuslabel ever quarter of a second
    def updateStatusLabel(self, label):
        text = self.getKeringStatus()
        label.configure(text=text)
        label.after(250, self.updateStatusLabel, label)

    #function used to get the status of the kering from the gpio system
    def getKeringStatus(self):
        try:
            data = serverFunctions.gpioRequest()
            statusString = 'status:' + data[1]
            return statusString
        except:
            return 'ERROR'


    #function used to generate y-coordinate for rainFall
    def getRainLevelYCoord(self):
        rainLevel = buienradarAPI['regenMMPU']
        if rainLevel == '-':
            rainLevel = 0
        rainLevelY = int(float(rainLevel) * 1.388888888888889)
        return rainLevelY

    #function used to generate y-coordinate for wind speed
    def getWindSpeedYCoord(self):
        windSpeed = buienradarAPI['windsnelheidMS']
        windSpeedY = int(float(windSpeed) * 5)
        return windSpeedY

    #function used to generate y-coordinate for wind direction
    def getWindDirectionYCoord(self):
        windDirection = buienradarAPI['windrichtingGR']
        windDirectionY = int(float(windDirection) * 0.4)
        return windDirectionY

    #function used to generate y-coordinate for water level
    def getWaterLevelYCoord(self):
        data = serverFunctions.gpioRequest()
        return data[0]*2

#function used to run the gui loop.
def runGui():
    global root, gui

    root = Tk()

    gui = Gui(root)
    gui.pack()

    gui.updateGraph(gui.waterLevelCoords, gui.waterLevelGraph, 'waterLevel', 10000)
    gui.updateGraph(gui.rainLevelCoords, gui.rainLevelGraph, 'rainLevel', 600000)
    gui.updateGraph(gui.windDirectionCoords, gui.windDirectionGraph, 'windDirection', 600000)
    gui.updateGraph(gui.windSpeedCoords, gui.windSpeedGraph, 'windSpeed', 600000)
    gui.updateStatusLabel(gui.statusLabel)
    root.mainloop()


buienradarAPI = buienradarApiCall()
print(type(buienradarAPI))


t1 = threading.Thread(target=doApiCall)
t2 = threading.Thread(target=giveInstruction, args=(1,"192.168.42.1","192.168.42.4"))
t3 = threading.Thread(target=runGui)


t1.start()
t2.start()
t3.start()


t1.join()
t2.join()
t3.join()
