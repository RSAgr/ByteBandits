import sys
import json
import os
import google.generativeai as genai
import re
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np

# Set default model globally
DEFAULT_EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# Configure your API key
load_dotenv()  # Load environment variables from .env file

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
    json.dump({"error": "GEMINI_API_KEY environment variable not set"}, sys.stdout)
    sys.exit(1)

genai.configure(api_key=GOOGLE_API_KEY)

# --- Context Injection Setup ---
# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Use os.path.join to create a platform-independent path relative to the script
#SAMPLES_FILE = os.path.join(SCRIPT_DIR, "data", "samples.jsonl")
SAMPLES_FILE = os.path.join(SCRIPT_DIR, "data", "vector_samples.jsonl")
NUM_CONTEXT_SAMPLES = 5  # Number of top matching samples to include as context

def load_samples(filepath):
    """Loads instructions and outputs from a .jsonl file."""
    samples = []
    if not os.path.exists(filepath):
        # Print the exact path being checked for debugging
        print(f"Warning: Samples file not found at {filepath}. No context will be injected.", file=sys.stderr)
        return samples
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                samples.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from line: {line.strip()} - {e}", file=sys.stderr)
    return samples

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# def find_matching_samples(user_instruction, samples, model=DEFAULT_EMBEDDING_MODEL, top_n=5):
#     """
#     Finds the top-N samples most similar to the user's instruction
#     using cosine similarity of precomputed embeddings.
    
#     `samples` must contain 'embedding' key.
#     """
#     # Step 1: Encode only the user instruction
#     user_embedding = model.encode([user_instruction], normalize_embeddings=True)[0]
#     user_embedding = np.array(user_embedding).reshape(1, -1)

#     # Step 2: Load precomputed sample embeddings
#     sample_embeddings = np.array([sample["embedding"] for sample in samples])

#     # Step 3: Compute cosine similarities
#     similarities = cosine_similarity(user_embedding, sample_embeddings)[0]

#     # Step 4: Sort samples by similarity score
#     ranked_samples = sorted(zip(similarities, samples), key=lambda x: x[0], reverse=True)

#     return [sample for _, sample in ranked_samples[:top_n]]

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def find_matching_samples(user_instruction, samples, model=DEFAULT_EMBEDDING_MODEL, top_n=5, threshold=0.4):
    """
    Finds the top-N samples most similar to the user's instruction
    using cosine similarity of precomputed embeddings.

    Only returns samples with similarity >= `threshold`.

    Parameters:
        user_instruction (str): The input prompt or query.
        samples (list): List of dicts with 'embedding' keys.
        model: SentenceTransformer or similar embedding model.
        top_n (int): Max number of similar samples to return.
        threshold (float): Minimum similarity score to accept a sample.
    """
    # Step 1: Encode only the user instruction
    user_embedding = model.encode([user_instruction], normalize_embeddings=True)[0]
    user_embedding = np.array(user_embedding).reshape(1, -1)

    # Step 2: Load precomputed sample embeddings
    sample_embeddings = np.array([sample["embedding"] for sample in samples])

    # Step 3: Compute cosine similarities
    similarities = cosine_similarity(user_embedding, sample_embeddings)[0]

    # Step 4: Filter by threshold
    filtered = [(sim, sample) for sim, sample in zip(similarities, samples) if sim >= threshold]

    # Step 5: Sort and limit
    ranked_samples = sorted(filtered, key=lambda x: x[0], reverse=True)

    return [sample for _, sample in ranked_samples[:top_n]]


# def find_matching_samples(user_instruction, samples, top_n=NUM_CONTEXT_SAMPLES):
#     """
#     Finds samples that are most relevant to the user's instruction.
#     This is a simple keyword-based matching. For more robust matching,
#     consider using embeddings and similarity search.
#     """
#     matches = []
#     user_instruction_lower = user_instruction.lower()

#     # Simple keyword matching: count shared words
#     for sample in samples:
#         sample_instruction_lower = sample.get("instruction", "").lower()
#         shared_words = set(user_instruction_lower.split()) & set(sample_instruction_lower.split())
#         score = len(shared_words)
#         if score > 0:
#             matches.append((score, sample))

