from pysnmp.entity.rfc3413.oneliner import cmdgen
from pingsweep import PingSweep
from vlan import VLAN
from host import Host
from oid import OID
import ipcalc
import socket
#import ping
import sys

class Crawler:
	"""This is the main class"""

	def __init__(self, *args):
		"""Crawler constructor, takes port and address as arguments"""
		self.port = args[0]
		self.address = args[1]					# starting point
		self.range = []

		net = ipcalc.Network(self.address)
		print('size of network: ' + str(net.size()))
		print('broadcast address: ' + str(net.broadcast()))

		#for ip in ipcalc.Network(self.address):
			#self.range.append(str(ip))

		#print('first host: ' + str(net.host_first()))
		#print('last host: ' + str(net.host_last()))
		#print('size of range: ' + str(len(self.range)))

		pingsweep = PingSweep(net)
		self.range = pingsweep.sweep()
		self.hostList = []

		print('crawler address range:')
		for counter, ip in enumerate(self.range):
			host = Host()
			host.ip = ip
			host.id += str(counter)
			self.hostList.append(host)
			print(counter)

		print('alive hosts:')
		for host in self.hostList:
			print(host.ip)

		self.communityStr = args[2]
		self.debugMode= args[3]
		self.cmdGen = cmdgen.CommandGenerator()
		self.hosts = []
		self.vlans = []
		self.oid = OID()

		self.network = {}
		self.subnets = {}

		host = Host()
		host.ip = self.address
		self.hosts.append(host)


	def getError(self, indication, status, index):
		print('SNMPGET ERROR')

		# Check for errors and print out results
		if indication:
			print(indication)
		elif status:
			print(status)


	def walkError(self, errorIndication, errorStatus, errorIndex):
		print('SNMPWALK ERROR')

		if errorIndication:
			print(errorIndication)
		else:
			if errorStatus:
				print('%s at %s' % (errorStatus.prettyPrint(),errorIndex
				and varBindTable[-1][int(errorIndex)-1] or '?'))


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

		# Check for errors
		if errorIndication or errorStatus:
			self.walkError(errorIndication, errorStatus, errorIndex)
		else:
			return varBindTable


	def getInfo(self, host):
		self.dbPrint('Getting info for ', host.ip)

		host.name = self.getHostName(host)

		host.interface = self.getInterface(host)

		host.mac = self.getMAC(host)

		host.neighbors = self.getNeighbors(host)

		self.getType(host)

		#self.getVLANs(host)
#		if(host.id != None):
			
#			host.id = 'host'+ str(host.id)
#		self.dbPrint(hostName)
		self.network[host.id] = {'mac':host.mac,'name': host.name, 'ip': host.ip, 'interface': host.interface, 'neighbors': host.neighbors }

		self.dbPrint('network dictionary:')
		for key, value in self.network.iteritems():
			print key, value
#			if key == 'neighbors':
#				print('key = neighbors')
			for neighbor in self.network[key]['neighbors']:
				print neighbor


	def getHostName(self, host):
		self.dbPrint('getHostName')
		hostName = ''

		varBinds = self.snmpGet(host.ip, self.oid.hostName)

		if varBinds is None:
			return ''

		for name, val in varBinds:
			hostName = str(val)
			self.dbPrint(val.prettyPrint())

		return hostName


	def getInterface(self, host):
		self.dbPrint('interface for host ', host.name)

		ipFound = False
		interface = ''

		result = self.snmpWalk(host.ip, self.oid.interface)

		if result is None:	# catch error
			return 0

		for varBindTableRow in result:
			for name, val in varBindTableRow:

				ipFound = self.searchStringForIP(name, host)
				if ipFound:
					self.dbPrint('interface of host is: ', str(val))
					interface = int(val)
				self.dbPrint(name.prettyPrint())

		return interface


	def searchStringForIP(self, name, host):
		"""Search for the host's ip in the snmp response"""

		ipFound = ''
		if(str(name).find(self.oid.interface + '.') != -1):
			ipFound = str(name)[21:]
			if ipFound == host.ip:
				return True

		return False


	def getMAC(self, host):
		self.dbPrint('get mac for ' + host.ip)
		mac = ''

		result = self.snmpGet(host.ip, self.oid.mac + '.' + str(host.interface))

		if result is None:	# catch error
			return ''

		for name, val in result:
			mac = host.hexToString(val)
			self.dbPrint('mac address: ', val.prettyPrint())

			#print(str(val))
			#host.mac = host.hexToString(val)
		return mac


	def getType(self, host):
		self.dbPrint('getType for ' + str(host.ip))
		result = self.snmpGet(host.ip, self.oid.type)

		if result is None:
			return ''

		for name, val in result:
			if val == 1:
				print('device is a router')
				host.type = 'router'


	def getHostID(self, hostIP):
		for host in self.hostList:
			if hostIP == host.ip:
				return host.id
		return None


	def getNeighbors(self, host):
		self.dbPrint('getNeighbors for ' + str(host.ip))
		neighbors = []
		host.visited = True
		exists = False

		varBindTable = self.snmpWalk(host.ip, self.oid.neighbors)

		if varBindTable is None:	# catch error
			return []

		for varBindTableRow in varBindTable:
			for name, val in varBindTableRow:
				if(str(name).find(self.oid.neighbors) != -1):
					self.dbPrint('FOUND IP ADDRESS')
					if(len(val) != 0):
						newHost = Host()
						if(val.__class__.__name__ == 'OctetString'):
							newHost.ip = newHost.hexToOct(val)
							newHost.id = self.getHostID(newHost.ip)
							newHost.mac = self.getMACofIP(host, newHost)
							self.dbPrint('adding ' + newHost.ip)
							if(newHost.id != None):
								neighbors.append(lnewHost.id)
							else
								dbPrint('A host in neighbor list is None')
