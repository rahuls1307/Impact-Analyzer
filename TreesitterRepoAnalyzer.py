import json
import os
import re
import sys
import tempfile
from git import Repo
from tqdm import tqdm
from tree_sitter_languages import get_parser

# -------------------------------------------------
# STEP 1: Prepare Tree-sitter parsers (prebuilt)
# -------------------------------------------------
# Using tree_sitter_languages prebuilt parsers; no build step required

# -------------------------------------------------
# STEP 2: Repo cloning
# -------------------------------------------------
def clone_repo(repo_url: str):
    base_dir = os.path.join(os.path.expanduser("~"), "tree_sitter_repos")
    os.makedirs(base_dir, exist_ok=True)
    repo_name = os.path.splitext(os.path.basename(repo_url))[0]
    local_path = os.path.join(base_dir, repo_name)

    if not os.path.exists(local_path):
        print(f"🚀 Cloning {repo_url} ...")
        Repo.clone_from(repo_url, local_path)
    else:
        print(f"✅ Repo already exists at {local_path}")

    return local_path

# -------------------------------------------------
# STEP 3: Language detection helper
# -------------------------------------------------
EXT_LANG_MAP = {
    ".java": "java",
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".go": "go",
    ".rb": "ruby",
    ".cs": "c_sharp",
    ".sql": "sql",
    ".xml": "xml",
    ".yml": "yaml",
    ".yaml": "yaml",
}

def detect_language(file_path):
    _, ext = os.path.splitext(file_path)
    return EXT_LANG_MAP.get(ext.lower())

# -------------------------------------------------
# STEP 4: Tree-sitter extraction
# -------------------------------------------------
def extract_code_features(code, language_name):
    try:
        parser = get_parser(language_name)
    except Exception as e:
        # Gracefully handle the error, which is likely the __init__ error
        # for problematic languages (like yaml, xml, sql).
        print(f"    ⚠️ Failed to get parser for language '{language_name}': {e}")
        return [] # Return empty features list to skip the file
    tree = parser.parse(bytes(code, "utf8"))
    root = tree.root_node

    features = []
    capture_nodes(root, code, features)
    return features

def capture_nodes(node, code, features):
    text = code[node.start_byte:node.end_byte]

    if node.type in {"class_declaration", "function_definition", "method_declaration"}:
        features.append({"type": node.type, "snippet": text[:120] + "..." if len(text) > 120 else text})

    # Capture string literals and detect SQL-like content
    if node.type == "string_literal":
        snippet = text.strip('"').strip("'")
        if re.search(r"\bSELECT|INSERT|UPDATE|DELETE|CREATE\s+TABLE\b", snippet, re.I):
            features.append({"type": "sql_snippet", "snippet": snippet})
        else:
            features.append({"type": "string_literal", "snippet": snippet[:120]})

    # Recursively walk children
    for child in node.children:
        capture_nodes(child, code, features)

# -------------------------------------------------
# STEP 5: Repo-wide scan
# -------------------------------------------------
def analyze_repo(repo_url):
    repo_path = clone_repo(repo_url)
    results = []

    all_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            if detect_language(file_path):
                all_files.append(file_path)

    print(f"📂 Found {len(all_files)} relevant files")

    for file_path in tqdm(all_files, desc="Analyzing files", ncols=100):
        lang = detect_language(file_path)
        print(f"🔍 Detected language: {lang}")
        try:
            with open(file_path, "r", errors="ignore") as f:
                code = f.read()
            feats = extract_code_features(code, lang)
            if feats:
                results.append({"file": file_path, "language": lang, "features": feats})
        except Exception as e:
            print(f"⚠️ Skipping {file_path}: {e}")

    return results

# -------------------------------------------------
# STEP 6: CLI entrypoint
# -------------------------------------------------


repo_url = 'https://srahulshanker@bitbucket.org/rahul-demo-workspace/backend-server.git'
output = analyze_repo(repo_url)
output_path = os.path.join(os.path.expanduser("~"), "tree_sitter_repos", "output.json")
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"Output saved to {output_path}")

print("\n\n========= 🔍 TREE-SITTER OUTPUT =========\n")
for file_result in output:
    print(f"\n📄 File: {file_result['file']} ({file_result['language']})")
    for feat in file_result["features"]:
        print(f"  - {feat['type']}: {feat['snippet'][:100]}")
