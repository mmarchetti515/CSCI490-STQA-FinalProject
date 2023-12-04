# database shit
import sqlite3 as s3
import db.sqlStrings as sqlStr

# warning no error checking, might not handle sqllite errors but fuck it
class databaseInterface:
    def __init__(self):
        self._dbName = "data490.db"
        self._conn   = None

        self.__connect()
        self.__defineTableSetup()
        self.__disconnect()

    # **** Public methods **** #
    def insertEndpoint(self, id, ip, portnum, isactive):
        # add sensor endpoint to sensorEndpoints table
        self.__connect()
        if (portnum > 1023):
            self._conn.execute(sqlStr.insertSensorEndpoint.format(id, ip, portnum, isactive))

        self._conn.commit()
        
        self.__disconnect()

    def getEndpoints(self):
        # returns list of all endpotnis in sensorEndpoints table
        self.__connect()

        res = [] # will be an array of tuples

        # SELECT in this case returns a list of lists with each entry representing a sensor endpoint
        cursor = self._conn.execute(sqlStr.getSensorEndpoints)

        for endpoint in cursor:
            res.append(endpoint)

        self.__disconnect()

        # returns list of tuples: each tuple in list holds data about 1 sensor endpoint
        return res
    
    def deleteEndpointByLocation(self, location):
        self.__connect()

        self._conn.execute(sqlStr.deleteSensorEndpointByLocation.format(location))
        self._conn.commit()
        print(f"{self._conn.total_changes} rows deleted.")

        self.__disconnect()

    def addSensorData(self, id, temp, humidity, pressure):
        self.__connect()

        self._conn.execute(sqlStr.insertSensorDatapoint.format(id, temp, humidity, pressure))
        self._conn.commit()

        self.__disconnect()

    def getSensorDatapointsByID(self, id):
        self.__connect()

        res = []
        cursor = self._conn.execute(sqlStr.getSensorDatapointsByID.format(id))

        for datapoint in cursor:
            res.append(datapoint)
        
        self.__disconnect()

        # returns a list of tuples, each tuple holds a sensor data point pertaining to 'id'
        # 1st param in tuple: datapoint counter
        # 2nd param in tuple: sensorid/name
        # 3-5th params are: temp, humidity, pressure
        return res

    # **** Private methods **** #
    def __connect(self):
        # connect to existing db or create new one
        self._conn = s3.connect(self._dbName)
    
    def __disconnect(self):
        # close
        self._conn.close()
    
    def __defineTableSetup(self):
        # Create tables if they do not exist
        if (self._conn != None):
            self._conn.execute(sqlStr.createSensorEndpointTable)
            self._conn.execute(sqlStr.createSensorDataTable)

# usage: init databaseInterface object, creates database file: public methods simplify transactions
# x = databaseInterface()
# x.publicfunction(...)