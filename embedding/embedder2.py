# import json
# import numpy as np
# from typing import List, Dict, Tuple
# import anthropic
# from sklearn.metrics.pairwise import cosine_similarity


# class CodeChunkEmbedder:
#     """
#     A plug-and-play Python module for embedding and querying code chunks.
#     Uses Claude AI for semantic understanding and cosine similarity for retrieval.
#     """

#     def __init__(self, model: str = "claude-sonnet-4-20250514"):
#         """
#         Initialize the embedder with Anthropic API client.
        
#         Args:
#             model: Claude model to use for semantic representation
#         """
#         self.client = anthropic.Anthropic()
#         self.model = model
#         self.chunks = []
#         self.embeddings = []
#         self.semantic_reps = []

#     def add_chunks(self, chunks: List[Dict[str, str]]) -> None:
#         """
#         Add code chunks to the embedder.
        
#         Args:
#             chunks: List of dicts with keys: 'id', 'text', 'context' (optional)
#         """
#         self.chunks = chunks
#         print(f"✓ Added {len(chunks)} chunks")

#     def embed_chunks(self) -> None:
#         """
#         Generate semantic embeddings for all chunks using Claude API.
#         """
#         print(f"\n📊 Embedding {len(self.chunks)} chunks...")
#         self.embeddings = []
#         self.semantic_reps = []

#         for idx, chunk in enumerate(self.chunks):
#             print(f"  Processing chunk {idx + 1}/{len(self.chunks)}...", end="\r")
            
#             text = chunk.get('text', '')
#             context = chunk.get('context', '')
            
#             prompt = f"""Generate a concise semantic representation (2-3 sentences) of this code chunk for similarity matching:

# Code: {text}
# Context: {context}

# Focus on what the code does functionally and its purpose."""

#             response = self.client.messages.create(
#                 model=self.model,
#                 max_tokens=200,
#                 messages=[
#                     {"role": "user", "content": prompt}
#                 ]
#             )
            
#             semantic_rep = response.content[0].text
#             self.semantic_reps.append(semantic_rep)
            
#             # Generate embedding vector
#             embedding = self._generate_embedding(semantic_rep)
#             self.embeddings.append(embedding)

#         print(f"\n✓ Successfully embedded {len(self.embeddings)} chunks")

#     def _generate_embedding(self, text: str) -> np.ndarray:
#         """
#         Convert text to a numerical embedding vector.
#         Uses word frequency in a 50-dimensional space.
        
#         Args:
#             text: Text to embed
            
#         Returns:
#             50-dimensional numpy array
#         """
#         words = text.lower().split()
#         vector = np.zeros(50)
        
#         for i, word in enumerate(words):
#             if word:
#                 char_code = ord(word[0])
#                 index = (char_code + i) % 50
#                 vector[index] += 1
        
#         return vector

#     def query(self, query_text: str, top_k: int = 3, threshold: float = 0.1) -> List[Dict]:
#         """
#         Search for chunks similar to the query.
        
#         Args:
#             query_text: Query string
#             top_k: Number of top results to return
#             threshold: Minimum similarity score (0-1)
            
#         Returns:
#             List of dicts with chunk info and similarity scores
#         """
#         if not self.embeddings:
#             raise ValueError("No embeddings found. Call embed_chunks() first.")
        
#         if not query_text.strip():
#             raise ValueError("Query cannot be empty.")
        
#         # Generate query embedding
#         query_embedding = self._generate_embedding(query_text)
        
#         # Calculate similarities
#         embeddings_array = np.array(self.embeddings)
#         similarities = cosine_similarity([query_embedding], embeddings_array)[0]
        
#         # Create results
#         results = []
#         for idx, similarity in enumerate(similarities):
#             if similarity >= threshold:
#                 results.append({
#                     'id': self.chunks[idx]['id'],
#                     'text': self.chunks[idx]['text'],
#                     'context': self.chunks[idx].get('context', ''),
#                     'semantic': self.semantic_reps[idx],
#                     'similarity': float(similarity)
#                 })
        
#         # Sort by similarity and return top_k
#         results.sort(key=lambda x: x['similarity'], reverse=True)
#         return results[:top_k]

#     def batch_query(self, queries: List[str], top_k: int = 3) -> Dict[str, List[Dict]]:
#         """
#         Perform multiple queries at once.
        
