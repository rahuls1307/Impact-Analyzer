import json
import networkx as nx
import matplotlib.pyplot as plt

# Load JSON file
with open("impact_graph.json", "r") as f:
    data = json.load(f)

G = nx.DiGraph()

# Add nodes
for node in data["nodes"]:
    G.add_node(node["id"], type=node["type"], repo=node["repo"])

# Add edges
for edge in data["edges"]:
    G.add_edge(edge["from"], edge["to"], type=edge["type"])

# Draw graph
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_size=2500, node_color='lightgreen', font_size=10)
edge_labels = nx.get_edge_attributes(G, 'type')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
plt.show()
