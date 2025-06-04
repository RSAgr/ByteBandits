import sys
import json
import os
import torch
import re
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# with open("data/samples.jsonl", "r", encoding="utf-8") as f:
#     for i, line in enumerate(f, 1):
#         try:
#             json.loads(line)
#         except Exception as e:
#             print(f"Line {i}: {e}")

# === RAG SETUP ===
SAMPLES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "samples.jsonl")
NUM_CONTEXT_SAMPLES = 2

def load_samples(filepath):
    samples = []
    if not os.path.exists(filepath):
        print(f"Warning: Samples file not found at {filepath}. No context will be injected.", file=sys.stderr)
        return samples
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                samples.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}", file=sys.stderr)
    return samples

def find_matching_samples(user_instruction, samples, top_n=NUM_CONTEXT_SAMPLES):
    user_instruction_lower = user_instruction.lower()
    matches = []
    for sample in samples:
        sample_instruction = sample.get("instruction", "").lower()
        shared_words = set(user_instruction_lower.split()) & set(sample_instruction.split())
        if shared_words:
            matches.append((len(shared_words), sample))
    matches.sort(key=lambda x: x[0], reverse=True)
    return [sample for _, sample in matches[:top_n]]

# === SLM SETUP ===
base_model = "EleutherAI/gpt-neo-125M"
tokenizer = AutoTokenizer.from_pretrained(base_model)
model = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=torch.float32)

lora_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lora-output")
model = PeftModel.from_pretrained(model, lora_path)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# === Read Prompt from Stdin ===
raw_input = sys.stdin.read()
try:
    data = json.loads(raw_input)
    prompt = data["prompt"].strip()
except Exception as e:
    json.dump({"error": f"Invalid input format: {str(e)}"}, sys.stdout)
    sys.exit(1)

# === RAG: Inject Context ===
all_samples = load_samples(SAMPLES_FILE)
context_examples_str = ""

if all_samples:
    matching_samples = find_matching_samples(prompt, all_samples, NUM_CONTEXT_SAMPLES)
    for i, sample in enumerate(matching_samples):
        context_examples_str += f"\nContext Example {i+1}:\nInstruction: {sample.get('instruction', '')}\nResponse:\n{sample.get('output', '')}\n"

# === Final Prompt for SLM ===
system_prompt = "You are a helpful coding assistant. Provide only code for the following task."
final_prompt = f"{system_prompt}\n{context_examples_str}\n\nInstruction: {prompt}\nResponse:\n"

# === Run Inference ===
try:
    inputs = tokenizer(final_prompt, return_tensors="pt").to(device)
    #inputs = tokenizer(final_prompt, return_tensors="pt", truncation=True, max_length=2048).to(device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=200,
            do_sample=True,
            temperature=0.5,
            top_k=20,
            top_p=0.7,
            pad_token_id=tokenizer.eos_token_id,
        )
    decoded = tokenizer.decode(output[0], skip_special_tokens=True)
    completion = decoded[len(final_prompt):].strip()

    # Remove any code block formatting if it was copied from training data
    match = re.search(r"```(?:[Pp]ython)?\s*([\s\S]+?)```", completion)
    if match:
        completion = match.group(1).strip()

    json.dump({"response": completion}, sys.stdout)
except Exception as e:
    json.dump({"error": f"Inference error: {str(e)}"}, sys.stdout)
    sys.exit(1)