#         Args:
#             queries: List of query strings
#             top_k: Number of top results per query
            
#         Returns:
#             Dict mapping query to results
#         """
#         results = {}
#         for query in queries:
#             results[query] = self.query(query, top_k)
#         return results

#     def save_embeddings(self, filepath: str) -> None:
#         """
#         Save embeddings to a JSON file.
        
#         Args:
#             filepath: Path to save file
#         """
#         data = {
#             'chunks': self.chunks,
#             'semantic_reps': self.semantic_reps,
#             'embeddings': [emb.tolist() for emb in self.embeddings]
#         }
        
#         with open(filepath, 'w') as f:
#             json.dump(data, f, indent=2)
        
#         print(f"✓ Saved embeddings to {filepath}")

#     def load_embeddings(self, filepath: str) -> None:
#         """
#         Load embeddings from a JSON file.
        
#         Args:
#             filepath: Path to load file
#         """
#         with open(filepath, 'r') as f:
#             data = json.load(f)
        
#         self.chunks = data['chunks']
#         self.semantic_reps = data['semantic_reps']
#         self.embeddings = [np.array(emb) for emb in data['embeddings']]
        
#         print(f"✓ Loaded {len(self.chunks)} chunks from {filepath}")


# # Example usage and testing
# if __name__ == "__main__":
#     # Sample code chunks from Todo List Application
#     sample_chunks = [
#         {
#             'id': 'Main_main_0',
#             'text': 'public static void main(String[] args) { TodoList toDoList = new TodoList(); toDoList.start(); }',
#             'context': 'Entry point of application'
#         },
#         {
#             'id': 'Task_class_0',
#             'text': 'public class Task { private String id; private String title; private LocalDate dueDate; private String status; private String projectName; }',
#             'context': 'Task data model with properties'
#         },
#         {
#             'id': 'TodoList_start_0',
#             'text': 'public void start() { showApplicationTitle(); while (TodoList.applicationRunning) { showAvailableActions(); int actionNumber = readAction(); executeAction(actionNumber); } }',
#             'context': 'Main application loop'
#         },
#         {
#             'id': 'DateSorting_execute_2',
#             'text': 'Collections.sort(entries, new Comparator<Map.Entry<String, Task>>() { ... }); TodoList.tasks.clear(); entries.forEach((entry) -> { TodoList.tasks.put(entry.getKey(), entry.getValue()); });',
#             'context': 'Sorting tasks by date'
#         },
#         {
#             'id': 'TodoList_execute_1',
#             'text': 'public void executeAction(int actionNumber) { switch (actionNumber) { case Actions.ADD_TASK: ... case Actions.REMOVE_TASK: ... } }',
#             'context': 'Action dispatcher switch statement'
#         },
#     ]

#     # Initialize embedder
#     print("🚀 Initializing Code Chunk Embedder...\n")
#     embedder = CodeChunkEmbedder()

#     # Add chunks
#     embedder.add_chunks(sample_chunks)

#     # Embed chunks
#     embedder.embed_chunks()

#     # Example queries
#     print("\n" + "="*60)
#     print("TESTING QUERIES")
#     print("="*60)

#     test_queries = [
#         "how to sort tasks by date",
#         "main application entry point",
#         "task properties and fields",
#         "handle different actions",
#     ]

#     for query_text in test_queries:
#         print(f"\n🔍 Query: '{query_text}'")
#         print("-" * 60)
        
#         results = embedder.query(query_text, top_k=2)
        
#         if results:
#             for rank, result in enumerate(results, 1):
#                 print(f"\n  [{rank}] Similarity: {result['similarity']:.2%}")
#                 print(f"      ID: {result['id']}")
#                 print(f"      Context: {result['context']}")
#                 print(f"      Semantic: {result['semantic'][:80]}...")
#         else:
#             print("  No results found.")

#     # Save embeddings for later use
#     print("\n" + "="*60)
#     embedder.save_embeddings('code_embeddings.json')
#     print("\n✨ Testing complete!")


import json
import numpy as np
from typing import List, Dict, Tuple
import requests
from sklearn.metrics.pairwise import cosine_similarity


