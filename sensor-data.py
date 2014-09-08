#!/usr/bin/env python

import os, sys, time
from daemon import Daemon
from tellcore.telldus import TelldusCore, SensorValue
import tellcore.constants as const
from sensordb import SensorDB

debug = 'true' in os.getenv('DEBUG', 'false').lower()

class SensorData(Daemon):
	def run(self):
		core = TelldusCore()
		sensorDb = SensorDB(database = 'ha', user = 'ha', password = 'ha')
		while True:
			listOfSensors = core.sensors()
			timestamp = 0
			for sensor in listOfSensors:
				if debug:
					sys.stdout.write("Found sensor: " + str(sensor.id) + "\n")
				if sensor.has_temperature():
					if debug:
						sys.stdout.write("... sensor supports temperature\n")
					sensorTemperature = sensor.temperature()
					timestamp = sensorTemperature.timestamp
				else:
					if debug:
						sys.stdout.write(".. sensor does not support temperature\n")
					sensorTemperature = SensorValue(const.TELLSTICK_TEMPERATURE, -100.0, 0)
				if sensor.has_humidity():
					if debug:
						sys.stdout.write("... sensor supports humidity\n")
					sensorHumidity = sensor.humidity()
					timestamp = sensorHumidity.timestamp
				else:
					if debug:
						sys.stdout.write(".. sensor does not support humidity\n")
					sensorTemperature = SensorValue(const.TELLSTICK_HUMIDITY, 0, 0)
				if timestamp > 0:
					if sensor.id > 0:
						sensorDb.insertSensorData(sensor.id, sensorTemperature.value, sensorHumidity.value, timestamp)
					else:
						if debug:
							sys.stdout.write("E: sensor id is not in allowed range\n")
				else:
					if debug:
						sys.stdout.write("Not able to setup timestamp for sensor values\n")
				if debug:
					sys.stdout.flush()
			time.sleep(300)

if __name__ == "__main__":
	daemon = SensorData('/tmp/sensor-data.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
