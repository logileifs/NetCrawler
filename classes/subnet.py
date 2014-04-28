#import ipcalc as ipcalc

class Subnet:
	"""docstring for Subnet"""
	def __init__(self, net):
		self.net = net 					#ipcalc network object
		self.id = net.network()
		self.broadcast = net.broadcast()
		self.network = net.network()
		
		self.unknown_hosts = []			#not in use
		self.known_hosts = []			#not in use
		self.host_list = []

	def __str__(self):
		return str(self.id)

	def in_network(self, address):
		return self.net.in_network(address)