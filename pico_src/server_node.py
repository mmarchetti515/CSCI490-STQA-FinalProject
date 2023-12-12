# imports
from   bme680   import *
from   machine  import SPI, I2C, Pin
import queue as Queue
import time
import network
import socket 
import machine
import struct
import htmlStrings as hS
import re
import uasyncio

class i2cComm:
    def __init__(self):
        # Data
        self.temp     = 0.0 # celsius
        self.humidity = 0.0 # rh %
        self.pressure = 0.0 # hPa

        # GPIO Pin defines for I2C
        self.sckPin = Pin(17)
        self.sdaPin = Pin(16)

        # I2C interfacea
        self.i2cObject = I2C(0,
                             scl = self.sckPin,
                             sda = self.sdaPin)

        # BME 680 Interface using I2C
        self.bme680I2CObject = BME680_I2C(self.i2cObject)

    def returnData(self):
        self.__getData()
        print("returnData: DEBUG\ntemp = {x}\nhumidity = {y}\npressure = {z}".format(x=self.temp, y = self.humidity, z = self.pressure))
        return [self.temp, self.humidity, self.pressure]

    def __getData(self):
        self.temp     = round(self.bme680I2CObject.temperature, 2)
        self.humidity = round(self.bme680I2CObject.humidity,    2)
        self.pressure = round(self.bme680I2CObject.pressure,    2)

