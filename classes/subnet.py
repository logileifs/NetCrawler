#import ipcalc as ipcalc

class Subnet:
	"""docstring for Subnet"""
	def __init__(self, net):
		self.net = net 					#ipcalc network object
		self.id = net.network()
		self.broadcast = net.broadcast()
		self.network = net.network()
		
		self.unknown_ips = []			#not in use
		self.known_ips = []			#not in use
		self.host_list = []
		self.scanned = False


	def __str__(self):
		return str(self.id)


	def in_network(self, address):
		return self.net.in_network(address)


	def host_exists(self, host):

		for h in self.host_list:
			if host.id == h.id:
				return True

		return False


	def add_host(self, host):

		if not self.host_exists(host):
			self.host_list.append(host)


	def add_known_ip(self, ip_addr):

		if ip_addr not in self.known_ips:
			self.known_ips.append(ip_addr)


	def add_unknown_ip(self, ip_addr):

		if ip_addr not in self.known_ips:
			if ip_addr not in self.unknown_ips:
				self.unknown_ips.append(ip_addr)


	def remove_unknown_ip(self, ip_addr):

		if ip_addr in self.unknown_ips:
			self.unknown_ips.remove(ip_addr)


	def get_next_unknown_ip(self):

		if self.unknown_ips:
			return self.unknown_ips[0]