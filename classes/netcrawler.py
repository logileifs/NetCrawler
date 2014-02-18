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


	def checkEntryPoint(self, address):
		host = Host()
		host.name = self.getHostName(address)
		if(len(host.name)):
			host.ip = address
			self.hosts.append(host)
			return True

		return False


	""" GEYMA
	def getError(self, indication, status, index):
		print('GET ERROR')
		if indication:
			print(indication)
		elif status:
			print(status)


	def walkError(self, errorIndication, errorStatus, errorIndex):
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

		# Check for errors and print out results
		if errorIndication:
			#self.getError(errorIndication, errorStatus, errorIndex)
			print(errorIndication)
		elif errorStatus:
			print(errorStatus)
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
		print ('getHostName')

		varBinds = self.snmpGet(address, self.oid.hostName)
#		varBinds = self.snmpGet(address, '1.1.1.1.1.1.1.1.1.1.1.1.1.1')

		for name, val in varBinds:
			print(val.prettyPrint())

		return str(val)


	def getNeighbors(self, host):
		print('getNeighbors for ' + str(host.ip))
		host.visited = True
		numOfNeighbors = 0

		varBindTable = self.snmpWalk(host.ip, self.oid.neighbors)

		for varBindTableRow in varBindTable:
			for name, val in varBindTableRow:
				if(str(name).find(self.oid.neighbors) != -1):
					print('FOUND IP ADDRESS')
					if(len(val) != 0):
						numOfNeighbors += 1
						newHost = Host()
						newHost.ip = val
						self.hosts.append(newHost)
				#print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))

		print('NEIGHBORS FOUND:')
		for counter, host in enumerate(self.hosts):
			if(counter == 0):
				print(host.ip)
				continue
			if(host.ip.__class__.__name__ == 'OctetString'):
				#print('class type is OctetString')
				host.ip = host.hexToOct(host.ip)
			#print(host.ip.__class__.__name__)
			print str(host.ip)

		return numOfNeighbors


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

#		print('vlans:')
#		for vlan in self.vlans:
#			print(vlan.number)
		
#		self.getMACsOnVLAN(self.vlans[1])


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
			#print(host.mac.prettyPrint())
			self.getIPForHost(vlan, host)
#			print(mac.prettyPrint())
#			print(vlan.convertMacToOct(mac))


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
#							print(ip[24:])
						if (val == host.mac):
							print('mac address ' + str(host.mac.prettyPrint()) + ' has ip: ' + ip)