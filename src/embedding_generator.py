"""
Embedding Generator using SentenceTransformers
"""
import numpy as np
from typing import List, Optional
import hashlib

class EmbeddingGenerator:
    """Generate embeddings for semantic matching"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.dimension = 384  # Default for MiniLM
    
    def _load_model(self):
        """Lazy load model"""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                print(f"Loading embedding model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                # Get actual dimension
                test_emb = self.model.encode(["test"])
                self.dimension = len(test_emb[0])
                print(f"Model loaded ({self.dimension} dimensions)")
            except ImportError:
                raise ImportError("Install sentence-transformers: pip install sentence-transformers")
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text"""
        try:
            self._load_model()
            
            # Clean and limit text
            text_clean = self._preprocess_text(text, max_length=1000)
            
            # Generate embedding
            embedding = self.model.encode([text_clean])[0]
            
            if not isinstance(embedding, np.ndarray):
                embedding = np.array(embedding, dtype=np.float32)
            
            return embedding
            
        except Exception as e:
            print(f"Embedding error: {e}")
            return self._fallback_embedding(text)
    
    def _preprocess_text(self, text: str, max_length: int = 1000) -> str:
        """Preprocess text for embedding"""
        import re
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Truncate if too long
        if len(text) > max_length:
            half = max_length // 2
            text = text[:half] + " [...] " + text[-half:]
        
        return text
    
    def _fallback_embedding(self, text: str) -> np.ndarray:
        """Fallback when model fails"""
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        seed = int(text_hash[:8], 16)
        
        np.random.seed(seed)
        embedding = np.random.randn(self.dimension).astype(np.float32)
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def get_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings"""
        if emb1 is None or emb2 is None:
            return 0.0
        
        # Ensure same shape
        if emb1.shape != emb2.shape:
            min_dim = min(len(emb1), len(emb2))
            emb1 = emb1[:min_dim]
            emb2 = emb2[:min_dim]
        
        dot = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot / (norm1 * norm2))