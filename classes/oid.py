"""SNMP Object Identifier data module"""

class OID:
	"""OID class"""

	def __init__(self, vendor=''):

		print('CREATING OID INSTANCE - VENDOR: ' + str(vendor))

		if vendor == '' or 'cisco':
			#self.hostname = '1.3.6.1.4.1.9.9.23.1.3.4.0'	#1.3.6.1.4.1.9.2.1.3 try this one
			self.hostname = '1.3.6.1.4.1.9.2.1.3.0'
			self.neighbors2 = '1.3.6.1.4.1.9.9.23.1.2.1.1.20'	#OLD - DO NOT USE
			self.neighbors = '1.3.6.1.4.1.9.9.23.1.2.1.1.4'
			self.vlans = '.1.3.6.1.4.1.9.9.46.1.3.1.1.2'
			self.macs_on_vlan = '.1.3.6.1.2.1.17.4.3.1.1'
			self.interface = '1.3.6.1.2.1.4.20.1.2'
			self.mac = '1.3.6.1.2.1.2.2.1.6'
			self.type = '1.3.6.1.2.1.4.1.0'	# 1 = router, 2 = not router
			self.sys_descr = '1.3.6.1.2.1.1.1.0'
			self.num_of_ports = '.1.3.6.1.2.1.17.1.2.0'
			self.cost_to_root = '.1.3.6.1.2.1.17.2.6.0'
			self.lowest_cost_port = '.1.3.6.1.2.1.17.2.7.0'
			self.serial_number = '1.3.6.1.2.1.47.1.1.1.1.11.1'
			self.model = '1.3.6.1.2.1.47.1.1.1.1.13.1'