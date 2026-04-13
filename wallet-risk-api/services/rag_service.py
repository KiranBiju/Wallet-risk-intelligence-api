import faiss
import pickle
import numpy as np
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


model = SentenceTransformer("all-MiniLM-L6-v2")


try:
    index = faiss.read_index("rag/faiss_index.bin")
    logger.info("[RAG] FAISS index loaded successfully")
except Exception as e:
    logger.error(f"[RAG ERROR] Failed to load FAISS index: {e}")
    index = None


try:
    with open("rag/patterns.pkl", "rb") as f:
        patterns = pickle.load(f)
    logger.info(f"[RAG] Loaded {len(patterns)} patterns")
except Exception as e:
    logger.error(f"[RAG ERROR] Failed to load patterns: {e}")
    patterns = []


def retrieve_patterns(feature_text: str, top_k: int = 3):

    try:
        if not index or not patterns:
            logger.warning("[RAG] Index or patterns not available")
            return []

        query_text = feature_text.lower().strip()

        query_vector = np.array(
            model.encode([query_text]),
            dtype=np.float32
        )

        
        distances, indices = index.search(query_vector, top_k)

        results = []

        for dist, idx in zip(distances[0], indices[0]):

            if idx == -1:
                continue

            if idx < 0 or idx >= len(patterns):
                continue

            similarity = 1 / (1 + float(dist))

            if similarity < 0.3 and len(results) >= 1:
                continue

            pattern_data = patterns[idx]

            if isinstance(pattern_data, dict) and "metadata" in pattern_data:
               meta = pattern_data["metadata"]
            else:
               meta = pattern_data

            pattern_name = meta.get("pattern")
            pattern_type = meta.get("type")
            description = meta.get("description")           

            if not pattern_name:
                continue

            pattern_data = patterns[idx]

            if "metadata" in pattern_data:
                meta = pattern_data["metadata"]
            else:
                meta = pattern_data

            results.append({
            "pattern": pattern_name,
               "type": pattern_type,
               "description": description,
               "similarity": round(similarity, 3)
            })

        results = sorted(results, key=lambda x: x["similarity"], reverse=True)[:3]

        
        logger.info(f"[RAG] Retrieved patterns: {results}")

        return results

    except Exception as e:
        logger.error(f"[RAG ERROR] Retrieval failed: {e}", exc_info=True)
        return []