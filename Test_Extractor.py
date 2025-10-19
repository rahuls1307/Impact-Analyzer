import os
from git import Repo, RemoteProgress
from tqdm import tqdm
from ArtifactExtractor import SemanticArtifactExtractor  # your extractor class
import json

# -----------------------------
# Setup repo details
# -----------------------------
REPO_URL = "https://srahulshanker@bitbucket.org/rahul-demo-workspace/backend-server.git"
REPO_NAME = "StockPortfolio"

# Persistent folder
BASE_DIR = os.path.join(os.path.expanduser("~"), "cloned_repos")
os.makedirs(BASE_DIR, exist_ok=True)

LOCAL_PATH = os.path.join(BASE_DIR, REPO_NAME)

# -----------------------------
# Git clone with progress bar
# -----------------------------
class TqdmProgress(RemoteProgress):
    def __init__(self):
        super().__init__()
        self.pbar = tqdm(total=100, desc="Cloning Repo", ncols=100, leave=True)

    def update(self, op_code, cur_count, max_count=None, message=''):
        if max_count:
            self.pbar.n = int(cur_count / max_count * 100)
            self.pbar.refresh()

if not os.path.exists(LOCAL_PATH):
    print(f"Cloning {REPO_URL} into {LOCAL_PATH} ...")
    Repo.clone_from(REPO_URL, LOCAL_PATH, progress=TqdmProgress())
else:
    print(f"Repo already exists at {LOCAL_PATH}")

# -----------------------------
# Run Artifact Extraction with file-level progress
# -----------------------------
# -----------------------------
# Run Artifact Extraction with progress
# -----------------------------
extractor = SemanticArtifactExtractor()

print(f"Extracting artifacts from repo '{REPO_NAME}'...")
# Use tqdm just to indicate extraction in progress
with tqdm(total=1, desc="Extracting Artifacts", ncols=100) as pbar:
    all_artifacts = extractor.extract_from_repo(LOCAL_PATH, REPO_NAME)
    pbar.update(1)

# -----------------------------
# Save artifacts to JSON
# -----------------------------
output_file = os.path.join(BASE_DIR, f"{REPO_NAME}_artifacts.json")
with open(output_file, "w") as f:
    json.dump(all_artifacts, f, indent=2)

print(f"Extraction complete! Artifacts saved to {output_file}")

