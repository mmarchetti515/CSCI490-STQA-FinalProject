import customtkinter         as ctk
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
        self.dataView      =      viewdataHandler(self.tabView.tab("View Data"))

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
        self._removeSensorHeader        = None

        self._addSensorLabel            = None
        self._addSensorNameEntry        = None

        self._addSensorIPLabel          = None
        self._addSensorIPEntry          = None

        self._addSensorPortLabel        = None
        self._addSensorPortEntry        = None

        self._addSensorIsActiveLabel    = None
        self._addSensorIsActiveCheckBox = None

        self._addSensorButton           = None

        self.__setupFrame()
        # base frame sizing issues so create new frame in left side
        # _subframe setup and such
        self.__setupSubFrame()
        self.__createObjects()
        self.__drawObjects()

        # update sensor view list
        self.__updateSensorListView()

    # ***** Private functions ***** #
    def __createObjects(self):
        self._dataView = ctk.CTkTextbox(master = self.ct,
                                        width  = 1,
                                        height = 1,
                                        border_spacing = 20)
        
        self._addSensorHeader    = ctk.CTkLabel(master = self._subFrame,
                                                text   = "Add Sensor",
                                                font   = ("Inter", 12.5, "bold"))
        self._addSensorLabel     = ctk.CTkLabel(master = self._subFrame,
                                                text   = "Sensor Name:",
                                                font   = ("Inter", 12.5, "bold"))
        self._addSensorNameEntry = ctk.CTkEntry(master = self._subFrame,
                                                width  = 1,
                                                height = 25,
                                                border_width = 2)
        self._addSensorIPLabel   = ctk.CTkLabel(master = self._subFrame,
                                                text   = "Sensor IP:",
                                                font   = ("Inter", 12.5, "bold"))
        self._addSensorIPEntry   = ctk.CTkEntry(master = self._subFrame,
                                                width  = 1,
                                                height  = 25,
                                                border_width = 2)
        self._addSensorPortLabel = ctk.CTkLabel(master = self._subFrame,
                                                text   = "Sensor Port:",
                                                font   = ("Inter", 12.5, "bold"))
        self._addSensorPortEntry = ctk.CTkEntry(master = self._subFrame,
                                                width = 1,
                                                height = 25,
                                                border_width = 2)
        self._addSensorIsActiveLabel = ctk.CTkLabel(master = self._subFrame,
                                                    text   = "Is Active:",
                                                    font   = ("Inter", 12.5, "bold"))
        self._addSensorIsActiveCheckBox = ctk.CTkCheckBox(master = self._subFrame,
                                                          width  = 1,
                                                          height = 20,
                                                          border_width = 2,
                                                          onvalue=True,
                                                          offvalue=False)
        self._addSensorButton    = ctk.CTkButton(master = self._subFrame,
                                                 text   = "Add",
                                                 width       = 100,
                                                 height      = 30,
                                                 fg_color    = "#4E6AE7",
                                                 hover_color = "#3E55B9",
                                                 command     = self.__onAddSensorClick)

    def __drawObjects(self):
        self._dataView.grid(row = 1, column = 1, sticky = "nsew")

        # _subFrame 
        self._subFrame.grid(row = 1, column = 0, sticky = "nsew")

        self._addSensorHeader       .grid(row = 0, column = 0, sticky = "NSEW", padx = 10) 
        self._addSensorLabel        .grid(row = 1, column = 0, sticky = "NSW",  padx = 10)
        self._addSensorNameEntry    .grid(row = 2, column = 0, sticky = "NSEW", padx = 10, pady = (0,10))
        self._addSensorIPLabel      .grid(row = 3, column = 0, sticky = "NSW",  padx = 10)
        self._addSensorIPEntry      .grid(row = 4, column = 0, sticky = "NSEW", padx = 10, pady = (0,10))
        self._addSensorPortLabel    .grid(row = 5, column = 0, sticky = "NSW",  padx = 10)
        self._addSensorPortEntry    .grid(row = 6, column = 0, sticky = "NSEW", padx = 10, pady = (0,20))
        self._addSensorIsActiveLabel.grid(row = 7, column = 0, sticky = "NSW",  padx = 10)
        self._addSensorIsActiveCheckBox.grid(row = 8, column = 0, sticky = "NSEW", padx = 10, pady = (0,20)) # will have to check
        self._addSensorButton       .grid(row = 9, column = 0, sticky = "NS",   padx = 10)

    def __onAddSensorClick(self):
        sensorName     = self._addSensorNameEntry.get() 
        sensorIP       = self._addSensorIPEntry.get()
        sensorPort     = self._addSensorPortEntry.get()
        sensorIsActive = self._addSensorIsActiveCheckBox.get()

        if (sensorName != "" and sensorIP != "" and sensorPort != ""):
            sensorPort = int(sensorPort)
            self.db.insertEndpoint(sensorName, sensorIP, sensorPort, sensorIsActive)

        self.__updateSensorListView()

    def __setupFrame(self):
        self.ct.grid_rowconfigure((0,2), weight = 1, uniform = "letterbox")
        self.ct.grid_rowconfigure(    1, weight = 4)
        
        self.ct.grid_columnconfigure((0,1), weight = 1, uniform = "cvh")
    
    def __setupSubFrame(self):
        self._subFrame = ctk.CTkFrame(master = self.ct, fg_color = "transparent")
        self._subFrame.grid_columnconfigure((0,1), weight = 1, uniform = "sfc")
    
    def __updateSensorListView(self):
        self._dataView.delete("0.0", "end")
        self._dataView.insert("end", "Sensor List:\n------------\n")

        arr = self.db.getEndpoints()
        for i, ep in enumerate(arr):
            string = ""
            string += f"[{i+1}]     Name:{ep[0]}\t\tIP: {ep[1]}\t\tPort: {ep[2]}\t\tIsActive: {ep[3]}\n"
            self._dataView.insert("end", string)

