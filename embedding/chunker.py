"""
chunker.py — Extracts structured code chunks from repositories or single files.
Used in P1 pipeline for code embedding and semantic tracking.
"""

import os
import glob
from git import Repo
from tree_sitter_languages import get_parser
from tqdm import tqdm

# ---------- CONFIG ----------
LANGUAGE_EXTENSIONS = {
    ".py": "python",
    ".java": "java",
    ".js": "javascript",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".h": "cpp",
    ".hpp": "cpp",
    ".go": "go",
    ".sql": "sql",
    ".ddl": "sql"
}

LANGUAGE_NODES = {
    "python": {"function": ["function_definition"], "class": ["class_definition"]},
    "java": {"function": ["method_declaration"], "class": ["class_declaration"]},
    "javascript": {"function": ["function_declaration", "method_definition"], "class": ["class_declaration"]},
    "cpp": {"function": ["function_definition"], "class": ["class_specifier"]},
    "go": {"function": ["function_declaration"], "class": []},
    "sql": {"function": [], "class": []}
}


def extract_chunks(code_bytes, lang_key, level="function"):
    # print("in exptract chunks " + code_bytes + lang_key +level)
    """Parse code with Tree-sitter and extract function/class chunks."""
    parser = get_parser(lang_key)
    tree = parser.parse(code_bytes)
    root = tree.root_node

    node_types = LANGUAGE_NODES.get(lang_key, {}).get(level, [])
    chunks = []

    def recurse(node):
        if node.type in node_types:
            start, end = node.start_byte, node.end_byte
            chunk_code = code_bytes[start:end].decode("utf8", errors="ignore").strip()
            if chunk_code:
                chunks.append(chunk_code)
        for child in node.children:
            recurse(child)

    recurse(root)
    return chunks


def clone_repo(url, dest_dir="repos"):
    """Clone a git repository (used in initialization)."""
    os.makedirs(dest_dir, exist_ok=True)
    repo_name = url.split("/")[-1].replace(".git", "")
    path = os.path.join(dest_dir, repo_name)
    if not os.path.exists(path):
        print(f"📦 Cloning {url} ...")
        Repo.clone_from(url, path)
    else:
        print(f"✅ Repo already cloned: {repo_name}")
    return path


def process_repo(repo_path):
    """Process an entire repository into code chunks."""
    repo_name = os.path.basename(repo_path)
    results = []

    for path in tqdm(glob.glob(f"{repo_path}/**/*.*", recursive=True), desc=f"Scanning {repo_name}"):
        ext = os.path.splitext(path)[1]
        if ext not in LANGUAGE_EXTENSIONS:
            continue
        lang = LANGUAGE_EXTENSIONS[ext]
        print("languageee :" +lang)
        try:
            with open(path, "rb") as f:
                code = f.read()
                print("this is code")
        except Exception:
            print("xception in reading code")
            continue

        if lang == "sql":
            chunk = code.decode("utf8", errors="ignore").strip()
            if chunk:
                results.append({
                    "repo": repo_name,
                    "path": path,
                    "language": lang,
                    "chunk_type": "db_schema",
                    "chunk_id": f"{repo_name}_{os.path.basename(path)}_0",
                    "chunk": chunk,
                })
        else:
            for level in ["function", "class"]:
                # print("levelll "+code)
                chunks = extract_chunks(code, lang, level)
                for i, chunk in enumerate(chunks):
                    results.append({
                        "repo": repo_name,
                        "path": path,
                        "language": lang,
                        "chunk_type": level,
                        "chunk_id": f"{repo_name}_{os.path.basename(path)}_{i}",
                        "chunk": chunk,
                    })

    return results


def chunk_file(file_path, repo_name="unknown"):
    """Chunk a single file — used by RepoWatcher for incremental updates."""
    ext = os.path.splitext(file_path)[1]
    if ext not in LANGUAGE_EXTENSIONS:
        return []

    lang = LANGUAGE_EXTENSIONS[ext]
    results = []

    try:
        with open(file_path, "rb") as f:
            code = f.read()
    except Exception as e:
        print(f"⚠️ Could not read {file_path}: {e}")
        return []

    if lang == "sql":
        chunk = code.decode("utf8", errors="ignore").strip()
        if chunk:
            results.append({
                "repo": repo_name,
                "path": file_path,
                "language": lang,
                "chunk_type": "db_schema",
                "chunk_id": f"{repo_name}_{os.path.basename(file_path)}_0",
                "chunk": chunk,
            })
    else:
        for level in ["function", "class"]:
            chunks = extract_chunks(code, lang, level)
            for i, chunk in enumerate(chunks):
                results.append({
                    "repo": repo_name,
                    "path": file_path,
                    "language": lang,
                    "chunk_type": level,
                    "chunk_id": f"{repo_name}_{os.path.basename(file_path)}_{i}",
                    "chunk": chunk,
                })

    return results
