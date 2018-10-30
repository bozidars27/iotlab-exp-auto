import paramiko
import json
import subprocess
import time
import threading
import paho.mqtt.client as mqtt
import os

from socket_io_handler import SocketIoHandler
from reservation import Reservation

class OTBoxStartup:

	CMD_ERROR                = "cmd_error"
	SSH_RETRY_TIME           = 600
	RETRY_PAUSE              =   6
	MQTT_PAUSE               =   1 
	EUI64_RETREIVAL_TIMEOUT  =  10

	CLIENT                   = "OpenBenchmark"
	
	eui_retreival_started    = False


	def __init__(self, user, domain, broker, testbed):
		self.user            = user
		self.domain          = domain
		self.testbed         = testbed
		self.broker          = broker

		self.socketIoHandler = SocketIoHandler()

		self.client          = paramiko.SSHClient()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.client.load_system_host_keys()

		self.mqttclient      = mqtt.Client(self.CLIENT)

		self.mqttclient.on_connect = self.on_connect
		self.mqttclient.on_subscribe = self.on_subscribe
		self.mqttclient.on_message = self.on_message

		self.ssh_connect()

		self.booted_nodes    = []
		self.active_nodes    = []

		self.reservation     = Reservation(user, domain)
		self.nodes           = self.reservation.get_reserved_nodes(True)
		
        # Fetch the latest version of opentestbed software in the shared A8 director of the SSH frontend
		self.ssh_command_exec('cd A8; rm -rf opentestbed; git clone https://github.com/bozidars27/opentestbed.git; cd opentestbed; git checkout origin/opentestbed-extension;')


	def ssh_connect(self):
		self.client.connect(self.domain, username=self.user)

	def ssh_disconnect(self):
		self.client.close()

	def ssh_command_exec(self, command):
		try:
			stdin, stdout, stderr = self.client.exec_command(command)
			stdin.close()

			output = []
			for line in stdout.read().splitlines():
				output.append(line)

			error = []
			for line in stderr.read().splitlines():
				error.append(line)

			if len(error) > 0:
				raise Exception(self.CMD_ERROR)

			return ''.join(output)

		except:
			return self.CMD_ERROR


	def boot_wait(self):
		for ind, node in enumerate(self.nodes):

			node_name = 'node-' + node.split('.')[0]
			print("Probing node: " + node_name)

			retries = 0
			num_of_retries = self.SSH_RETRY_TIME / self.RETRY_PAUSE

			while True:
				try:
					boot_op = self.ssh_command_exec('ssh -o "StrictHostKeyChecking no" root@' + node_name + ' "cd A8;"')
				except:
					print 'Error executing command: ssh -o "StrictHostKeyChecking no" root@' + node_name

				if boot_op == self.CMD_ERROR and retries <= num_of_retries:
					print("Node " + node_name + ": retrying")
					self.socketIoHandler.publish('BOOT_RETRY', node_name + ": " + str(retries) + "/" + str(num_of_retries))
					retries += 1
					time.sleep(self.RETRY_PAUSE)
				elif retries > num_of_retries:
					self.socketIoHandler.publish('BOOT_FAIL', node_name)
					break
				else:
					self.socketIoHandler.publish('NODE_BOOTED', node_name)
					self.booted_nodes.append(node)
					break

	def on_connect(self, client, userdata, flags, rc):
		print "Connected to broker: {0}".format(self.broker)
		client.subscribe('{0}/deviceType/box/deviceId/+/resp/status'.format(self.testbed))

	def on_message(self, client, userdata, message):
		try:
			payload = json.loads(message.payload)
			eui64   = payload['returnVal']['motes'][0]['EUI64']
			print("Received message: {0}".format(eui64))
			with open('nodes_eui64.log', 'a') as f:
				f.write(eui64 + "\n")

			self.eui_retreival_started = True
		
		except Exception, e:
			print("An exception occured: {0}".format(str(e)))


	def on_subscribe(self, mosq, obj, mid, granted_qos):
		print("Subscribed: " + str(mid) + " " + str(granted_qos))

		time.sleep(self.MQTT_PAUSE)

		payload_status = {
			'token':       123,
		}
		# publish the cmd message
		self.mqttclient.publish(
			topic   = '{0}/deviceType/box/deviceId/all/cmd/status'.format(self.testbed),
			payload = json.dumps(payload_status),
		)



	def start(self):
		print("OTBox startup commencing...")
		self.boot_wait()

		try:
			for ind, node in enumerate(self.booted_nodes):
				node_name = 'node-' + node.split('.')[0]
				print("Starting otbox.py on " + node_name + "...")
                                self.ssh_command_exec('ssh -o "StrictHostKeyChecking no" root@' + node_name + ' "source /etc/profile; cd A8; cd opentestbed; pip install requests; python otbox.py --testbed=iotlab --broker=broker.mqttdashboard.com >& otbox-' + node_name + '.log &"')
				self.active_nodes.append(node)
				self.socketIoHandler.publish('NODE_ACTIVE', node_name)
		except:
			self.socketIoHandler.publish('NODE_ACTIVE_FAIL', node_name)
			print("Exception happened!")


	def get_eui64(self):
		print "Getting EUI64 addresses"

		if os.path.exists("nodes_eui64.log"):
			os.remove("nodes_eui64.log")
		
		self.mqttclient.connect(self.broker)

		timer = 0
		while True:
			self.mqttclient.loop(.1)

			if self.eui_retreival_started:
				timer += .1

			if timer > self.EUI64_RETREIVAL_TIMEOUT:
				break
