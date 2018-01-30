from tkinter import Tk, Canvas, PhotoImage, Label, SUNKEN, RAISED, Frame, Button, Scale, Checkbutton, IntVar, Entry, Toplevel, Text
import random, time, threading

import httpRequests
from syncParameters import writeParameters
from httpRequests import buienradarApiCall
from serverFunctions import giveInstruction

def doApiCall():
    """ This function does the API call. It is separate so it can run asynchronous with the giveInstruction function"""
    global buienradarAPI
    while True:
        buienradarAPI = httpRequests.buienradarApiCall()
        time.sleep(600)

def validDateString(dateTimeString):
    try:
        time.strptime(dateTimeString, '%Y-%m-%d %H:%M')
        returnValue = True
    except:
        returnValue = False

    return returnValue


#gui class
class Gui(Frame):
    counter = 0
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

    def create_window(self, title, text):
        t = Toplevel(self)
        t.wm_title(title)
        i = Text(t, relief="flat", height=50, width=70)
        i.insert(1.0, text)
        i.config(state='disabled')
        print(text)
        i.pack()

    def showHistoryWindow(self):
        string = self.getHistoryString()
        self.create_window('Historie', string)

    def getHistoryString(self):
        self.startEntryString = self.historyStartEntry.get()
        self.endEntryString = self.historyEndEntry.get()
        returnValue = 'beginwaarde'

        if validDateString(self.startEntryString) == True:
            if validDateString(self.endEntryString) == True:
                if time.mktime(time.strptime(self.startEntryString, '%Y-%m-%d %H:%M')) <= time.mktime(time.strptime(self.endEntryString, '%Y-%m-%d %H:%M')):
                    returnValue = (self.startEntryString, self.endEntryString)
        else:
            returnValue = 'allemaal problemen'
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

    #function used to
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

    def updateGraph(self, list, canvas, type, miliseconds):
        self.drawGraph(self.updateYCoordList(list, type), canvas)
        canvas.after(miliseconds, self.updateGraph, list, canvas, type, miliseconds)

    def updateStatusLabel(self, label):
        label.configure(text=random.randint(0, 9))
        label.after(100, self.updateStatusLabel, label)

    def getRainLevelYCoord(self):
        rainLevel = buienradarAPI['regenMMPU']
        if rainLevel == '-':
            rainLevel = 0
        rainLevelY = int(float(rainLevel) * 1.388888888888889)
        return rainLevelY

    def getWindSpeedYCoord(self):
        windSpeed = buienradarAPI['windsnelheidMS']
        windSpeedY = int(float(windSpeed) * 5)
        return windSpeedY

    def getWindDirectionYCoord(self):
        windDirection = buienradarAPI['windrichtingGR']
        windDirectionY = int(float(windDirection) * 0.4)
        return windDirectionY

    def getWaterLevelYCoord(self):
        return 50


def runGui():
    global root, gui

    root = Tk()

    gui = Gui(root)
    gui.pack()

    gui.updateGraph(gui.waterLevelCoords, gui.waterLevelGraph, 'waterLevel', 1000)
    gui.updateGraph(gui.rainLevelCoords, gui.rainLevelGraph, 'rainLevel', 600000)
    gui.updateGraph(gui.windDirectionCoords, gui.windDirectionGraph, 'windDirection', 600000)
    gui.updateGraph(gui.windSpeedCoords, gui.windSpeedGraph, 'windSpeed', 600000)
    gui.updateStatusLabel(gui.statusLabel)
    root.mainloop()


buienradarAPI = buienradarApiCall()
print(type(buienradarAPI))


t1 = threading.Thread(target=doApiCall)

t2 = threading.Thread(target=giveInstruction, args=(1,"192.168.42.1"))

t3 = threading.Thread(target=runGui)


t1.start()
t2.start()
t3.start()


t1.join()
t2.join()
t3.join()