class spiComm:
    def __init__(self):
        # Data
        self.temp     = 0.0 # celsius
        self.humidity = 0.0 # rh %
        self.pressure = 0.0 # hectoPascals

        # GPIO Pin defines for SPI
        self. rxPin  = Pin(19)                            
        self. csPin  = Pin(17, mode = Pin.OUT, value = 1) 
        self.sckPin  = Pin(18)                            
        self. txPin  = Pin(16)                            
        
        # SPI interface
        self.spiObject = SPI(0, 
                             baudrate = 1000*1000, 
                             sck      = self.sckPin, 
                             mosi     = self.rxPin,
                             miso     = self.txPin) 

        # BME680 Interface using SPI
        self.bme680SPIObject = BME680_SPI(self.spiObject, self.csPin)

        # ====== structures for history + historical data retrieval ====== #
        self._temperatureHistory = Queue(maxsize = 5)
        self._humidityHistory    = Queue(maxsize = 5)
        self._pressureHistory    = Queue(maxsize = 5)
        
        self._temperatureAvg     = 0
        self._humidityAvg        = 0
        self._pressureAvg        = 0

        self._temperatureHigh    = 0
        self._humidityHigh       = 0
        self._pressureHigh       = 0

        self._temperatureLow     = 0
        self._humidityLow        = 0
        self._pressureLow        = 0

        self.histCorruptMsg = "History data corrupted, clearing all history..."
        self.histEmptyMsg   = "History data not available, please wait and try again..."

        # we can safely assume that a pico and sensor would likely not be used under such conditions 
        self._curHighTmp         = -9999
        self._curLowTmp          = -9999
        self._curHighHum         = -9999
        self._curLowHum          = -9999
        self._curHighPrs         = -9999
        self._curLowPrs          = -9999

    def returnData(self):
        self._getData()
        print("returnData: DEBUG\ntemp = {x}\nhumidity = {y}\npressure = {z}".format(x=self.temp, y = self.humidity, z = self.pressure))
        return [self.temp, self.humidity, self.pressure]

    def _saveToHistory(self):
        _getData()

        # == save to temperature history == #

        # pop the oldest data point from the queue
        if self._temperatureHistory.full():
            self._temperatureHistory.get()
        # check if new high or low
        if self.temp > curTmpHigh or curTmpHigh == -9999:
            curTmpHigh = self.temp
        if self.temp < curTmpLow or curTmpLow == -9999:
            curTmpLow = self.temp
        self._temperatureHistory.put(self.temp)


        # == save to humidity history == #

        # pop the oldest data point from the queue
        if self._humidityHistory.full():
            self._humidityHistory.get()
        # check if new high or low
        if self.humidity > curHumHigh or curHumHigh == -9999:
            curHumHigh = self.humidity
        if self.humidity < curHumLow or curHumLow == -9999:
            curhumLow = self.humidity
        self._humidityHistory.put(self.humidity)

        # == save to pressure history == #

        # pop the oldest data point from the queue
        if self._pressureHistory.full():
            self._pressureHistory.get()
        # check if new high or low
        if self.pressure > curPrsHigh or curPrsHigh == -9999:
            curTmpHigh = self.pressure
        if self.pressure < curPrsLow or curPrsLow == -9999:
            curPrsLow = self.pressure
        self._pressureHistory.put(self.pressure)

    def _getAvgsFromHistory(self):
        tempHistSize = self._temperatureHistory.qsize()
        humHistSize  = self._humidityHistory.qsize()
        presHistSize = self._pressureHistory.qsize()
        # Ensure that all queues are of equal size. If they are not, there has been some corruption
        # in the data gathering process
        if tempHistSize == humHistSize == presHistSize:
            numVals = tempHistSize
            tmpAvg = (sum(self._temperatureHistory)) / numVals
            humAvg = (sum(self._humidityHistory))    / numVals
            prsAvg = (sum(self._pressureHistory))    / numVals
            return [tmpAvg, humAvg, prsAvg]
        # queues haven't been filled yet
        elif {tempHistSize, humHistSize, presHistSize} == 0:
            print(self.histEmptyMsg)
            return -1
        # corruption has occurred
        else:
            print(self.histCorruptMsg)
            return -1

    def _getHighsFromHistory(self):
        tempHistSize = self._temperatureHistory.qsize()
        humHistSize  = self._humidityHistory.qsize()
        presHistSize = self._pressureHistory.qsize()
        # Ensure that all queues are of equal size. If they are not, there has been some corruption
        # in the data gathering process
        if tempHistSize == humHistSize == presHistSize:
            return [self.curTmpHigh, self.curHumHigh, self.curPrsHigh]
        # queues haven't been filled yet
        elif {tempHistSize, humHistSize, presHistSize} == 0:
            print(self.histEmptyMsg)
            return -1
        # corruption has occurred
        else:
            print(self.histCorruptMsg)
            return -1
            
    def _getLowsFromHistory(self):
        tempHistSize = self._temperatureHistory.qsize()
        humHistSize  = self._humidityHistory.qsize()
        presHistSize = self._pressureHistory.qsize()
        # Ensure that all queues are of equal size. If they are not, there has been some corruption
        # in the data gathering process
        if tempHistSize == humHistSize == presHistSize:
            return [self.curTmpLow, self.curHumLow, self.curPrsLow]
        # queues haven't been filled yet
        elif {tempHistSize, humHistSize, presHistSize} == 0:
            print(self.histEmptyMsg)
            return -1
        # corruption has occurred
        else:
            print(self.histCorruptMsg)
            return -1

    # private
    def _getData(self):
        self.temp     = round(self.bme680SPIObject.temperature, 2)
        self.humidity = round(self.bme680SPIObject.humidity,    2)
        self.pressure = round(self.bme680SPIObject.pressure,    2)

