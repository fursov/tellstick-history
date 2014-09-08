import os, sys
import MySQLdb
import MySQLdb.cursors

debug = 'true' in os.getenv('DEBUG', 'false').lower()

class SensorDB(object):
	def __init__(self, database = 'ha', user = 'ha', password = 'ha', maxEntries = 1024):
		self.db = MySQLdb.connect(user = user, passwd = password, db = database, cursorclass = MySQLdb.cursors.DictCursor)
		self.cursor = self.db.cursor()
		self.maxEntries = maxEntries
		query = "SHOW TABLES LIKE 'sensordata'"
		numOfTables = self.cursor.execute(query)
		if numOfTables == 0:
			query = "CREATE TABLE IF NOT EXISTS `sensordata` (`id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY, " + \
				"`sensor_id` INT, `temperature` FLOAT, `humidity` TINYINT, `timestamp` INT)"
			self.cursor.execute(query)
			self.db.commit()


	def __del__(self):
		self.cursor.close()
		self.db.close()


	def insertSensorData(self, id, temperature, humidity, timestamp):
		# Detect last entry for this sensor:
		# if data with same timestamp exists then discard the data
		query = "SELECT * FROM sensordata WHERE `sensor_id`='" + str(id) + "' ORDER BY `timestamp` ASC LIMIT 1"
		numOfEntries = self.cursor.execute(query)
		if (numOfEntries == 1):
			entry = self.cursor.fetchall()[0]
			if (timestamp == entry['timestamp']):
                                if debug:
					sys.stdout.write("Entry with same timestamp for same id exists, sensor: " + str(id) + "\n")
				return
		query = "INSERT INTO `sensordata`(`sensor_id`, `temperature`, `humidity`, `timestamp`) VALUES (" + \
			str(id)  + "," + str(temperature)  + "," + \
			str(humidity) + "," + str(timestamp)  + ")"
		self.cursor.execute(query)
		self.db.commit()
		
		query =  "SELECT * FROM sensordata WHERE `sensor_id`='" + str(id) + "' ORDER BY `timestamp` DESC"
		numOfEntries = self.cursor.execute(query)
		oldestEntry = self.cursor.fetchall()[0]
		if numOfEntries > self.maxEntries:
			query = "DELETE FROM `sensordata` WHERE `sensor_id`='" + str(oldestEntry['sensor_id']) + "' AND `timestamp`=" + str(oldestEntry['timestamp'])
			self.cursor.execute(query)
			self.db.commit()


	def getSensorHistory(self, id, fromTimestamp = 0, toTimestamp = 0):
		lowLimit = ''
		highLimit = ''
		if (fromTimestamp > 0):
			lowLimit = ' AND `timestamp`>' + str(fromTimestamp)
		if (toTimestamp > 0):
			highLimit = ' AND `timestamp`<' + str(toTimestamp)
                query = "SELECT * FROM sensordata WHERE `sensor_id`='" + str(id) + "'" + lowLimit + highLimit  + " ORDER BY `timestamp`"
                numOfEntries = self.cursor.execute(query)
                entries = self.cursor.fetchall()
		return entries
