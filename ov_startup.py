import subprocess

class OVStartup:

	def start(self):
		subprocess.Popen(['sudo', 'scons', 'runweb', '--port=8080', '--opentestbed', '--root=random'], cwd='/home/vagrant/soda/openvisualizer/openvisualizer', stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

