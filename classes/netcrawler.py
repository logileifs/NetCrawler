from pysnmp.entity.rfc3413.oneliner import cmdgen
from vlan import VLAN
from host import Host
from oid import OID

class Crawler:
	"""This is the main class"""

	def __init__(self, *args):
		"""Crawler constructor, takes port and address as arguments"""
		self.port = args[0]
		self.address = args[1]					# starting point
		self.communityStr = args[2]
		self.cmdGen = cmdgen.CommandGenerator()
		self.vlans = []
		self.hosts = []

		self.oid = OID()
		self.debugMode= args[3]


	def checkEntryPoint(self, address):
		host = Host()
#		host.ip = address
		host.name = self.getHostName(address)
		if(len(host.name)):
			host.ip = address
			self.hosts.append(host)
			return True

		return False


	def getError(self, indication, status, index):
		print('SNMPGET ERROR')

		# Check for errors and print out results
		if indication:
			print(indication)
		elif status:
			print(status)


	"""def walkError(self, errorIndication, errorStatus, errorIndex):
		print('SNMPWALK ERROR')

		if errorIndication:
			print(errorIndication)
		else:
			if errorStatus:
				print('%s at %s' % (errorStatus.prettyPrint(),errorIndex
				and varBindTable[-1][int(errorIndex)-1] or '?'))"""


	def snmpGet(self, address, oid):
		errorIndication, errorStatus, errorIndex, varBinds = self.cmdGen.getCmd(
			cmdgen.CommunityData(self.communityStr),
			cmdgen.UdpTransportTarget((address, self.port)),
			cmdgen.MibVariable(oid),
			lookupNames=True, lookupValues=True
		)

		# Check for errors
		if errorIndication or errorStatus:
			self.getError(errorIndication, errorStatus, errorIndex)
		else:
			return varBinds


	def snmpWalk(self, address, oid):
		errorIndication, errorStatus, errorIndex, varBindTable = self.cmdGen.nextCmd(
			cmdgen.CommunityData(self.communityStr),
			cmdgen.UdpTransportTarget((address, self.port)),
			oid
		)

		if errorIndication:
			print(errorIndication)
		else:
			if errorStatus:
				print('%s at %s' % (
					errorStatus.prettyPrint(),
					errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
					)
				)
			else:		
				return varBindTable


	def getHostName(self, address):
		#print ('getHostName')
		hostName = ''

		varBinds = self.snmpGet(address, self.oid.hostName)

		for name, val in varBinds:
			hostName = str(val)
			#print(val.prettyPrint())

		#host.name = hostName

		return hostName


	def getInterface(self, host):
		print('interface for host ' + host.name)

		ipFound = ''
		result = self.snmpWalk(host.ip, self.oid.interface)

		for varBindTableRow in result:
			for name, val in varBindTableRow:
				if(str(name).find(self.oid.interface + '.') != -1):
					ipFound = str(name)[21:]
					if ipFound == host.ip:
						print('interface of host is: ' + str(val))
						host.interface = int(val)
					print(ipFound)
					print(name.prettyPrint())

#				print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))


	def getMAC(self, host):
		result = self.snmpGet(host.ip, self.oid.mac + '.' + str(host.interface))

		for name, val in result:
			print('mac address: ' + val.prettyPrint())

			#print(str(val))
			host.mac = host.hexToString(val)


	def getNeighbors(self, host):
		print('getNeighbors for ' + str(host.ip))
		numOfNeighbors = 0
		host.visited = True
		exists = False

		varBindTable = self.snmpWalk(host.ip, self.oid.neighbors)

		for varBindTableRow in varBindTable:
			for name, val in varBindTableRow:
				if(str(name).find(self.oid.neighbors) != -1):
					#print('FOUND IP ADDRESS')
					if(len(val) != 0):
						numOfNeighbors += 1
						newHost = Host()
						if(val.__class__.__name__ == 'OctetString'):
							newHost.ip = newHost.hexToOct(val)
#						newHost.ip = val
						for host in self.hosts:
							if host.ip == newHost.ip:
								exists = True

						if not exists:
							self.hosts.append(newHost)
				#print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))

		#print('NEIGHBORS FOUND:')
		for counter, host in enumerate(self.hosts):
			if(counter == 0):
				#print(host.ip)
				continue
			if(host.ip.__class__.__name__ == 'OctetString'):
				host.ip = host.hexToOct(host.ip)
			#print str(host.ip)

		return numOfNeighbors


	def printHosts(self):
		for counter, host in enumerate(self.hosts):
			print('\nHost ' + str(counter) + ': ' + host.name)
			print('visited: ' + str(host.visited))
			print('ip: ' + host.ip)
			print('mac: ' + host.mac)
			print('interface: ' + str(host.interface))


	def getVLANs(self):
		print('getVLANs')
		replies = []

		varBindTable = self.snmpWalk(self.address, oid.vlans)

		for varBindTableRow in varBindTable:
			for name, val in varBindTableRow:
				replies.append(name)

		for reply in replies:
			vlan = VLAN()
			vlan.number = int(str(reply).split('.')[-1])
			self.vlans.append(vlan)


	def getMACsOnVLAN(self, vlan):
		print('getMACsOnVLAN ' + str(vlan.number))

		errorIndication, errorStatus, errorIndex, varBindTable = self.cmdGen.nextCmd(
			cmdgen.CommunityData('menandmice@'+str(vlan.number)),
			cmdgen.UdpTransportTarget(('192.168.60.254', 161)),
			'.1.3.6.1.2.1.17.4.3.1.1'
		)

		if errorIndication:
			print(errorIndication)
		else:
			if errorStatus:
				print('%s at %s' % (
					errorStatus.prettyPrint(),
					errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
					)
				)
			else:
				for varBindTableRow in varBindTable:
					for name, val in varBindTableRow:
						print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
						host = Host(val)
						#host.mac = val
						vlan.hosts.append(host)

		for host in vlan.hosts:
			self.getIPForHost(vlan, host)


	def getIPForHost(self, vlan, host):
		print('getIPForHost ' + str(host.mac.prettyPrint()))

		errorIndication, errorStatus, errorIndex, varBindTable = self.cmdGen.nextCmd(
			cmdgen.CommunityData('menandmice@'+str(vlan.number)),
			cmdgen.UdpTransportTarget(('192.168.60.254', 161)),
			'1.3.6.1.2.1.4.22.1.2.29'
		)

		if errorIndication:
			print(errorIndication)
		else:
			if errorStatus:
				print('%s at %s' % (
					errorStatus.prettyPrint(),
					errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
					)
				)
			else:
				for varBindTableRow in varBindTable:
					for name, val in varBindTableRow:
						print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
						reply = str(name)
						if(reply.find('1.3.6.1.2.1.4.22.1.2.29.') != -1):
							ip = reply[24:]
							host.ip = ip
						if (val == host.mac):
							print('mac address ' + str(host.mac.prettyPrint()) + ' has ip: ' + ip)


	def dbPrint(self, string):
		if(debugMode):
			print(string)