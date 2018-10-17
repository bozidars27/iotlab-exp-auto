import sys
import ConfigParser

from otbox_startup import OTBoxStartup
from ov_startup import OVStartup
from reservation import Reservation
from ov_log_monitor import OVLogMonitor

configParser = ConfigParser.RawConfigParser()   
configFilePath = 'conf.txt'
configParser.read(configFilePath)

USERNAME = configParser.get('exp-config', 'user')
HOSTNAME = 'saclay.iot-lab.info'

EXP_DURATION = 15 #Duration in minutes
NODES = "saclay,a8,106+107+108"

def main():
	print 'Script started'
	if sys.argv[1] == '-check':
		print 'Checking experiment'
		Reservation(USERNAME, HOSTNAME).check_experiment()
	if sys.argv[1] == '-reserve':
		print 'Reserving nodes'
		Reservation(USERNAME, HOSTNAME).reserve_experiment(EXP_DURATION, NODES)
	if sys.argv[1] == '-terminate':
		print 'Terminating experiment'
		Reservation(USERNAME, HOSTNAME).terminate_experiment()
	elif sys.argv[1] == '-otbox':
		print 'Starting OTBox'
		OTBoxStartup(USERNAME, HOSTNAME).start()
	elif sys.argv[1] == '-ov-start':
		print 'Starting OV'
		OVStartup().start()
	elif sys.argv[1] == '-ov-monitor':
		print 'Starting OV log monitoring'
		OVLogMonitor().start()

if __name__ == '__main__':
	main()