#						for host in self.hosts:
#						for someHost in self.hostList:
#							if someHost.ip == newHost.ip:
#								exists = True

#						if not exists:
#							self.hosts.append(newHost)
#							self.hostList.append(newHost)
				#print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))

		self.dbPrint('NEIGHBORS FOUND:')
#		for counter, host in enumerate(self.hosts):
		for counter, host in enumerate(self.hostList):
			if(counter == 0):
				self.dbPrint(host.ip)
				continue
			#if(host.ip.__class__.__name__ == 'OctetString'):
				#host.ip = host.hexToOct(host.ip)
			#print str(host.ip)

		#return numOfNeighbors

		return neighbors


#	def getMACofIP(self, address, interface, ip):
	def getMACofIP(self, host, newHost):
		self.dbPrint('getting mac for ' + str(newHost.ip) + ' from ' + str(host.ip))
		self.dbPrint('interface: ' + str(host.interface))
								#ipNetToMediaPhysAddress	#interface
		result = self.snmpGet(host.ip, '1.3.6.1.2.1.4.22.1.2' + '.' + str(host.interface) + '.' + str(newHost.ip))

		if result is None:
			return ''

		for name, val in result:
			self.dbPrint('converting mac: ' + val.prettyPrint())
			mac = newHost.hexToString(val)

		print('mac of neighbor ' + str(newHost.ip) + ' is ' + mac)

		return mac


	def printHosts(self):
		for counter, host in enumerate(self.hostList):
			print('\nHost ' + str(counter) + ': ' + host.name)
			print('visited: ' + str(host.visited))
			print('ip: ' + host.ip)
			print('mac: ' + host.mac)
			print('type: ' + host.type)
			print('interface: ' + str(host.interface))
			print('neighbors: ')
			for neighbor in host.neighbors:
				print('\t' + str(neighbor))


	def printNetwork(self):
		self.dbPrint('network dictionary:')
		for key, value in self.network.iteritems():
			print key, value
			for neighbor in self.network[key]['neighbors']:
				print neighbor


	def getVLANs(self, host):
		self.dbPrint('getVLANs')
		replies = []

		varBindTable = self.snmpWalk(host.ip, self.oid.vlans)

		for varBindTableRow in varBindTable:
			for name, val in varBindTableRow:
				#print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
				
				if int(val) == 1:
					replies.append(name)
					#print('vlan ' + str(name) + ' is operational')

		for reply in replies:
			vlan = VLAN()
			vlan.number = int(str(reply).split('.')[-1])
	
			if vlan.number not in self.subnets:
				self.subnets[str(vlan.number)] = { 'hosts': [] }
#			print(vlan.number)
			#self.vlans.append(vlan)

		print('subnets:')
		print(self.subnets)


	def getMACsOnVLAN(self, vlan):
		self.dbPrint('getMACsOnVLAN ', str(vlan.number))

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
		self.dbPrint('getIPForHost ', str(host.mac.prettyPrint()))

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


	def generateXML(self):
		from dicttoxml import dicttoxml
		xml = dicttoxml(self.network)
		with open('network.xml', 'w') as myFile:
			myFile.write(xml)


	def dbPrint(self, *args):
		if(self.debugMode):
			output = ''
			for arg in args:
				output += str(arg)
			print('## ' + output)


	