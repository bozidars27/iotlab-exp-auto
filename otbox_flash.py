import paho.mqtt.client as mqtt
import base64
import json
import re

CLIENT = 'exp-auto'

class OTBoxFlash:

	def __init__(self, firmware_path, broker, testbed):
		self.firmware_path = firmware_path
		self.broker        = broker
		self.testbed       = testbed

		self.client        = mqtt.Client(CLIENT)
		self.client.connect(self.broker)

	def get_motes(self):
		with open('nodes_eui64.log', 'r') as f:
			return f.read().split('\n')

	def is_eui64(self, mote):
		return re.match('([0-9a-f]{2}-){7}([0-9a-f]{2})\Z', mote) != None

	def flash(self):
		#{0}/deviceType/mote/deviceId/+/cmd/program

		topics = ['{0}/deviceType/mote/deviceId/{1}/cmd/program'.format(self.testbed, mote) for mote in self.get_motes() if self.is_eui64(mote)]

		with open(self.firmware_path) as f:
			data = f.read().replace('\n', '')
			payload = {
				'hex': base64.b64encode(data)
			}

			for topic in topics:
				self.client.publish(topic, json.dumps(payload))