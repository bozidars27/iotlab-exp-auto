import sys

from otbox_startup import OTBoxStartup
from ov_startup import OVStartup
from reservation import Reservation


def main():
	print 'Script started'
	if sys.argv[1] == '-reserve':
		print 'Reserving nodes'
		res = Reservation('skrbic', 'saclay.iot-lab.info')
		res.reserve_experiment(15, 5)
	elif sys.argv[1] == '-otbox':
		print 'Starting OTBox'
		OTBoxStartup('skrbic', 'saclay.iot-lab.info').start()
	elif sys.argv[1] == '-ov':
		print 'Starting OV'
		OVStartup().start()


if __name__ == '__main__':
	main()
		