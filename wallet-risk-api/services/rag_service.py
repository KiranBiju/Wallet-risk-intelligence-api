import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("rag/faiss_index.bin")

with open("rag/patterns.pkl", "rb") as f:
    patterns = pickle.load(f)


def retrieve_patterns(feature_text, top_k=3):

    query_text = feature_text.lower()

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

        results.append({
            "pattern": patterns[idx]["pattern"],
            "type": patterns[idx]["type"],
            "description": patterns[idx]["description"],
            "score": float(dist)
        })

    return results