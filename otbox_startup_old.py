import paramiko
import json
import subprocess
import time

from reservation import Reservation

class OTBoxStartup:

	def __init__(self):
		self.user = 'root'

		self.client = paramiko.SSHClient()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.client.load_system_host_keys()

		self.get_reserved_nodes()

	def ssh_connect(self, domain):
		try: 
			self.client.connect(domain, username=self.user)
			return True
		except:
			self.client.close()
			return False


	def get_reserved_nodes(self):
		test = subprocess.Popen(["iotlab-experiment", "get","-p"], stdout=subprocess.PIPE)
		output = test.communicate()[0]

		self.nodes = json.loads(output)['nodes']


	def start_otbox(self):
		for ind, node in self.nodes:
			node_name = 'node-' + node.split('.')[0]

			while True:
				boot_op = self.ssh_connect(node_name)

				if not boot_op:
					time.sleep(1)
				else:
					stdin, stdout, stderr = self.client.exec_command('cd ~/A8; pip install requests; python otbox.py')
					stdin.close()
					self.client.close()
					break
