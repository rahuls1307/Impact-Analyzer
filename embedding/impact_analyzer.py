"""
impact_analyzer.py — Computes semantic impact of code changes using embeddings and an LLM.
Works with ChromaDB, CodeEmbedder, and RepoWatcher.
"""

import os
import json
from chromadb import Client
from chromadb.config import Settings
from embedding.embedder import CodeEmbedder

# You can switch to Gemini or GPT later. This stub uses OpenAI-compatible models.
from openai import OpenAI

class ImpactAnalyzer:
    def __init__(
        self,
        chroma_dir="chroma_db",
        collection_name="code_chunks",
        model_name="microsoft/graphcodebert-base",
        llm_model="gpt-4o-mini"
    ):
        self.embedder = CodeEmbedder(model_name)
        self.client = Client(Settings(persist_directory=chroma_dir))
        self.collection = self.client.get_or_create_collection(collection_name)
        self.llm = OpenAI()  # assumes OPENAI_API_KEY or compatible key is set
        print(f"🧠 ImpactAnalyzer initialized with {llm_model}")

        self.llm_model = llm_model

    def analyze_change(self, changed_chunk):
        """
        Given one changed chunk (dict from chunker.py or watcher),
        find semantically similar chunks and analyze their relationship via LLM.
        """
        print(f"🔍 Analyzing impact for: {changed_chunk['chunk_id']}")

        # Step 1: Compute embedding for changed chunk
        embedding = self.embedder.embed(changed_chunk["chunk"])

        # Step 2: Query Chroma for semantically similar code
        similar = self.collection.query(
            query_embeddings=[embedding],
            n_results=5,
            include=["documents", "metadatas", "distances"]
        )

        if not similar["documents"]:
            print("⚠️ No similar chunks found.")
            return None

        # Step 3: Format context for LLM
        context_chunks = []
        for doc, meta, dist in zip(similar["documents"][0], similar["metadatas"][0], similar["distances"][0]):
            context_chunks.append(
                f"[{meta['repo']}] {meta['path']} ({meta['language']}):\n{doc}\n(Similarity: {1 - dist:.2f})"
            )

        context_text = "\n\n".join(context_chunks)
        changed_code = changed_chunk["chunk"]

        # Step 4: Ask the LLM to reason about impact
        prompt = f"""
You are a software impact analysis assistant.

A code change occurred in repo `{changed_chunk['repo']}` at path `{changed_chunk['path']}`.
Here is the modified code block:

{changed_code}

Here are the most semantically similar code regions across the codebase:

{context_text}

Question: Based on this, which components or functions could be affected by this change and why?
Give a concise reasoning (2-4 sentences) explaining dependencies or logical impacts.
"""

        response = self.llm.chat.completions.create(
            model=self.llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        result = response.choices[0].message.content
        print(f"💡 Impact analysis:\n{result}\n")
        return result

    def batch_analyze(self, changed_chunks):
        """
        Run impact analysis for multiple changed chunks.
        """
        results = {}
        for chunk in changed_chunks:
            impact = self.analyze_change(chunk)
            results[chunk["chunk_id"]] = impact
        return results


# Example usage
if __name__ == "__main__":
    with open("changed_chunks.json", "r") as f:
        changed = json.load(f)

    analyzer = ImpactAnalyzer()
    results = analyzer.batch_analyze(changed)
    with open("impact_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("✅ Saved impact analysis to impact_results.json")