class CodeChunkEmbedder:
    """
    A plug-and-play Python module for embedding and querying code chunks.
    Uses Ollama (local LLM) for semantic understanding and cosine similarity for retrieval.
    Install Ollama from: https://ollama.ai
    Run: ollama pull mistral (or any other model)
    Then start: ollama serve
    """

    def __init__(self, model: str = "mistral", ollama_url: str = "http://localhost:11434"):
        """
        Initialize the embedder with Ollama local LLM.
        
        Args:
            model: Ollama model name (default: mistral)
            ollama_url: URL where Ollama is running
        """
        self.model = model
        self.ollama_url = ollama_url
        self.chunks = []
        self.embeddings = []
        self.semantic_reps = []
        
        # Check if Ollama is running
        try:
            response = requests.get(f"{ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                print(f"✓ Connected to Ollama at {ollama_url}")
            else:
                print(f"⚠ Ollama may not be running properly")
        except requests.exceptions.ConnectionError:
            print(f"⚠ Warning: Could not connect to Ollama at {ollama_url}")
            print("  Make sure Ollama is running: ollama serve")
            print("  And model is available: ollama pull mistral")

    def add_chunks(self, chunks: List[Dict[str, str]]) -> None:
        """
        Add code chunks to the embedder.
        
        Args:
            chunks: List of dicts with keys: 'id', 'text', 'context' (optional)
        """
        self.chunks = chunks
        print(f"✓ Added {len(chunks)} chunks")

    def embed_chunks(self) -> None:
        """
        Generate semantic embeddings for all chunks using Ollama.
        """
        print(f"\n📊 Embedding {len(self.chunks)} chunks...")
        self.embeddings = []
        self.semantic_reps = []

        for idx, chunk in enumerate(self.chunks):
            print(f"  Processing chunk {idx + 1}/{len(self.chunks)}...", end="\r")
            
            text = chunk.get('text', '')
            context = chunk.get('context', '')
            
            prompt = f"""Generate a concise semantic representation (2-3 sentences) of this code chunk for similarity matching:

Code: {text}
Context: {context}

Focus on what the code does functionally and its purpose."""

            try:
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    semantic_rep = response.json()['response']
                    self.semantic_reps.append(semantic_rep)
                    
                    # Generate embedding vector
                    embedding = self._generate_embedding(semantic_rep)
                    self.embeddings.append(embedding)
                else:
                    print(f"\n✗ Error from Ollama: {response.status_code}")
                    print(f"  Make sure model '{self.model}' is downloaded: ollama pull {self.model}")
                    raise Exception("Ollama request failed")
                    
            except requests.exceptions.Timeout:
                print(f"\n✗ Timeout: Ollama took too long to respond")
                raise
            except requests.exceptions.ConnectionError:
                print(f"\n✗ Connection Error: Could not reach Ollama at {self.ollama_url}")
                print(f"  Start Ollama with: ollama serve")
                raise

        print(f"\n✓ Successfully embedded {len(self.embeddings)} chunks")

    def _generate_embedding(self, text: str) -> np.ndarray:
        """
        Convert text to a numerical embedding vector.
        Uses word frequency in a 50-dimensional space.
        
        Args:
            text: Text to embed
            
        Returns:
            50-dimensional numpy array
        """
        words = text.lower().split()
        vector = np.zeros(50)
        
        for i, word in enumerate(words):
            if word:
                char_code = ord(word[0])
                index = (char_code + i) % 50
                vector[index] += 1
        
        return vector

    def query(self, query_text: str, top_k: int = 3, threshold: float = 0.1) -> List[Dict]:
        """
        Search for chunks similar to the query.
        
        Args:
            query_text: Query string
            top_k: Number of top results to return
            threshold: Minimum similarity score (0-1)
            
        Returns:
            List of dicts with chunk info and similarity scores
        """
        if not self.embeddings:
            raise ValueError("No embeddings found. Call embed_chunks() first.")
        
        if not query_text.strip():
            raise ValueError("Query cannot be empty.")
        
        # Generate query embedding
        query_embedding = self._generate_embedding(query_text)
        
        # Calculate similarities
        embeddings_array = np.array(self.embeddings)
        similarities = cosine_similarity([query_embedding], embeddings_array)[0]
        
        # Create results
        results = []
        for idx, similarity in enumerate(similarities):
            if similarity >= threshold:
                results.append({
                    'id': self.chunks[idx]['id'],
                    'text': self.chunks[idx]['text'],
                    'context': self.chunks[idx].get('context', ''),
                    'semantic': self.semantic_reps[idx],
                    'similarity': float(similarity)
                })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]

    def batch_query(self, queries: List[str], top_k: int = 3) -> Dict[str, List[Dict]]:
        """
        Perform multiple queries at once.
        
        Args:
            queries: List of query strings
            top_k: Number of top results per query
            
        Returns:
            Dict mapping query to results
        """
        results = {}
        for query in queries:
            results[query] = self.query(query, top_k)
        return results

    def save_embeddings(self, filepath: str) -> None:
        """
        Save embeddings to a JSON file.
        
        Args:
            filepath: Path to save file
        """
        data = {
            'chunks': self.chunks,
            'semantic_reps': self.semantic_reps,
            'embeddings': [emb.tolist() for emb in self.embeddings]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Saved embeddings to {filepath}")

    def load_embeddings(self, filepath: str) -> None:
        """
        Load embeddings from a JSON file.
        
        Args:
            filepath: Path to load file
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.chunks = data['chunks']
        self.semantic_reps = data['semantic_reps']
        self.embeddings = [np.array(emb) for emb in data['embeddings']]
        
        print(f"✓ Loaded {len(self.chunks)} chunks from {filepath}")


# Example usage and testing
if __name__ == "__main__":
    print("="*60)
    print("CODE CHUNK EMBEDDINGS - OLLAMA VERSION")
    print("="*60)
    print("\nSetup Instructions:")
    print("1. Install Ollama: https://ollama.ai")
    print("2. In a terminal, run: ollama serve")
    print("3. In another terminal, download a model:")
    print("   ollama pull mistral")
    print("   (or: ollama pull neural-chat, ollama pull orca-mini)")
    print("\nThen run this script.")
    print("="*60 + "\n")

    # Sample code chunks from Todo List Application
    sample_chunks = [
        {
            'id': 'Main_main_0',
            'text': 'public static void main(String[] args) { TodoList toDoList = new TodoList(); toDoList.start(); }',
            'context': 'Entry point of application'
        },
        {
            'id': 'Task_class_0',
            'text': 'public class Task { private String id; private String title; private LocalDate dueDate; private String status; private String projectName; }',
            'context': 'Task data model with properties'
        },
        {
            'id': 'TodoList_start_0',
            'text': 'public void start() { showApplicationTitle(); while (TodoList.applicationRunning) { showAvailableActions(); int actionNumber = readAction(); executeAction(actionNumber); } }',
            'context': 'Main application loop'
        },
        {
            'id': 'DateSorting_execute_2',
            'text': 'Collections.sort(entries, new Comparator<Map.Entry<String, Task>>() { ... }); TodoList.tasks.clear(); entries.forEach((entry) -> { TodoList.tasks.put(entry.getKey(), entry.getValue()); });',
            'context': 'Sorting tasks by date'
        },
        {
            'id': 'TodoList_execute_1',
            'text': 'public void executeAction(int actionNumber) { switch (actionNumber) { case Actions.ADD_TASK: ... case Actions.REMOVE_TASK: ... } }',
            'context': 'Action dispatcher switch statement'
        },
    ]

    # Initialize embedder
    print("🚀 Initializing Code Chunk Embedder...\n")
    embedder = CodeChunkEmbedder(model="mistral")

    # Add chunks
    embedder.add_chunks(sample_chunks)

    # Embed chunks
    try:
        embedder.embed_chunks()
    except Exception as e:
        print(f"\n✗ Error during embedding: {e}")
        print("\nMake sure Ollama is running!")
        print("Start it with: ollama serve")
        exit(1)

    # Example queries
    print("\n" + "="*60)
    print("TESTING QUERIES")
    print("="*60)

    test_queries = [
        "how to sort tasks by date",
        "main application entry point",
        "task properties and fields",
        "handle different actions",
    ]

    for query_text in test_queries:
        print(f"\n🔍 Query: '{query_text}'")
        print("-" * 60)
        
        results = embedder.query(query_text, top_k=2)
        
        if results:
            for rank, result in enumerate(results, 1):
                print(f"\n  [{rank}] Similarity: {result['similarity']:.2%}")
                print(f"      ID: {result['id']}")
                print(f"      Context: {result['context']}")
                print(f"      Semantic: {result['semantic'][:80]}...")
        else:
            print("  No results found.")

    # Save embeddings for later use
    print("\n" + "="*60)
    embedder.save_embeddings('code_embeddings.json')
    print("\n✨ Testing complete!")