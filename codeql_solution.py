import os
import subprocess
import json
from pathlib import Path


# ----------------- CONFIG -----------------
CODEQL_CLI = "/opt/homebrew/bin/codeql"  # your codeql executable
TEMP_DIR = "./temp_repos"
OUTPUT_FILE = "dependency_map.json"

# Repos to analyze
REPOS = [
    "https://srahulshanker@bitbucket.org/rahul-demo-workspace/backend-server.git"
]

# Map file extensions to CodeQL language imports
EXT_LANG_MAP = {
    ".java": "java",
    ".py": "python",
    ".cpp": "cpp",
    ".c": "cpp",
    ".js": "javascript",
    ".ts": "javascript",
    ".go": "go",
    # You can add more extensions as needed
}

# Example queries you have (with "import python" as placeholder)
# QUERY_FILES = ["functions.ql", "calls.ql", "db_usage.ql", "api_endpoints.ql", "config_usage.ql"]
QUERY_FILES = [ "api_endpoints.ql", "config_usage.ql"]
# ----------------- FUNCTIONS -----------------
def clone_repo(url, base_dir):
    repo_name = url.rstrip(".git").split("/")[-1]
    repo_path = os.path.join(base_dir, repo_name)
    if not os.path.exists(repo_path):
        subprocess.run(["git", "clone", url, repo_path], check=True)
    return repo_path

def detect_repo_languages(repo_path):
    langs = set()
    for root, _, files in os.walk(repo_path):
        for file in files:
            ext = Path(file).suffix
            if ext in EXT_LANG_MAP:
                langs.add(EXT_LANG_MAP[ext])
    return list(langs)

def create_codeql_db(repo_path, lang):
    db_path = os.path.join(repo_path, f"codeql-db-{lang}")
    if not os.path.exists(db_path):
        subprocess.run([
            CODEQL_CLI, "database", "create", db_path,
            "--language="+lang, "--source-root="+repo_path
        ], check=True)
    return db_path

def prepare_query(query_file, lang):
    with open(query_file, "r") as f:
        query_text = f.read()
    # Replace placeholder import with actual language import
    query_text = query_text.replace("import python", f"import {lang}")
    temp_query_path = query_file.replace(".ql", f"_{lang}.ql")
    with open(temp_query_path, "w") as f:
        f.write(query_text)
    return temp_query_path

def run_codeql_query(db_path, query_file, codeql_cli, lang):
    # Use the installed pack location
    search_path = "/Users/srahulshanker/.codeql/packages"
    
    stem = Path(query_file).stem
    bqrs_file = os.path.join(db_path, stem + ".bqrs")
    json_file = os.path.join(db_path, stem + "_results.json")

    # Run query -> BQRS
    subprocess.run([
        codeql_cli, "query", "run", query_file,
        "--database", db_path,
        "--output", bqrs_file,
        "--threads=0",
    ], check=True)

    # Decode BQRS -> JSON
    subprocess.run([
        codeql_cli, "bqrs", "decode", bqrs_file,
        "--format=json",
        "--output", json_file
    ], check=True)

    with open(json_file) as f:
        return json.load(f)

# ----------------- MAIN -----------------
def main():
    os.makedirs(TEMP_DIR, exist_ok=True)
    full_dep_map = {}

    for repo_url in REPOS:
        repo_path = clone_repo(repo_url, TEMP_DIR)
        repo_name = Path(repo_path).name
        full_dep_map[repo_name] = {}

        langs = detect_repo_languages(repo_path)
        print(f"[INFO] Detected languages for {repo_name}: {langs}")

        # Map languages to their query files
    LANG_QUERY_MAP = {
        "java": [ "db_usage_java.ql"],
        "python": ["functions.ql", "calls.ql", "db_usage.ql", "api_endpoints.ql", "config_usage.ql"]
    }

    # Then in your main loop:
    for lang in langs:
        db_path = create_codeql_db(repo_path, lang)
        full_dep_map[repo_name][lang] = []

        query_files = LANG_QUERY_MAP.get(lang, QUERY_FILES)  # fallback to original list
        for q in query_files:
            query_path = f"./codeql_queries/{q}"
            results = run_codeql_query(db_path, query_path, CODEQL_CLI, lang)
            full_dep_map[repo_name][lang].extend(results)
    # Save final semantic dependency map
    with open(OUTPUT_FILE, "w") as f:
        json.dump(full_dep_map, f, indent=2)

    print(f"[DONE] Dependency map saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
