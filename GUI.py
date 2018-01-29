from tkinter import Tk, Canvas, PhotoImage, Label, SUNKEN, RAISED, Frame, Button, Scale, Checkbutton, IntVar, ttk
import random, time, threading
import urllib.request
import urllib.parse
import urllib.error
import json

#example api data
buienradarAPI = {
    '@id': '6344',
    'stationcode': '6344',
    'stationnaam': {'@regio': 'Rotterdam',
                    '#text': 'Meetstation Rotterdam'},
    'lat': '51.95',
    'lon': '4.45',
    'datum': '01/29/2018 13:10:00',
    'luchtvochtigheid': '76',
    'temperatuurGC': '10.5',
    'windsnelheidMS': '11.05',
    'windsnelheidBF': '6',
    'windrichtingGR': '232',
    'windrichting': 'ZW',
    'luchtdruk': '1022.84',
    'zichtmeters': '30100',
    'windstotenMS': '15.8',
    'regenMMPU': '100',
    'zonintensiteitWM2': '100',
    'icoonactueel': {'@ID': 'c', '@zin': 'Zwaar bewolkt',
                     '#text': 'https://www.buienradar.nl/resources/images/icons/weather/30x30/c.png'},
    'temperatuur10cm': '10.3',
    'url': 'http://www.buienradar.nl/nederland/weerbericht/weergrafieken/6344',
    'latGraden': '52.58',
    'lonGraden': '4.75',
    }

#function used in gui to write parameters to json file
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


#gui class
class Gui(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.pack()

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

        self.historyButton = Button(box, text='Historie', font=('Helvetica', 16), borderwidth=2)
        self.historyButton.place(x=890, y=800, height=90, width=345)

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
        self.windDirectionCheck = Checkbutton(box, variable=self.IntVarWindDirection)
        self.windDirectionCheck.place(x=1500, y=350)

        self.windSpeedSlider = Scale(box, from_=0, to=35, relief=RAISED)
        self.windSpeedSlider.place(x=1245, y=505, height=265)
        self.windSpeedCheck = Checkbutton(box, variable=self.IntVarWindSpeed)
        self.windSpeedCheck.place(x=1472, y=626)

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

    #function used to read config from the GUI and write to file
    def updateConfig(self):
        print('config updated')
        if self.IntVarWaterHeight.get() == 0:
            waterheightParameter = '-'
        else:
            waterheightParameter = self.waterLevelSlider.get()

        if self.IntVarWindDirection.get() == 0:
            windSpeedParameter = '-'
        else:
            windSpeedParameter = self.windSpeedSlider.get()

        if self.IntVarRainLevel.get() == 0:
            rainLevelParameter = '-'
        else:
            rainLevelParameter = self.rainLevelSlider.get()

        if self.IntVarWindDirection.get() == 0:
            windDirectionParameter = '-'
        else:
            windDirectionParameter = self.windDirectionSlider.get()

        writeParameters('params.json', windDirectionParameter, waterheightParameter, rainLevelParameter, windSpeedParameter)

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

    def updateGraph(self, list, canvas, type):
        self.drawGraph(self.updateYCoordList(list, type), canvas)
        canvas.after(2000, self.updateGraph, list, canvas, type)

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
        return 25


def runGui():
    global root, gui

    root = Tk()

    gui = Gui(root)
    gui.pack()

    gui.updateGraph(gui.waterLevelCoords, gui.waterLevelGraph, 'waterLevel')
    gui.updateGraph(gui.rainLevelCoords, gui.rainLevelGraph, 'rainLevel')
    gui.updateGraph(gui.windDirectionCoords, gui.windDirectionGraph, 'windDirection')
    gui.updateGraph(gui.windSpeedCoords, gui.windSpeedGraph, 'windSpeed')
    gui.updateStatusLabel(gui.statusLabel)
    root.mainloop()

def runOther():
    pass

runGui()


'''
t1 = threading.Thread(target=runGui)
t2 = threading.Thread(target=runOther)


t1.start()
t2.start()


t1.join()
t2.join()

'''