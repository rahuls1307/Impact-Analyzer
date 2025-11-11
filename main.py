# main.py
from embedding.chunker import clone_repo, process_repo, chunk_file
from embedding.vector_store import VectorStore
from embedding.embedder import CodeEmbedder
from embedding.embedder2 import CodeChunkEmbedder
import json

import os

def main():
    # ---------- SETUP ----------
    # test_repo_url = "https://github.com/kopaljain03/MediCare"  # example repo
    test_repo_url ="https://github.com/Sifaldin/Todo-List-Application-Java"
    test_file = "sample.py"  # local file for testing single file mode

    # Initialize embedder and vector store
    embedder = CodeEmbedder(model_name="microsoft/graphcodebert-base")
    vector_store = VectorStore(collection_name="code_chunks", persist_dir="chroma_data")

    # ---------- 1️⃣ Clone & process repository ----------
    print("\n=== Processing repository ===")
    repo_path = clone_repo(test_repo_url)
    chunks = process_repo(repo_path)
    print(f"Total chunks extracted: {len(chunks)}")
    # Storing chunks in a JSON file
    with open('output.json', 'w') as f:
        json.dump(chunks, f, indent=4)


    # Just show a few samples
    for i, c in enumerate(chunks[:3]):
        print(f"\nChunk {i+1}:")
        print(f"Path: {c['path']}")
        print(f"Type: {c['chunk_type']}")
        print(c['chunk'][:200], "...\n")

    embedder = CodeChunkEmbedder()
    embedder.add_chunks(chunks)
    embedder.embed_chunks()
    results = embedder.query("find chunks about sorting")
    print(results)
    embedder.save_embeddings('embeddings.json')
    embedder.load_embeddings('embeddings.json')

    # # ---------- 2️⃣ Embed & store ----------
    # print("\n=== Embedding & Storing first few chunks ===")
    # for chunk in chunks[:5]:
    #     emb = embedder.embed(chunk["chunk"])
    #     vector_store.add_chunk(chunk, emb)
    #     print(f"Stored chunk: {chunk['chunk_id']}")

    # # ---------- 3️⃣ Query similar code ----------
    # print("\n=== Query Similar ===")
    # query_snippet = "Function that adds a new task to the list"
    # query_emb = embedder.embed(query_snippet)
    # results = vector_store.query_similar(query_emb, top_k=3)
    # print("Query results:", results)

    # # ---------- 4️⃣ Test single file chunking ----------
    # if os.path.exists(test_file):
    #     print("\n=== Testing single file chunking ===")
    #     file_chunks = chunk_file(test_file)
    #     print(f"Extracted {len(file_chunks)} chunks from {test_file}")
    # else:
    #     print(f"\n⚠️ Skipping file test — '{test_file}' not found.")


if __name__ == "__main__":
    main()
