import json
import faiss
import pickle
import numpy as np

from sentence_transformers import SentenceTransformer

print("Building RAG Index...")

#LOAD MODEL

model = SentenceTransformer("all-MiniLM-L6-v2")

#LOAD DATA
with open("rag/scam_patterns.json", "r") as file:
    data = json.load(file)

if not data:
    print("No data found. Exiting.")
    exit()


#TEXT BUILDER

def build_text(item):
    return (
        f"Pattern: {item.get('pattern', '')}. "
        f"Type: {item.get('type', '')}. "
        f"Severity: {item.get('severity', '')}. "
        f"Description: {item.get('description', '')}."
    ).lower()


documents = []
texts = []

for item in data:

    #VALIDATION

    if not item.get("pattern"):
        continue

    text = build_text(item)

    documents.append({
        "id": item.get("id"),
        "pattern": item.get("pattern"),
        "type": item.get("type"),
        "severity": item.get("severity"),
        "description": item.get("description"),
        "text": text
    })

    texts.append(text)


if len(texts) == 0:
    print("No valid texts to encode.")
    exit()


#EMBEDDINGS

vectors = model.encode(texts, convert_to_numpy=True)

print(f"Vectors: {len(vectors)}")
print(f"Dimension: {vectors.shape}")


#FAISS INDEX

dimension = vectors.shape[1]

index = faiss.IndexFlatL2(dimension)
index.add(vectors)

print("Index size:", index.ntotal)


faiss.write_index(index, "rag/faiss_index.bin")

with open("rag/patterns.pkl", "wb") as f:
    pickle.dump(documents, f)

print("Saved index + metadata successfully")