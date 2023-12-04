# ***** Create Table Scripts ***** #

createSensorEndpointTable = \
"""
CREATE TABLE IF NOT EXISTS sensorEndpoints (
    SENSORID    TEXT   PRIMARY KEY  NOT NULL    UNIQUE,
    IP          TEXT                NOT NULL    UNIQUE,
    PORTNUM     INT                 NOT NULL    UNIQUE
)
"""

# Primary key should be naturall autoincrementing
createSensorDataTable = \
"""
CREATE TABLE IF NOT EXISTS sensorData (
    ENTRYNO    INTEGER    PRIMARY KEY    AUTOINCREMENT,
    SENSORID   TEXT       NOT NULL,
    TEMP       REAL       NOT NULL,
    HUMIDITY   REAL       NOT NULL,
    PRESSURE   REAL       NOT NULL,
    FOREIGN KEY (SENSORID) REFERENCES sensorEndpoints(SENSORID)
)
"""

# ***** Sensor Endpoint Table Ops ***** #
insertSensorEndpoint = \
"""
INSERT INTO sensorEndpoints(SENSORID, IP, PORTNUM)
VALUES ('{0}', '{1}', '{2}')
"""

getSensorEndpoints = \
"""
SELECT SENSORID, IP, PORTNUM from sensorEndpoints
"""

deleteSensorEndpointByLocation = \
"""
DELETE FROM sensorEndpoints where SENSORID = '{0}'
"""

# ***** Sensor Data Table Ops ***** #
insertSensorDatapoint = \
"""
INSERT INTO sensorData(SENSORID, TEMP, HUMIDITY, PRESSURE)
VALUES ('{0}', '{1}', '{2}', '{3}'
)
"""

getSensorDatapointsByID = \
"""
SELECT * FROM sensorData WHERE SENSORID = '{0}'
"""