import customtkinter as ctk
import threading as th # debugging
import UI.utilsUI as utilsUI

class gui(ctk.CTk):
    # main gui root class
    def __init__(self):
        # init ctk
        super().__init__()
        print("[Line 10: mainUI.py: class gui] Main thread: " + str(th.get_ident()))

        self.__setupWindow()
        self.__createBaseFrame()

        self.bind("<<threadEvent>>", self.__eventHandler)

    # ***** Private functions ***** #
    def __createBaseFrame(self):
        self.thisTab = utilsUI.tabFrame(master = self)
        self.thisTab.grid(row = 0, column = 0, sticky = "nsew")

    def __eventHandler(self, e):
        # update gui
        self.after(500)

    def __setupWindow(self):
        # var
        x = 1280; y = 720

        self.title          ("Sensor Aggregation")
        self.geometry                 (f"{x}x{y}")
        self.minsize                         (x,y)
        self.grid_rowconfigure   ((0), weight = 1)
        self.grid_columnconfigure((0), weight = 1)