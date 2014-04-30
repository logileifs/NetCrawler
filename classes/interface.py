class Interface:

	def __init__(self):

		self.number = None
		self.descr = ''
		self.mac = ''
		self.macs_connected = []
		self.ips = []
		self.port = None
		self.status = None

	def __str__(self):
		return self.number


	def print_interface(self):

		print('\tnumber: ' + str(self.number))
		print('\tdescr: ' + str(self.descr))
		print('\tmac: ' + str(self.mac))
		print('\tport: ' + str(self.port))
		print('\tstatus: ' + str(self.status))

		print('\tconnected macs:')
		for mac in self.macs_connected:
			print('\t\t' + mac)