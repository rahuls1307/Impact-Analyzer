import json
import networkx as nx
import matplotlib.pyplot as plt

# ----------------------------
# Load Tree-sitter JSON output
# ----------------------------
with open("tree_sitter_sample_data.json", "r") as f:
    repos_data = json.load(f)

# ----------------------------
# Initialize directed graph
# ----------------------------
G = nx.DiGraph()

# ----------------------------
# Helper functions to add nodes and edges
# ----------------------------
def add_repo(repo_name, path):
    G.add_node(repo_name, type="repo", path=path)
    return repo_name

def add_file(file_name, repo_name, package=None):
    G.add_node(file_name, type="file", package=package)
    G.add_edge(repo_name, file_name, type="contains")
    return file_name

def add_class(class_name, file_node, class_type="class", annotations=[]):
    G.add_node(class_name, type="class", class_type=class_type, annotations=annotations)
    G.add_edge(file_node, class_name, type="contains")
    return class_name

def add_method(method_name, class_node, signature=None, annotations=[]):
    G.add_node(method_name, type="method", signature=signature, annotations=annotations)
    G.add_edge(class_node, method_name, type="contains")
    return method_name

def add_field(field_name, class_node, field_type=None, annotations=[]):
    G.add_node(field_name, type="field", field_type=field_type, annotations=annotations)
    G.add_edge(class_node, field_name, type="contains")
    return field_name

def add_annotation(annotation_text, parent_node):
    G.add_node(annotation_text, type="annotation")
    G.add_edge(parent_node, annotation_text, type="annotated_with")
    return annotation_text

def add_method_call(caller_method, callee_method):
    G.add_edge(caller_method, callee_method, type="calls")

def add_import(file_node, imported_class, repo_node=None):
    G.add_edge(file_node, imported_class, type="imported_from")
    if repo_node:
        G.add_edge(file_node, repo_node, type="imported_from")

# ----------------------------
# Filter strings by AST context
# ----------------------------
def keep_string_literal(feature, parent_type=None):
    """
    Only keep string literals that are part of:
    - Annotations
    - Method calls
    - Constants / field declarations
    """
    if feature["type"] != "string_literal":
        return True
    if parent_type in ["annotation", "method_invocation", "field_declaration"]:
        return True
    # otherwise discard trivial strings
    snippet = feature.get("snippet", "").strip()
    if len(snippet) <= 2:
        return False
    return True

# ----------------------------
# Build the graph
# ----------------------------
for repo_file in repos_data:
    file_path = repo_file["file"]
    repo_name = file_path.split("/")[3]  # heuristic: repo folder
    add_repo(repo_name, "/".join(file_path.split("/")[:4]))
    
    file_name = file_path.split("/")[-1]
    add_file(file_name, repo_name)
    
    last_class = None
    last_method = None
    
    for feat in repo_file.get("features", []):
        if not keep_string_literal(feat):
            continue
        
        node_label = f'{feat["type"]}: {feat.get("snippet","").splitlines()[0][:30]}'

        if feat["type"] == "class_declaration":
            last_class = add_class(node_label, file_name, annotations=[])
        elif feat["type"] == "method_declaration":
            if last_class:
                last_method = add_method(node_label, last_class, annotations=[])
            else:
                last_method = add_method(node_label, file_name, annotations=[])
        elif feat["type"] == "field_declaration":
            if last_class:
                add_field(node_label, last_class)
            else:
                add_field(node_label, file_name)
        elif feat["type"] == "annotation":
            if last_method:
                add_annotation(node_label, last_method)
            elif last_class:
                add_annotation(node_label, last_class)
            else:
                add_annotation(node_label, file_name)
        elif feat["type"] == "string_literal":
            # attach to last method, else class, else file
            if last_method:
                G.add_node(node_label, type="string_literal")
                G.add_edge(last_method, node_label, type="defines")
            elif last_class:
                G.add_node(node_label, type="string_literal")
                G.add_edge(last_class, node_label, type="defines")
            else:
                G.add_node(node_label, type="string_literal")
                G.add_edge(file_name, node_label, type="defines")

# ----------------------------
# Draw a simple graph for visualization
# ----------------------------
color_map = []
for node in G.nodes:
    ntype = G.nodes[node].get("type","")
    if ntype=="repo":
        color_map.append("lightblue")
    elif ntype=="file":
        color_map.append("skyblue")
    elif ntype=="class":
        color_map.append("lightgreen")
    elif ntype=="method":
        color_map.append("orange")
    elif ntype=="string_literal":
        color_map.append("pink")
    elif ntype=="annotation":
        color_map.append("yellow")
    else:
        color_map.append("gray")

plt.figure(figsize=(15,12))
pos = nx.spring_layout(G, k=0.5, seed=42)
nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=2000, font_size=8, arrowsize=20)
plt.title("Cross-Repo Impact Graph")
plt.show()
