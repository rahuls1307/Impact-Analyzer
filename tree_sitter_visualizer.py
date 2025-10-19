import json
import networkx as nx
import matplotlib.pyplot as plt

# Example: load your Tree-sitter output
with open("impact_graph.json", "r") as f:
    data = json.load(f)

G = nx.DiGraph()

for file_item in data:
    file_node = file_item["file"]
    G.add_node(file_node, type="file")
    
    for feature in file_item.get("features", []):
        f_type = feature["type"]
        snippet = feature.get("snippet", "").split("\n")[0]  # first line as label
        node_label = f"{f_type}: {snippet[:30]}"  # truncate for readability
        G.add_node(node_label, type=f_type)
        G.add_edge(file_node, node_label)

# Optional: color nodes by type
color_map = []
for node in G:
    ntype = G.nodes[node]["type"]
    if ntype == "file":
        color_map.append("lightblue")
    elif ntype == "class_declaration":
        color_map.append("lightgreen")
    elif ntype == "method_declaration":
        color_map.append("orange")
    elif ntype == "string_literal":
        color_map.append("pink")
    else:
        color_map.append("gray")

# Draw the graph
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, k=0.5, seed=42)
nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=1500, font_size=8, arrowsize=20)
plt.title("Tree-sitter Code Structure Graph")
plt.show()
