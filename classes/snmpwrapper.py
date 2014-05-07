from pysnmp.entity.rfc3413.oneliner import cmdgen
from pprint import pprint
from oid import OID

class SNMPWrapper:
	"""docstring for SNMPWrapper"""

	#oid = OID()

	def __init__(self, community_str=''):
		self.community_str = community_str
		self.port = 161
		self.cmd_gen = cmdgen.CommandGenerator()

	def get(self, address, oid, vlan_id=''):
		"""docstring"""

		err_indication, err_status, err_index, var_binds = self.cmd_gen.getCmd(
			cmdgen.CommunityData(self.community_str + vlan_id),
			cmdgen.UdpTransportTarget((address, self.port)),
			cmdgen.MibVariable(oid),
			lookupNames=True, lookupValues=True
		)

		# Check for errors
		if err_indication or err_status:
			self.get_error(err_indication, err_status, err_index, address)
		else:
			#self.parse_var_binds(var_binds)
			#self.parse_reply(var_binds)
			return var_binds


	def walk(self, address, oid, vlan_id=''):
		"""docstring"""

		err_indication, err_status, err_index, var_bind_table = self.cmd_gen.nextCmd(
			cmdgen.CommunityData(self.community_str + vlan_id),
			cmdgen.UdpTransportTarget((address, self.port)),
			oid
		)

		# Check for errors
		if err_indication or err_status:
			self.walk_error(err_indication, err_status,
							err_index, address, var_bind_table)
		else:
			results = self.parse_var_bind_table(var_bind_table)
			
			return results


	def parse_var_binds(self, var_binds):
		print('parse_var_binds')

		#pprint(var_binds)

		for name, val in var_binds:
			# do something
			pass
			#print('key: ' + str(name))
			#print('value: ' + str(val))


	def parse_var_bind_table(self, var_bind_table):
		#print('parse_var_bind_table')

		#pprint(var_bind_table)

		keys = []
		values = []

		for var_bind_table_row in var_bind_table:
			for name, val in var_bind_table_row:
				keys.append(str(name))
				values.append(str(val))

		#return keys, values
		return var_bind_table

	def parse_reply(self, reply):
		print(type(reply))
		from pprint import pprint
		pprint(reply)


	def walk_error(self, indication, status, index, address, var_bind_table):
		"""SNMP WALK error handler"""

		#print('SNMPWALK ERROR')

		if indication:
			print(str(indication) + ' from ' + str(address))
		else:
			if status:
				print('%s at %s' % (status.prettyPrint(), index
				and var_bind_table[-1][int(index)-1] or '?'))


	def get_error(self, indication, status, index, address):
		"""SNMP GET error handler"""
		
		#print('SNMPGET ERROR')

		if indication:
			print(str(indication) + ' from ' + str(address))
		elif status:
			print(status)