class viewdataHandler:
    # takes viewData tab from tab view and treats it like a frame
    def __init__(self, viewDataTab):
        self.vd    = viewDataTab
        self._root = viewDataTab.master.master

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
            print("DEBUG: [Line 106]: utilsUI.py: class viewdataHandler] Thread: " + str(th.get_ident()))
            self.__getData()
            self._root.event_generate("<<threadEvent>>", when = "tail", state = 123)
            
            sleep(5)
            
    def __drawObjects(self):
        self._dataView       .grid(row = 0, column = 0, sticky = "nsew")
        self._startStopButton.grid(row = 1, column = 0, columnspan = 2)

    def __getData(self):
        self._startStopButton.configure(state = "disabled")
        print("DEBUG: [Line 117]: utilsUI.py: class viewdataHandler] Thread: " + str(th.get_ident()))
        x = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        x.connect(("192.168.1.38", 8000))
            
        x.send("get".encode("utf-8")[:1024])
        
        print("DEBUG: Waiting for data response...")
        sleep(1)
        response = x.recv(1024)
        print("DEBUG: Received message of length: " + str(len(response)))
        if (len(response) == 24):
            # little endian byte order + 3 doubles in byte stream
            unpackedData = struct.unpack("<3d", response)

            self._dataView.insert("end", "Read:\n")
            self._dataView.insert("end", "Temperature:  " + str(round(unpackedData[0], 2)) + " C\n")
            self._dataView.insert("end", "Rel. Humidity " + str(round(unpackedData[1], 2)) + " %\n")
            self._dataView.insert("end", "Presssure:    " + str(round(unpackedData[2], 2)) + " hPa\n\n")
            self._dataView.see("end")

        x.close()
        print("DEBUG: [Line 138]: utilsUI.py: class viewdataHandler] __getData() Done" )
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