from operator import itemgetter
import networkx as nx
import matplotlib.pyplot as plt


class DrawNetwork:
	""" To draw the network """

	def draw2(self, network):
		"""docstring"""

		edges = self.create_edges(network)
		nodes = self.create_nodes(network)
		labels = self.create_labels(network)

		G = nx.Graph()
		G.add_nodes_from(nodes)
		G.add_edges_from(edges)

		# Draw graph
		pos = nx.shell_layout(G)
		nx.draw(G, node_color='w', with_labels=True)
		G = nx.dodecahedral_graph()
		nx.draw_networkx_labels(G, pos, labels)

		plt.savefig('network.png')
		plt.show()

	def draw(self, network):
		"""docstring"""

		edges = self.create_edges(network)
		nodes = self.create_nodes(network)
		labels = self.create_labels(network)

		G = nx.Graph()
		G.add_nodes_from(network)
		G.add_edges_from(edges)

		mapping = self.map_labels(network)
		H = nx.relabel_nodes(G, mapping, False)

		pos = nx.spring_layout(G) # positions for all nodes

		nx.draw(G, pos = pos, node_color = 'r', node_size = 80, with_labels = True)

		plt.savefig("network.png") # save as png
		plt.show() # display


	def create_edges(self, network):
		"""docstring"""

		edges = []

		for key, value in network.iteritems():
			for neighbor in network[key]['neighbors']:
				edge = (key, neighbor)
				edges.append(edge)
				for neighbor in network[key]['neighbors']:
					edge = (key, neighbor)
					edges.append(edge)

		return edges


	def create_nodes(self, network):
		"""docstring"""

		nodes = []
		for key in network.iteritems():
			nodes.append(key)

		return nodes


	def create_labels(self, network):
		"""docstring"""

		labels = []
		for key, value in network.iteritems():
			labels.append(network[key]['ip'])

		return labels

	def map_labels(self, network):
		"""docstring"""

		labels = {}
		for key, value in network.iteritems():
			ip = network[key]['ip']
			labels[key] = ip

		return labels
