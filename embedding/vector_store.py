# embedding/vector_store.py
import chromadb

class VectorStore:
    """
    A wrapper around ChromaDB for storing and updating code embeddings.
    """

    def __init__(self, collection_name="code_chunks", persist_dir="chroma_data"):
        # Use the new PersistentClient API
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        print(f"✅ Initialized ChromaDB collection '{collection_name}' at {persist_dir}")

    def add_chunk(self, chunk_data, embedding):
        """
        Add a single code chunk and its embedding to the collection.
        """
        self.collection.add(
            ids=[chunk_data["chunk_id"]],
            documents=[chunk_data["chunk"]],
            metadatas=[{
                "repo": chunk_data["repo"],
                "path": chunk_data["path"],
                "language": chunk_data["language"],
                "chunk_type": chunk_data["chunk_type"]
            }],
            embeddings=[embedding.tolist()]
        )

    def update_chunk(self, chunk_data, embedding):
        """
        Update existing chunk embedding (delete old + re-add new).
        """
        self.delete_chunk(chunk_data["chunk_id"])
        self.add_chunk(chunk_data, embedding)

    def delete_chunk(self, chunk_id):
        """
        Delete a chunk from the collection by ID.
        """
        self.collection.delete(ids=[chunk_id])

    def query_similar(self, code_embedding, top_k=5):
        """
        Search for top-k semantically similar chunks.
        """
        return self.collection.query(
            query_embeddings=[code_embedding.tolist()],
            n_results=top_k
        )

    def persist(self):
        """
        Save the collection to disk.
        (In the new API, this is automatic, but you can still call this
        if you want explicit checkpoints.)
        """
        print("✅ Chroma persistence is automatic; no manual save required.")
