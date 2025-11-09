"""
repo_watcher.py — Monitors cloned repositories for updates and re-embeds changed files.
Works with chunker.py and embedder.py in the P1 pipeline.
"""

import os
import time
import json
import hashlib
from datetime import datetime
from git import Repo
from embedding.chunker import chunk_file
from embedding.embedder import CodeEmbedder
from chromadb import Client
from chromadb.config import Settings


class RepoWatcher:
    def __init__(self, repo_paths, chroma_dir="chroma_db", poll_interval=60):
        """
        repo_paths: list of local repo paths to monitor.
        chroma_dir: path to Chroma persistent directory.
        poll_interval: how often (seconds) to check for changes.
        """
        self.repo_paths = repo_paths
        self.poll_interval = poll_interval
        self.embedder = CodeEmbedder()
        self.db = Client(Settings(persist_directory=chroma_dir))
        self.collection = self.db.get_or_create_collection("code_chunks")
        self.hash_store_path = "file_hashes.json"
        self.hash_store = self._load_hash_store()

    # ---------- Hash Utilities ----------
    def _hash_file(self, path):
        """Compute MD5 hash of file contents."""
        try:
            with open(path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None

    def _load_hash_store(self):
        if os.path.exists(self.hash_store_path):
            with open(self.hash_store_path, "r") as f:
                return json.load(f)
        return {}

    def _save_hash_store(self):
        with open(self.hash_store_path, "w") as f:
            json.dump(self.hash_store, f, indent=2)

    # ---------- Core Watch Logic ----------
    def _get_changed_files(self, repo_path):
        """Detect files that are new or modified since last check."""
        changed = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                path = os.path.join(root, file)
                ext = os.path.splitext(path)[1]
                if ext not in [".py", ".java", ".js", ".cpp", ".go", ".sql", ".ddl"]:
                    continue

                new_hash = self._hash_file(path)
                old_hash = self.hash_store.get(path)
                if new_hash and new_hash != old_hash:
                    changed.append(path)
                    self.hash_store[path] = new_hash
        return changed

    def _remove_deleted_files(self):
        """Clean up hashes for files that no longer exist."""
        to_delete = [f for f in self.hash_store if not os.path.exists(f)]
        for f in to_delete:
            del self.hash_store[f]

    # ---------- Main Update Loop ----------
    def run_once(self):
        """Run one scan iteration (for testing or scheduled mode)."""
        total_changes = 0
        for repo_path in self.repo_paths:
            repo_name = os.path.basename(repo_path)
            repo = Repo(repo_path)
            print(f"\n🔍 Checking {repo_name} at {datetime.now().strftime('%H:%M:%S')}")

            repo.remote().fetch()
            if repo.head.is_detached:
                print(f"⚠️ Skipping detached HEAD in {repo_name}")
                continue

            changed_files = self._get_changed_files(repo_path)
            if not changed_files:
                print(f"✅ No changes detected in {repo_name}")
                continue

            print(f"🧩 {len(changed_files)} changed files found in {repo_name}")

            for path in changed_files:
                chunks = chunk_file(path, repo_name)
                if not chunks:
                    continue

                for chunk in chunks:
                    embedding = self.embedder.embed(chunk["chunk"])
                    self.collection.upsert(
                        ids=[chunk["chunk_id"]],
                        embeddings=[embedding],
                        metadatas=[{
                            "repo": repo_name,
                            "path": path,
                            "language": chunk["language"],
                            "chunk_type": chunk["chunk_type"]
                        }],
                        documents=[chunk["chunk"]]
                    )
            total_changes += len(changed_files)

        self._remove_deleted_files()
        self._save_hash_store()
        print(f"💾 Updated embeddings for {total_changes} modified files.\n")

    def run_forever(self):
        """Continuously poll repos for changes."""
        print("🚀 RepoWatcher started. Monitoring for updates...\n")
        while True:
            try:
                self.run_once()
            except Exception as e:
                print(f"⚠️ Error during watch cycle: {e}")
            time.sleep(self.poll_interval)
