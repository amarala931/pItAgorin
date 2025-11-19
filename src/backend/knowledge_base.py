import chromadb
from chromadb.utils import embedding_functions
import uuid
from config.settings import DB_PATH

class KnowledgeBase:
    def __init__(self):
        """
        Initializes the connection to the ChromaDB database.
        If the data folder does not exist, ChromaDB will create it automatically.
        """
        # Persistent Client: Saves the data to the hard drive (data/chroma_store folder)
        self.client = chromadb.PersistentClient(path=DB_PATH)
        
        # Embedding Function: We use a light and fast model (all-MiniLM-L6-v2)
        # This model converts text into lists of numbers that represent its meaning.
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Collection: It's like a "table" in SQL. We store all knowledge here.
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base", # Translated from base_conocimiento
            embedding_function=self.embedding_fn
        )

    def add_document(self, text, topic, source="manual"):
        """
        Saves a new text fragment to the database.
        
        Args:
            text (str): The content to memorize.
            topic (str): The topic/theme (e.g., 'History', 'Technical') for later filtering.
            source (str): Origin of the data (filename or 'manual').
        """
        if not text or not text.strip():
            return # Don't save empty text

        self.collection.add(
            documents=[text],
            metadatas=[{"topic": topic, "source": source}], # Translated keys
            ids=[str(uuid.uuid4())] # Generate a unique ID for each fragment
        )

    def query_db(self, query, topics, n_results=3):
        """
        Searches for relevant information based on a question and topics.
        
        Args:
            query (str): The user's question or prompt.
            topics (list): List of allowed topics (e.g., ['Finance']).
            n_results (int): How many text fragments to retrieve.
            
        Returns:
            str: A string with all found information joined, or "" if nothing is found.
        """
        # If the user did not select any topics, we do not search to save resources
        # (Or you could remove this if to search the ENTIRE database by default)
        if not topics:
            return ""
        
        # Perform the semantic search
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"topic": {"$in": topics}} # Critical filter: Only search in chosen topics
        )
        
        # Process results: Chroma returns a list of lists.
        # Check if anything was found.
        if results['documents'] and results['documents'][0]:
            # Join the found fragments with newlines
            joined_context = "\n\n".join(results['documents'][0])
            return joined_context
        
        return ""

    def get_topics(self):
        """
        Retrieves the list of all unique topics existing in the DB.
        Useful for populating the GUI selector.
        """
        # Get only the metadata from the entire collection
        data = self.collection.get(include=['metadatas'])
        
        unique_topics = set()
        for meta in data['metadatas']:
            if 'topic' in meta: # Translated key
                unique_topics.add(meta['topic'])
                
        return list(sorted(unique_topics))