class Interface:

	def __init__(self):

		self.number = None
		self.descr = ''
		self.mac = ''
		self.macs_connected = []
		self.ips = []
		self.port = None
		self.status = None
		self.name = ''


	def __str__(self):
		return self.number


	def has_connections(self):

		return len(self.macs_connected) > 0


	def number_of_connections(self):

		return len(self.macs_connected)


	def add_mac(self, mac):

		if str(mac) not in self.macs_connected:
			self.macs_connected.append(mac)


	def print_interface(self):

		print('\tnumber: ' + str(self.number))
		print('\tdescr: ' + str(self.descr))
		print('\tname: ' + str(self.name))
		print('\tmac: ' + str(self.mac))
		print('\tport: ' + str(self.port))
		print('\tstatus: ' + str(self.status))

		print('\tconnected macs:')
		for mac in self.macs_connected:
			print('\t\t' + mac)
		print('')