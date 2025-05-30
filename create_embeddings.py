import json
import os
from sentence_transformers import SentenceTransformer
import numpy as np # For converting embeddings to list for JSON serialization

# Configuration
SAMPLES_FILE = os.path.join("data", "samples.jsonl")
VECTOR_SAMPLES_FILE = os.path.join("data", "vector_samples.jsonl")
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2' # Use the same model as your main script

def load_raw_samples(filepath):
    """Loads instructions and outputs from a .jsonl file."""
    samples = []
    if not os.path.exists(filepath):
        print(f"Error: Samples file not found at {filepath}. Cannot create embeddings.", file=sys.stderr)
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                samples.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from line: {line.strip()} - {e}", file=sys.stderr)
    return samples

def create_and_store_embeddings():
    print(f"Loading SentenceTransformer model: {EMBEDDING_MODEL_NAME}...")
    try:
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("Model loaded.")
    except Exception as e:
        print(f"Error loading SentenceTransformer model: {e}", file=sys.stderr)
        print("Please ensure you have internet access for the first download or model is cached.")
        return

    raw_samples = load_raw_samples(SAMPLES_FILE)
    if not raw_samples:
        print("No raw samples to process. Exiting.")
        return

    instructions = [s.get("instruction", "") for s in raw_samples]
    print(f"Encoding {len(instructions)} instructions...")
    # Encode in batches for efficiency
    instruction_embeddings = model.encode(instructions, convert_to_tensor=False) # Convert to numpy array directly

    print(f"Storing embeddings to {VECTOR_SAMPLES_FILE}...")
    with open(VECTOR_SAMPLES_FILE, 'w', encoding='utf-8') as f_out:
        for i, sample in enumerate(raw_samples):
            # Convert numpy array embedding to a list for JSON serialization
            sample['embedding'] = instruction_embeddings[i].tolist()
            f_out.write(json.dumps(sample) + '\n')
    print("Embeddings stored successfully.")

if __name__ == "__main__":
    # Ensure the 'data' directory exists
    os.makedirs("data", exist_ok=True)
    create_and_store_embeddings()