#     matches.sort(key=lambda x: x[0], reverse=True)
#     return [sample for score, sample in matches[:top_n]]

# Load all samples once
all_samples = load_samples(SAMPLES_FILE)

# === Read prompt from stdin ===
raw_input = sys.stdin.read()
try:
    data = json.loads(raw_input)
    prompt = data["prompt"]
except Exception as e:
    json.dump({"error": f"Invalid input format: {str(e)}"}, sys.stdout)
    sys.exit(1)

# === Build System Prompt and Full Prompt ===
system_prompt = """You are a helpful AI coding assistant for Algorand (blockchain) that generates Python code. If anyone asks for anything apart from python code, simply deny with an apology message.
When given an instruction, respond with only the code that implements it.
Do not include any explanations or additional text. 
A statless contract must contain logic() and not approval() or clear()
A stateful contract must contain approve() and clear()
Mode.Signature should be used for stateless contracts
Mode.Application should be used for Stateful contracts
"""

# Add general examples to the system prompt
general_examples = """Example 1:
Instruction: generate a function to add two numbers
Response:
def add(a, b):
    return a + b

Example 2:
Instruction: print hello world
Response:
print("Hello, World!")

Example 3:
Instruction: check if a number is prime
Response:
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True
"""

instruction = prompt.lower().strip()
if not instruction.startswith('generate') and not instruction.startswith('write'):
    instruction = f'generate code to {instruction}'

# --- Context Injection ---
context_examples_str = ""
context_chunks = []
if all_samples:
    matching_samples = find_matching_samples(instruction, all_samples,DEFAULT_EMBEDDING_MODEL, NUM_CONTEXT_SAMPLES)
    #matching_samples = find_matching_samples(instruction, all_samples, NUM_CONTEXT_SAMPLES)
    if matching_samples:
        context_examples_str = "\n\nHere are some relevant examples:\n"
        for i, sample in enumerate(matching_samples):
            context_examples_str += f"\nContext Example {i+1}:\n"
            context_examples_str += f"Instruction: {sample.get('instruction', 'N/A')}\n"
            context_examples_str += f"Response:\n{sample.get('output', 'N/A')}\n"
            # if(i==0 or i==1):
            #     print(context_examples_str)
            if i < 2:  # Store top two chunks
                context_chunks.append({
                    "instruction": sample.get("instruction", "N/A"),
                    "output": sample.get("output", "N/A")
                })
    else:
        print("No matching samples found for context injection.", file=sys.stderr)

# Combine system prompt, general examples, and context examples
full_prompt = f"{system_prompt}{general_examples}{context_examples_str}\n\nInstruction: {instruction}\nResponse:\n"

# === Call Gemini API ===
try:
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(full_prompt)
    completion = response.text.strip()

    # Clean output if inside code blocks
    # if '```python' in completion:
    #     code = completion.split('```python')[1].split('```')[0].strip()
    #     completion = code
    # elif '```Python' in completion:
    #     code = completion.split('```Python')[1].split('```')[0].strip()
    #     completion = code
    # elif '```' in completion:
    #     code = completion.split('```')[1].split('```')[0].strip()
    #     if code.startswith('python'):
    #         code = code[6:].strip()
    #     completion = code
    match = re.search(r"```(?:[Pp]ython)?\s*([\s\S]+?)```", completion)
    if match:
        completion = match.group(1).strip()
    context_display = ""
    for i, chunk in enumerate(context_chunks[:2]):  # Only show top 2
        context_display += f"=== Example {i+1} ===\n"
        context_display += f"Instruction: {chunk['instruction']}\n"
        context_display += f"Code:\n{chunk['output']}\n\n"

    result = {
        "response": completion,
        "context_chunks": context_display.strip()  # Now a formatted string
    }
    json.dump(result, sys.stdout)
    #json.dump({"response": completion}, sys.stdout)

except Exception as e:
    error_msg = f"Inference error: {str(e)}"
    print(f"Error: {error_msg}", file=sys.stderr)
    json.dump({"error": error_msg}, sys.stdout)
    sys.exit(1)