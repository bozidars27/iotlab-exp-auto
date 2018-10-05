from socket_io_handler import SocketIoHandler

import time
import subprocess
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

socketIoHandler = SocketIoHandler()


class MyHandler(FileSystemEventHandler):

	def __init__(self):
		self.last_timestamp = 0.0

	def on_modified(self, event):
		try:
			last_line = self.get_last_line(event.src_path)
			last_line_timestamp = float(json.loads(last_line)['_timestamp'])

			if last_line_timestamp > self.last_timestamp:
				#print("event type: " + str(event.event_type) + " path : " + str(event.src_path))
				socketIoHandler.publish('LOG_MODIFICATION', last_line)		
				self.last_timestamp = last_line_timestamp
		except Exception, e:
			socketIoHandler.publish('LOG_MODIFICATION', str(e))		
		

	def get_last_line(self, file_path):
		return subprocess.check_output(['tail', '-1', file_path])


class OVLogMonitor:

	LOG_DIR = '/home/vagrant/soda/openvisualizer/openvisualizer/build/runui'

	def __init__(self):
		self.event_handler = MyHandler()
		self.observer = Observer()

	def start(self):
		self.observer.schedule(self.event_handler, path=self.LOG_DIR, recursive=False)
		self.observer.start()

		try:
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			self.observer.stop()

		self.observer.join()



