import paho.mqtt.client as mqtt
import base64

CLIENT = 'exp-auto'

class OTBoxFlash:

	__init__(self, firmware_path, broker, testbed):
		self.firmware_path = firmware_path
		self.broker        = broker
		self.testbed       = testbed

		self.client        = mqtt.Client(CLIENT)
		self.client.connect(self.broker)

	def flash(self):
		#{0}/deviceType/mote/deviceId/+/cmd/program

		topic = '{0}/deviceType/mote/deviceId/+/cmd/program'.format(self.testbed)

		with fopen(self.firmware_path) as f:
			data = f.read().replace('\n', '')
			payload = {
				'hex': base64.b64encode(data)
			}

			self.client.publish(topic, json.dumps(payload))