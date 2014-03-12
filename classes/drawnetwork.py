from operator import itemgetter
import networkx as nx
import matplotlib.pyplot as plt


class DrawNetwork:
	""" To draw the network """

	def draw2(self, network):
		edges = self.createEdges(network)
		nodes = self.createNodes(network)
		labels = self.createLabels(network)

		G=nx.Graph()
		G.add_nodes_from(nodes)
		G.add_edges_from(edges)

		# Draw graph
		pos=nx.shell_layout(G)
		nx.draw(G,node_color='w',with_labels=True)
		G=nx.dodecahedral_graph()
		nx.draw_networkx_labels(G,pos, labels)

		plt.savefig('network.png')
		plt.show()

	def draw(self, network):
		edges = self.createEdges(network)
		nodes = self.createNodes(network)
		labels = self.createLabels(network)

		G=nx.Graph()
		G.add_nodes_from(network)
		G.add_edges_from(edges)

		mapping = self.mapLabels(network)
		H=nx.relabel_nodes(G,mapping,False)

		pos=nx.spring_layout(G) # positions for all nodes

		nx.draw(G, pos=pos, node_color='b', node_size=80, with_labels=True)

		plt.savefig("network.png") # save as png
		plt.show() # display


	def createEdges(self, network):
		edges = []

		for key, value in network.iteritems():
			for neighbor in network[key]['neighbors']:
				edge = (key, neighbor)
				edges.append(edge)
				for neighbor in network[key]['neighbors']:
					edge = (key, neighbor)
					edges.append(edge)

		return edges


	def createNodes(self, network):
		nodes = []
		for key in network.iteritems():
			nodes.append(key)

		return nodes


	def createLabels(self, network):
		labels = []
		for key, value in network.iteritems():
			labels.append(network[key]['ip'])

		return labels

	def mapLabels(self, network):
		labels= {}
		for key, value in network.iteritems():
			ip = network[key]['ip']
			labels[key] = ip

		return labels
