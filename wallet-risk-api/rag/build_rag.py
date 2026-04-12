import json
import faiss
import pickle
import numpy as np

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

with open('rag/scam_patterns.json', 'r') as file:
    data = json.load(file)

if not data:
    print("No data found. Exiting.")
    exit()    

def combine_fields(item):
    text = f"{item['pattern']} {item['type']} {item['description']}"
    return text.lower()

texts = [combine_fields(item) for item in data]

if len(texts) == 0:
    print("No valid texts to encode.")
    exit()

documents = []

for item in data:
    text = combine_fields(item)

    documents.append({
        "text": text,
        "metadata": item
    })

texts = [doc["text"] for doc in documents]

#VECTOR EMBEDDING

vectors = model.encode(texts, convert_to_tensor=False)

print(f"Number of vectors generated: {len(vectors)}")
print(f"Dimension of each vector: {vectors[0].shape}")

#FAISS

embeddings = np.array(vectors, dtype=np.float32)

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings) 

D, I = index.search(vectors, k=5)

print("Index size:", index.ntotal)

# SAVE FAISS INDEX
faiss.write_index(index, "rag/faiss_index.bin")

with open("rag/patterns.pkl", "wb") as f:
    pickle.dump(documents, f)

print("Saved index and metadata successfully")
