from operator import itemgetter
import networkx as nx
import matplotlib.pyplot as plt


class DrawNetwork:
	""" To draw the network """

	def draw(self, network):
		edges = self.createEdges(network)

		G=nx.Graph()
		G.add_nodes_from(network)
		G.add_edges_from(edges)

		# Draw graph
		pos=nx.shell_layout(G)
		nx.draw(G,node_color='w',with_labels=True)
		G=nx.dodecahedral_graph()

		# Draw ego as large and red
		#nx.draw_networkx_nodes(hub_ego,pos,nodelist=[nodes],node_size=300,node_color='r')
		plt.savefig('network.png')
		plt.show()

	def createEdges(self, network):
		edges = []

		for key, value in network.iteritems():
			for neighbor in network[key]['neighbors']:
				edge = (key, neighbor)
				edges.append(edge)

		return edges

