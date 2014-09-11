import config
import random

def get_random_port():
	port_range=config.PortRange.strip("'").split(':')	
	random_port = random.randint(int(port_range[0]),int(port_range[1]))
		
	return random_port

if __name__ == '__main__':
	print get_random_port()