class wifiManagerServer:
    def __init__(self):
        self._picoConfigSSID       = "PICO_AP"
        self._picoConfigPass       = "password"
        self._picoConfigAuthMode   = 2
        self._ap_if                = network.WLAN(network.AP_IF)  # network config for host node usage
        self._wlan                 = network.WLAN(network.STA_IF) # network configfor searching
        self._picoConfigServerSock = socket.socket()

        self.serverIP              = ""
        
        self._numberOfConnections  = 0

        self.__setup()

    def run(self):
        self.__run()
        return self.serverIP

    # ***** Private + some helpers ***** #
    def __attemptConnection(self, _ssid, _password):
        attempts = 0
        print("Attempting connection to WIFI")
        self._wlan.active(True)
        print(_ssid, _password)
        self._wlan.connect(_ssid, _password)
        while (self._wlan.isconnected() == False and attempts < 30):
            attempts += 1
            print("Attempting to connect to WIFI")
            time.sleep_ms(1000)

        if (self._wlan.isconnected() == False):
            print("Failed to connect")
            return False

        print("Success")
        return True

    def __extractSSIDandPass(self, pageReq):
        print(pageReq)
        pageReq = self.__urldecode(pageReq)

        ssidP = "=.*&"
        passP = "&.*"

        ssid  = re.search(ssidP, pageReq).group(0)[1:-1].replace("+", " ")
        passw = re.search(passP, pageReq).group(0).split("=")[1]

        return ssid, passw

    def __run(self):
        # bind, listen on port 80, serve ice cream
        self._picoConfigServerSock.bind(('', 80)) # bind on pub host and well known port
        self._picoConfigServerSock.listen(0) # ONE CLIENT!

        while (1):
            # check for connection status
            if (self._wlan.isconnected()):
                # We no longer need the access point object to be enabled: exit function
                self._ap_if.active(False)
                self.serverIP = self._wlan.ifconfig()[0]
                return True

            # otherwise inf loop
            print("Waiting for client to make a request...")
            clientSock, clientAddress = self._picoConfigServerSock.accept()
            # debug
            self._numberOfConnections += 1
            print(self._numberOfConnections)
            print(f"{clientAddress} made a request...\n")

            # ensure request from browser is complete -> looking for byte string \r\n\r\n
            browserRequest = b""

            # look for request end and ensure full request, http ends with bytes \r\n\r\n
            print("DEBUG: Receiving data from client browser...")
            while (not re.search(b"\r\n\r\n", browserRequest)):
                buffer = clientSock.recv(64) # 128 byte chunks
                browserRequest += buffer
                print(f"DEBUG: {len(buffer)} bytes received...")

            # find out what client wants
            pageReq = self.__parseRequest(browserRequest)

            # http headers
            clientSock.send("HTTP/1.1 200 OK\n")
            clientSock.send("Content-Type: text/html\n")
            clientSock.send("\n")
            
            # index/home page of sorts
            if (pageReq == "/"):
                clientSock.send(hS.wifiHTMLStart.encode("utf-8"))
                
                # get potential access points
                self._wlan.active(True)
                possiblePointsRaw = self._wlan.scan()
                possiblePoints  = [] # could contain duplicates: nature of .scan()
                possiblePointsF = [] # no duplicates

                possiblePoints  = [p[0].decode("utf-8") for p in possiblePointsRaw if p[0].decode("utf-8") != ""]
                [possiblePointsF.append(i) for i in possiblePoints if (i not in possiblePointsF)]

                for p in possiblePointsF:
                    clientSock.send(f"<option value='{p}'>{p}</option>".encode("utf-8"))
                
                clientSock.send(hS.wifiHTMLEnd.encode("utf-8"))
                self._wlan.active(False)

            # user should have entered data to connect to a hotspot, must check
            elif (re.search("/connect", pageReq)):
                ssid, password = self.__extractSSIDandPass(pageReq)
                succ = hS.wifiConnectSuccessHTML.encode("utf-8").format(x = ssid)
                fail = hS.wifiConnectFailedHTML. encode("utf-8").format(x = ssid)
                res = self.__attemptConnection(ssid, password)

                print(res)

                if (res):
                    clientSock.sendall(succ)
                    time.sleep(1)
                else:
                    clientSock.sendall(fail)

            else:
                pass # for now -> 404 stuff I think

            # done for now, client was served the appropriate page, loop will restart accepting a new request
            clientSock.close()
    
    def __parseRequest(self, request):
        requestArray = request.split(b"\n")
        requestArray = requestArray[0].decode("utf-8").split(" ")
        return requestArray[1]

    def __setup(self): 
        # Configure access point ssid and password for other devices, no accesss to cyw43 c HAL stuck in WPA2
        self._ap_if.config(essid = self._picoConfigSSID, password = self._picoConfigPass)
        self._ap_if.active(True)
        self._wlan.active(True)

        # Wait while ap is configuring itself, takes a bit
        while (self._ap_if.active() == False):
            print("Pico W AP is configuring, one moment...")
            time.sleep_ms(500)

        # syslog
        AP_Addr = self._ap_if.ifconfig()[0] # static IP of 192.168.4.1
        print(f"Please connect to {AP_Addr} to configure WIFI")

    def __urldecode(self,str):
        # url decoding not supported on micropython, adapted from micropython-libs
        dic = {"%21":"!","%22":'"',"%23":"#","%24":"$","%26":"&","%27":"'","%28":"(","%29":")","%2A":"*","%2B":"+","%2C":",","%2F":"/","%3A":":","%3B":";","%3D":"=","%3F":"?","%40":"@","%5B":"[","%5D":"]","%7B":"{","%7D":"}"}
        for k,v in dic.items(): 
            str = str.replace(k,v)
        return str 


