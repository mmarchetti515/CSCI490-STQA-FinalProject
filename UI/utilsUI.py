import customtkinter         as ctk
import CTkTable              as ctkT
from   db import dbInterface as db
import socket
import struct
import threading             as th
from   time                  import sleep

class tabFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs): 
        # init ctk frame
        super().__init__(master)

        self.db = db.databaseInterface()

        self.configureView = None
        self.dataView      = None

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

        self.configureView = configureviewHandler(self.tabView.tab("Configure"), self.db)
        self.dataView      =      viewdataHandler(self.tabView.tab("View Data"), self.db)

    def __drawObjects(self):
        self.tabView.grid(row = 0, column = 0, sticky = "nsew", padx = 10, pady = (0, 10))

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

        self.__updateSensorListView("add")
        self.__updateDropdownMenu()

    # ***** Private functions ***** #
    def __createObjects(self):
        self.value = [["Device Name",
                       "IP Address",
                       "Port"
                       ]]
        arr = self.db.getEndpoints()
        yo = []
        for ep in arr:
            buff = []
            for x in range(3):
                buff.append(ep[x])
            self.value.append(buff)

        """ self._dataView = ctk.CTkTextbox(master = self.ct,
                                        width  = 1,
                                        height = 1,
                                        border_spacing = 20) """
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
                                                 hover_color = "#3E55B9")

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

        if (sensorName != "" and sensorIP != "" and sensorPort != ""):
            sensorPort = int(sensorPort)
            self.db.insertEndpoint(sensorName, sensorIP, sensorPort)

        self.__updateSensorListView("add")
        self.__updateDropdownMenu()

    def __setupFrame(self):
        self.ct.grid_rowconfigure((0,2), weight = 1, uniform = "letterbox")
        self.ct.grid_rowconfigure(    1, weight = 1)
        
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

    def __updateSensorListView(self, updateType):
        if updateType == "add":
            arr = self.db.getEndpoints()
            newRow = []
            for ep in arr:
                buff = []
                for x in range(3):
                    buff.append(ep[x])
                newRow = buff
                self.value.append(buff)
            print(self.value)
            rowCtr = len(self.value)
            self._dataView.add_row(newRow)
        if updateType == "delete":
            print("delete stuff")

class viewdataHandler:
    # takes viewData tab from tab view and treats it like a frame
    def __init__(self, viewDataTab, dbObj):
        self.vd    = viewDataTab
        self._root = viewDataTab.master.master

        # this class will be accessing the db
        self.db = dbObj

        self._dataView        = None
        self._startStopButton = None

        # Threading
        self._loopThread      = th.Thread(target = self.__dataLoop, daemon = True) 
        self._keepThreadAlive = False
        
        self.__setupFrame()
        self.__createObjects()
        self.__drawObjects()

    # ***** Private functions ***** # 
    def __createObjects(self):
        self._dataView        = ctk.CTkTextbox(master     = self.vd)

        self._startStopButton = ctk.CTkButton (master      = self.vd,
                                               width       = 150,
                                               height      = 30,
                                               fg_color    = "#4E6AE7",
                                               hover_color = "#3E55B9",
                                               text        = "Start",
                                               command     = self.__onButtonClick)
        
    def __dataLoop(self):
        while (self._keepThreadAlive):
            print("DEBUG: [Line: utilsUI.py: class viewdataHandler] Thread: " + str(th.get_ident()))
            self.__getData()
            self._root.event_generate("<<threadEvent>>", when = "tail", state = 123)
            
            sleep(5)
            
    def __drawObjects(self):
        self._dataView       .grid(row = 0, column = 0, sticky = "nsew", padx = 10 , pady = 20)
        self._startStopButton.grid(row = 1, column = 0, columnspan = 2)

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
                string = ""
                string += f"{id}\t"

                self._dataView.insert("end", f"Data from {id}:\n")
                self._dataView.insert("end", "Temperature:   " + str(round(unpackedData[0], 2)) + " C\n")
                self._dataView.insert("end", "Rel. Humidity: " + str(round(unpackedData[1], 2)) + " %\n")
                self._dataView.insert("end", "Presssure:     " + str(round(unpackedData[2], 2)) + " hPa\n\n")
                self._dataView.see("end")

            clientSocket.close()

        # 2: We have our endpoints 
        for endpoint in endpoints:
            socketTuple = (endpoint[1], endpoint[2])
            pingEndpoint(endpoint[0])
        self._startStopButton.configure(state = "normal")
    
    def __onButtonClick(self):
        if (self._startStopButton.cget("text") == "Start" and not self._loopThread.is_alive()): 
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

    def __resetThread(self): 
        self._loopThread = None
        self._loopThread = th.Thread(target = self.__dataLoop, daemon = True)  
    
    def __setupFrame(self):
        self.vd.grid_rowconfigure(0, weight = 5)
        self.vd.grid_rowconfigure(1, weight = 1)

        self.vd.grid_columnconfigure(0, weight = 1, uniform = "data")
        self.vd.grid_columnconfigure(1, weight = 1, uniform = "data")