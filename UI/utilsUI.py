import customtkinter         as ctk
import CTkTable              as ctkT
from tkinter import messagebox
from tkinter import IntVar
from   db import dbInterface as db
import socket
import struct
import threading               as th
from   time                    import sleep

class tabFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs): 
        # init ctk frame
        super().__init__(master)

        self.db = db.databaseInterface()

        self.configureView     = None
        self.dataView          = None
        self.edgeProcessorView = None

        self.__setupWindow()
        self.__createObjects()
        self.__drawObjects()

    def __setupWindow(self):
        self.grid_rowconfigure   (0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

    def __createObjects(self):        
        self.tabView = ctk.CTkTabview(master = self)
        self.tabView.add("Configure")
        self.tabView.add("View Data")
        self.tabView.add("Edge Processor")

        self.configureView     =      configureviewHandler(self.tabView.tab("Configure"), self.db)
        self.dataView          =           viewdataHandler(self.tabView.tab("View Data"), self.db)
        self.edgeProcessorView =          edgeprocessorHandler(self.tabView.tab("Edge Processor"))

        self.tabView.configure(command = lambda: self.__tabCallback(self.tabView.get()))

    def __drawObjects(self):
        self.tabView.grid(row = 0, column = 0, sticky = "nsew", padx = 10, pady = (0, 10))

    def __tabCallback(self, n):
        if (n == "View Data"):
            self.dataView.refreshDataView() 

class configureviewHandler:
    def __init__(self, configureTab, dbObj):
        self.ct = configureTab

        # this class will be accessing the db
        self.db = dbObj

        # objects init
        self._dataView                  = None
        self._subFrame                  = None
        self._addSensorHeader           = None
        self._addSensorLabel            = None
        self._addSensorNameEntry        = None
        self._addSensorIPLabel          = None
        self._addSensorIPEntry          = None
        self._addSensorPortLabel        = None
        self._addSensorPortEntry        = None
        self._addSensorButton           = None

        self._removeSensorHeader        = None
        self._removeSensorLabel         = None
        self._removeSensorOptMenu       = None
        self._removeSensorButton        = None

        self.__setupFrame()
        # base frame sizing issues so create new frame in left side
        # _subframe setup and such
        self.__setupSubFrame()
        self.__createObjects()
        self.__drawObjects()

        # update sensor view list

        self.__updateDropdownMenu()

        self.numSensors = len(self.db.getEndpoints())
        self.__populateEndpointList()

    # ***** Private functions ***** #
    def __createObjects(self):
        self.value = [["Device Name", "IP Address", "Port"]]

        self._dataView          = ctkT.CTkTable(master = self.ct,
                                                column = 3,
                                                corner_radius=8,
                                                hover_color='#a8a8a8',
                                                color_phase="horizontal",
                                                colors=['#4a4a4a', '#737373'],
                                                header_color='#2b2b2b',
                                                values = self.value)

        # add sensor region 
        self._addSensorHeader    = ctk.CTkLabel(master = self._subFrame,
                                                text   = "Add Sensor",
                                                font   = ("Inter", 13, "bold"))
        self._addSensorLabel     = ctk.CTkLabel(master = self._subFrame,
                                                text   = "Sensor Name:",
                                                font   = ("Inter", 13, "bold"))
        self._addSensorNameEntry = ctk.CTkEntry(master = self._subFrame,
                                                width  = 1,
                                                height = 30,
                                                border_width = 2)
        self._addSensorIPLabel   = ctk.CTkLabel(master = self._subFrame,
                                                text   = "Sensor IP:",
                                                font   = ("Inter", 13, "bold"))
        self._addSensorIPEntry   = ctk.CTkEntry(master = self._subFrame,
                                                width  = 1,
                                                height  = 30,
                                                border_width = 2)
        self._addSensorPortLabel = ctk.CTkLabel(master = self._subFrame,
                                                text   = "Sensor Port:",
                                                font   = ("Inter", 13, "bold"))
        self._addSensorPortEntry = ctk.CTkEntry(master = self._subFrame,
                                                width = 1,
                                                height = 30,
                                                border_width = 2)

        self._addSensorButton    = ctk.CTkButton(master = self._subFrame,
                                                 text   = "Add",
                                                 width       = 100,
                                                 height      = 25,
                                                 fg_color    = "#4E6AE7",
                                                 hover_color = "#3E55B9",
                                                 command     = self.__onAddSensorClick)
        
        # remove sensor region
        self._removeSensorHeader = ctk.CTkLabel(master = self._subFrame,
                                                text   = "Remove Sensor",
                                                font   = ("Inter", 13, "bold"))
        self._removeSensorLabel  = ctk.CTkLabel(master = self._subFrame,
                                                text   = "Sensor Name:",
                                                font   = ("Inter", 13, "bold"))
        self._removeSensorOptMenu= ctk.CTkOptionMenu(master               = self._subFrame,
                                                     width                = 1,
                                                     height               = 30,
                                                     fg_color             = "#484a4c",
                                                     button_color         = "#2a2b2d",
                                                     button_hover_color   = "#3E55B9",
                                                     dropdown_fg_color    = "#484A4C",
                                                     dropdown_hover_color = "#3E55B9")
        self._removeSensorButton = ctk.CTkButton(master      = self._subFrame,
                                                 text        = "Remove",
                                                 width       = 100,
                                                 height      = 25,
                                                 fg_color    = "#4E6AE7",
                                                 hover_color = "#3E55B9",
                                                 command     = self.__onRemoveSensorClick)

    def __drawObjects(self):
        self._dataView.grid(row = 1, column = 1, sticky = "EW")

        # _subFrame 
        self._subFrame.grid(row = 1, column = 0, sticky = "nsew")

        self._addSensorHeader          .grid(row = 0, column = 0, sticky = "NSEW", padx = 20) 
        self._addSensorLabel           .grid(row = 1, column = 0, sticky = "NSW",  padx = 20)
        self._addSensorNameEntry       .grid(row = 2, column = 0, sticky = "NSEW", padx = 20, pady = (0,10))
        self._addSensorIPLabel         .grid(row = 3, column = 0, sticky = "NSW",  padx = 20)
        self._addSensorIPEntry         .grid(row = 4, column = 0, sticky = "NSEW", padx = 20, pady = (0,10))
        self._addSensorPortLabel       .grid(row = 5, column = 0, sticky = "NSW",  padx = 20)
        self._addSensorPortEntry       .grid(row = 6, column = 0, sticky = "NSEW", padx = 20, pady = (0,20))
        self._addSensorButton          .grid(row = 7, column = 0, sticky = "NS",   padx = 20)

        self._removeSensorHeader       .grid(row = 0, column = 1, sticky = "NSEW", padx = 20)
        self._removeSensorLabel        .grid(row = 1, column = 1, sticky = "NSW",  padx = 20)
        self._removeSensorOptMenu      .grid(row = 2, column = 1, sticky = "NSEW", padx = 20, pady = (0,10))
        self._removeSensorButton       .grid(row = 4, column = 1, sticky = "N",    padx = 20, rowspan = 1)

    def __onAddSensorClick(self):
        sensorName     = self._addSensorNameEntry.get() 
        sensorIP       = self._addSensorIPEntry.get()
        sensorPort     = self._addSensorPortEntry.get()
        
        # before adding a new row, verify that there won't be any clashes
        dupFound = self.__checkForDuplicateEntries(sensorName, sensorIP)
        if (sensorName != "" and sensorIP != "" and sensorPort != "" and dupFound == False):
            sensorPort = int(sensorPort)
            self.db.insertEndpoint(sensorName, sensorIP, sensorPort)
            self.__updateTableContents()
            self.__updateDropdownMenu()
        else:
            messagebox.showerror("Input Error", "Please enter valid values for the new device.")

    def __onRemoveSensorClick(self):
        self._oRSC_sensorName = self._removeSensorOptMenu.get()
        if self._oRSC_sensorName != "Select sensor...":
            self.db.deleteEndpointByLocation(self._oRSC_sensorName)
            self.__updateTableContents()
            self.__updateDropdownMenu()
        else:
            messagebox.showerror("Input Error", "Please select a device to be removed")

    def __populateEndpointList(self):
        if(self.numSensors > 0):
            res = self.db.getEndpoints()
            for index, endpoint in enumerate(res):
                    self._dataView.add_row([endpoint[0], endpoint[1], endpoint[2]], index+1)


    def __setupFrame(self):
        self.ct.grid_rowconfigure((0,2), weight = 1, uniform = "letterbox")
        self.ct.grid_rowconfigure(    1, weight = 2)
        
        self.ct.grid_columnconfigure((0,1), weight = 1, uniform = "cvh")
    
    def __setupSubFrame(self):
        self._subFrame = ctk.CTkFrame(master = self.ct, fg_color = "transparent")
        self._subFrame.grid_columnconfigure((0,1), weight = 1, uniform = "sfc")
    
    def __updateDropdownMenu(self):
        self._removeSensorOptMenu.set("Select sensor...")
        self._removeSensorOptMenu["borderwidth"] = 0
        res = []
        arr = self.db.getEndpoints()
        for ep in arr:
            res.append(ep[0])
        
        self._removeSensorOptMenu.configure(values = res)

    # completely new function for adding a device to the table
    def __updateTableContents(self):
        # clean the table
        if self.numSensors > 0:
            for i in range(1, self.numSensors+1):
                self._dataView.delete_row(i)
        # now that the table is clean, we can repopulate
        arr = self.db.getEndpoints()
        self.numSensors = len(arr)
        if self.numSensors > 0:
            for index, endpoint in enumerate(arr):
                self._dataView.add_row([endpoint[0], endpoint[1], endpoint[2]], index+1)

    def __checkForDuplicateEntries(self, deviceID, ipAddr):
        arr = self.db.getEndpoints()
        self.numSensors = len(arr)
        if self.numSensors > 0:
            for index, endpoint in enumerate(arr):
                if endpoint[0] == deviceID or endpoint[1] == ipAddr:
                    return True
                index+1
        return False

class viewdataHandler:
    # takes viewData tab from tab view and treats it like a frame
    def __init__(self, viewDataTab, dbObj):
        self.vd    = viewDataTab
        self._root = viewDataTab.master.master

        # this class will be accessing the db
        self.db = dbObj

        # "Prime" initial num of sensors in db
        self._numOfSensors = len(self.db.getEndpoints())

        self._dataView         = None
        self._startStopButton  = None
        self._intervalHEntry   = None
        self._pollingRateEntry = None

        # "Prime" the thread
        self._loopThread      = th.Thread(target = self.__dataLoop, daemon = True) 
        self._keepThreadAlive = False

        self._pollingInterval = 0 # Default: 60 seconds polling
        self._intervalHLength = 0 # Default: Average based on last 5 values

        self.__setupFrame()
        self.__createObjects()
        self.__drawObjects()
        self.__populateDataView()

    # clear list for redraw
    def refreshDataView(self):
        if (self._numOfSensors > 0):
            for rowNum in range(1, self._numOfSensors+1):
                try:
                    self._dataView.delete_row(rowNum)
                except: pass

        # get new list of sensors from db
        res = self.db.getEndpoints()
        self._numOfSensors = len(res)
        if (self._numOfSensors > 0):
            for index, endpoint in enumerate(res):
                self._dataView.add_row([endpoint[0], "N/A", "N/A", "N/A", "N/A"], index+1)

    # ***** Private functions ***** # 
    def __createObjects(self):
        self._dataView       = ctkT.CTkTable(master = self.vd,
                                             row    = 1,
                                             column = 4,
                                             corner_radius=8,
                                             hover_color='#a8a8a8',
                                             color_phase="horizontal",
                                             colors=['#4a4a4a', '#737373'],
                                             header_color='#2b2b2b',
                                             values = [["Sensor","Temp","Humidity","Pressure"]],
                                             font = ("Inter", 15, "bold"))
        
        self._pollingRateLabel  = ctk.CTkLabel(master       = self.vd,
                                              text         = "Polling Rate (s)",
                                              font         = ("Inter", 12.5, "bold"))
        self._pollingRateEntry = ctk.CTkEntry(master       = self.vd,
                                              width        = 200,
                                              height       = 30,
                                              border_width = 2,
                                              placeholder_text = "60")

        self._intervalHLabel   = ctk.CTkLabel(master       = self.vd,
                                              text         = "History Length (points)",
                                              font         = ("Inter", 12.5, "bold")) 
        self._intervalHEntry   = ctk.CTkEntry(master       = self.vd,
                                              width        = 200,
                                              height       = 30,
                                              border_width = 2,
                                              placeholder_text = "5")

        self._startStopButton = ctk.CTkButton (master      = self.vd,
                                               width       = 200,
                                               height      = 30,
                                               fg_color    = "#4E6AE7",
                                               hover_color = "#3E55B9",
                                               text        = "Start",
                                               command     = self.__onButtonClick)
        
    def __dataLoop(self):
        while (self._keepThreadAlive):
            print("DEBUG: [Line: utilsUI.py: class viewdataHandler] Thread: " + str(th.get_ident()))
            self.__getData() # debug disable for updating ui
            self.__updateView()
            self._root.event_generate("<<threadEvent>>", when = "tail", state = 123)

            sleep(self._pollingInterval)
            
    def __drawObjects(self):
        self._dataView       .grid(row = 0, column = 0, columnspan = 2, sticky = "EW", padx = 10 , pady = 20)

        self._pollingRateLabel.grid(row = 1, column = 0, sticky = "SE", padx = 20)
        self._pollingRateEntry.grid(row = 2, column = 0, sticky = "NE", padx = 20, pady = (0,10))
        self._intervalHLabel.  grid(row = 1, column = 1, sticky = "SW", padx = 20)
        self._intervalHEntry.  grid(row = 2, column = 1, sticky = "NW", padx = 20, pady = (0,10))

        self._startStopButton.grid(row = 3, column = 0, columnspan = 2)

    def __getData(self):
        # 1: Get array of endpoints
        self._startStopButton.configure(state = "disabled")
        print("DEBUG: __getData(): class viewdataHandler Thread: " + str(th.get_ident()))
        endpoints = self.db.getEndpoints()
        
        # ***** sub-functions ***** # 
        def pingEndpoint(id):
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect(socketTuple)

            clientSocket.send("get".encode("utf-8")[:1024])

            # wait a sec to get response, kind of relieves latency pressure
            sleep(1)

            response = clientSocket.recv(1024)

            if (len(response) == 24):
                # little endian byte order + 3 doubles in byte streams
                # [0]: Temp
                # [1]: Humidity
                # [2]: Pressure
                unpackedData = struct.unpack("<3d", response)
                
                # WIP WIP WIP display data here UI stuff WIP WIP WIP

            clientSocket.close()

            temp = round(unpackedData[0], 2) # C
            humi = round(unpackedData[1], 2) # rel hum %
            pres = round(unpackedData[2], 2) # hPa
            return [temp, humi, pres]
            

        # 2: We have our endpoints 
        for endpoint in endpoints:
            socketTuple = (endpoint[1], endpoint[2])
            id          =  endpoint[0] 
            arr = pingEndpoint(id)
            self.db.addSensorData(id, arr[0], arr[1], arr[2])

        self._startStopButton.configure(state = "normal")
    
    def __onButtonClick(self):
        if (self._startStopButton.cget("text") == "Start" and not self._loopThread.is_alive()): 
            if (self._intervalHEntry.get() == ""):
                self._intervalHLength = 5
            else:
                self._intervalHLength = int(self._intervalHEntry.get())

            if (self._pollingRateEntry.get() == ""):
                self._pollingInterval = 60
            else:
                self._pollingInterval = int(self._pollingRateEntry.get());
            
            self._startStopButton.configure(text = "Stop")
            self._keepThreadAlive = True
            self._loopThread.start()

        else:
            self._startStopButton.configure(state = "disabled", text = "Quitting...")
            self._root.update()
            self._keepThreadAlive = False

            print("DEBUG: Waiting for current sub-thread to finish...")
            self._loopThread.join()

            print("DEBUG: Resetting thread...")
            self.__resetThread()

            self._startStopButton.configure(state = "normal", text = "Start")

    def __populateDataView(self):
        if (self._numOfSensors > 0):
            # get new list of sensors from db
            res = self.db.getEndpoints()
            for index, endpoint in enumerate(res):
                self._dataView.add_row([endpoint[0], "N/A", "N/A", "N/A", "N/A"], index+1)

    def __resetThread(self): 
        self._loopThread = None
        self._loopThread = th.Thread(target = self.__dataLoop, daemon = True)  
    
    def __setupFrame(self):
        self.vd.grid_rowconfigure(0, weight = 5)
        self.vd.grid_rowconfigure(1, weight = 1)
        self.vd.grid_rowconfigure(2, weight = 1)
        self.vd.grid_rowconfigure(3, weight = 1)

        self.vd.grid_columnconfigure((0, 1), weight = 1)
    

    def __updateView(self):
        # By this point we have the number of sensors

        # How do we associate each data set organized by sensor ID 
        # in the ctkTable which has no general organization by nature
        #   - We know the number of sensors in the ctkTable,
        #   - So this gives us a number of indices to iterate through
        #   - Lib allows us to pull data per indices -> THIS will be our way to access our sensor ID <=> KEY
        #   - Our 'map' is [id,temp,humidity,pressure]
        for idx in range(1, self._numOfSensors+1):
            # get the (sensor ID/sensor Name/KEY)
            key = self._dataView.get_row(idx)[0]

            # request the data for the key
            # db api allows us to provide a threshold for how max most recent datapoints to request
            arr = self.db.getSensorDatapointsInOrderByID(key, self._intervalHLength)

            print(arr)

            # extract the data we want for the most recent datapoint
            temp    = arr[0][1:5]

            temp    = list(temp)
            temp[1] = "Current: " + str(temp[1]) + " C"
            temp[2] = "Current: " + str(temp[2]) + " %"
            temp[3] = "Current: " + str(temp[3]) + " hPa"

            tAvg = 0.0
            hAvg = 0.0
            pAvg = 0.0

            if (len(arr) < self._intervalHLength):
                for i in range(len(arr)):
                    tAvg += arr[i][2]
                    hAvg += arr[i][3]
                    pAvg += arr[i][4]

                tAvg = round(tAvg/len(arr), 2)
                hAvg = round(hAvg/len(arr), 2)
                pAvg = round(pAvg/len(arr), 2)
            
            elif (len(arr) >= self._intervalHLength):
                for i in range(0,self._intervalHLength):
                    tAvg += arr[i][2]
                    hAvg += arr[i][3]
                    pAvg += arr[i][4]

                tAvg = round(tAvg/self._intervalHLength, 2)
                hAvg = round(hAvg/self._intervalHLength, 2)
                pAvg = round(pAvg/self._intervalHLength, 2)

            temp[1] += "\nAvg: " + str(tAvg) + " C"
            temp[2] += "\nAvg: " + str(hAvg) + " %"
            temp[3] += "\nAvg: " + str(pAvg) + " hPa"

            self._dataView.edit_row(idx, temp)

class edgeprocessorHandler:
    # dbObj probably not even needed
    def __init__(self, edgeprocessorTab): 
        self.ept = edgeprocessorTab

        # objects init
        self._edgeDataView         = None
        self._subFrame             = None
        self._statChoiceListButton = None

        # radio button frame init
        self._statChoiceListSelection = IntVar(self.ept)

        # main setup on tab click
        self.__setupFrame()
        # base frame sizing issues so create new frame in left side
        # _subframe setup and such
        self.__setupSubFrame()
        self.__createObjects()
        self.__drawObjects()

    def __createObjects(self):
        # init values
        self._tableHeaders = [["Device Name", "Temperature", "Humidity", "Pressure"]]
        self._guideBoxText = "Help text\nUse the tools on this page to pull values computed by the edge processors gathered over a period of 5 minutes. You may choose to compute the 5 minute avergae, 5 minute high, or the 5 minute low. This reduces strain on the local system and does not use the database."

        self._edgeDataView         = ctkT.CTkTable(master = self.ept,
                                                   column = 3,
                                                   corner_radius=8,
                                                   hover_color='#a8a8a8',
                                                   color_phase="horizontal",
                                                   colors=['#4a4a4a', '#737373'],
                                                   header_color='#2b2b2b',
                                                   values = self._tableHeaders)
        
        self._addGuideBox          = ctk.CTkTextbox(master = self.ept,
                                                    corner_radius= 8,
                                                    width=400,
                                                    wrap='word',
                                                    font = ("Inter", 13),
                                                    height = 200)

        # Radio button group
        self.radiobutton_frame     = ctk.CTkFrame(master = self.ept)

        self._radioButton_1        = ctk.CTkRadioButton(master=self.radiobutton_frame,
                                                        variable=self._statChoiceListSelection,
                                                        text="Average",
                                                        value=1)
        
        self._radioButton_2        = ctk.CTkRadioButton(master=self.radiobutton_frame,
                                                        variable=self._statChoiceListSelection,
                                                        text="High", 
                                                        value=2)
        
        self._radioButton_3        = ctk.CTkRadioButton(master=self.radiobutton_frame,
                                                        variable=self._statChoiceListSelection,
                                                        text="Low", 
                                                        value=3)
        
        self._statChoiceListButton = ctk.CTkButton(master=self.ept,
                                                   text="Request",
                                                   width=100,
                                                   height=25,
                                                   fg_color="#4E6AE7",
                                                   hover_color="#3E55B9",
                                                   command=self.__onstatChoiceListClick)
        
    def __drawObjects(self):
        self._edgeDataView.grid(row = 1, column = 1, sticky = "NE")

        # _subFrame 
        self._subFrame.grid(row = 1, column = 0, sticky = "nsew")

        self._addGuideBox.grid(row = 1, column = 0, sticky = "NSEW", padx = 20)
        
        # Radio button group
        self.radiobutton_frame.grid(row=1, column=3, padx=(20, 20), pady=(20, 20), sticky="sew")
        self._radioButton_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")
        self._radioButton_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")
        self._radioButton_3.grid(row=3, column=2, pady=10, padx=20, sticky="n")

        self._statChoiceListButton.grid(row = 2, column = 3, sticky = "N", padx = 20)

        # populate the user guide text
        self.__populateGuideBox()

    def __setupFrame(self):
        self.ept.grid_rowconfigure((0,2), weight = 1, uniform = "letterbox")
        self.ept.grid_rowconfigure(    1, weight = 1)
        
        self.ept.grid_columnconfigure((0,1), weight = 1, uniform = "cvh")

    def __setupSubFrame(self):
        self._subFrame = ctk.CTkFrame(master = self.ept, fg_color = "transparent")
        self._subFrame.grid_columnconfigure((0,1), weight = 1, uniform = "sfc")

    def __populateGuideBox(self):
        self._addGuideBox.insert("0.0", self._guideBoxText)

    def __onstatChoiceListClick(self):
        if self._statChoiceListSelection != 0:
            print("you selected a value", self._statChoiceListSelection)
        else:
            print("something happened oh no uwu", self._statChoiceListSelection)