class serverNode:
    def __init__(self, serverIP):
        self._packetSize            = 24           # number of bytes packet size should be -> 3 doubles (8 bytes each) = 24 total bytes
        self._dIP                   = ""           # lchost created by connecting to wi-fi, alt: use 127.0.0.1 for lchost
        self._localServerSocketInfo = ()           # contains 
        self._socketPort            = 8000         # avoid cross port < 1023
        self._serverIP              = serverIP
        self._spiObject             = spiComm()    # spi interface comm
        #self._i2cObject             = i2cComm()    # i2c interface comm

    def runServer(self):
        self.__mainLoop()

    # ***** Private Methods ***** #
    def __createClientInstanceSocket(self):
        print("Waiting for a client...")
        clientSocket, clientAddress = self._serverSocket.accept()
        print(f"Accepted client connection from {clientAddress[0]}:{clientAddress[1]}")
        return clientSocket, clientAddress
    
    def __createServerSocket(self):
        self._localServerSocketInfo = (self._serverIP, self._socketPort)
        self._serverSocket          = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._serverSocket.           setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
        self._serverSocket.           bind(self._localServerSocketInfo)
        self._serverSocket.           listen(0)

        print(f"Server listening on {self._serverIP}:{self._socketPort}")

    async def __gatherData(self):
        while true:
            # num seconds between data gather
            interval = 10
            print("data being gathered - current interval... ", interval)
            # sleep for designated interval
            await uasyncio.sleep(interval)

    def __mainLoop(self):
        # init parent server socket to wait for new client connections: retains overall server life
        self.__createServerSocket()

        # retain server socket -> renew client socket type beat
        while (True):
            # begin gathering data 
            await self.__gatherData()

            # wait for a client to request
            clientSocket, clientAddress = self.__createClientInstanceSocket()

            print("Waiting for request...")
            request = clientSocket.recv(1024)  # get data from client
            request = request.decode("utf-8")  # get data from clientrequest.decode("utf-8")

            if (request.lower() == "get"):
                print("get request received: retrieving sensor readings...")
                sensorArrayData = self._spiObject.returnData()
                #sensorArrayData = self._i2cObject.returnData()

                # testing phase for encoding/decoding
                # data size: each floating point no./double = 8 bytes
                #   - 3 double = 24 bytes
                # struct args: (< : little endian byte order, 3 : number of items, d : type of items, double in this case)
                # struct serializes the data based on these args and organizes a standard protocol packet size
                print("sending data...")
                packedData = struct.pack("<3d", *sensorArrayData)
                clientSocket.send(packedData)

                # close socket so it doesn't stay open for no reason
                print("resetting...\n---------\n")
                clientSocket.close()

            elif (request.lower() == "hih"):
                print("hih (high) request received: retrieving sensor readings...")
                sensorArrayData1 = self._spiObject._getHighsFromHistory()
                print("sending data...")
                packedData1 = struct.pack("<3d", *sensorArrayData1)
                clientSocket.send(packedData1)

                # close socket so it doesn't stay open for no reason
                print("resetting...\n---------\n")
                clientSocket.close()

            elif (request.lower() == "avg"):
                print("avg request received: retrieving sensor readings...")
                sensorArrayData2 = self._spiObject._getAvgsFromHistory()
                print("sending data...")
                packedData2 = struct.pack("<3d", *sensorArrayData2)
                clientSocket.send(packedData2)

                # close socket so it doesn't stay open for no reason
                print("resetting...\n---------\n")
                clientSocket.close()

            elif (request.lower() == "low"):
                print("low request received: retrieving sensor readings...")
                sensorArrayData3 = self._spiObject._getLowsFromHistory()
                print("sending data...")
                packedData3 = struct.pack("<3d", *sensorArrayData3)
                clientSocket.send(packedData3)

                # close socket so it doesn't stay open for no reason
                print("resetting...\n---------\n")
                clientSocket.close()

def main():
    wifi = wifiManagerServer()
    serverIP = wifi.run()

    s = serverNode(serverIP)
    s.runServer()

if __name__ == "__main__":
    uasyncio.run(main())