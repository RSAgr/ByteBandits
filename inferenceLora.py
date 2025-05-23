import sys
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Load base model and tokenizer
base_model = "EleutherAI/gpt-neo-125M"
tokenizer = AutoTokenizer.from_pretrained(base_model)
model = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=torch.float32)

# Load LoRA fine-tuned weights
#model = PeftModel.from_pretrained(model, "./lora-output")

import os
script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory where inferenceLora.py resides
lora_path = os.path.join(script_dir, "lora-output")
model = PeftModel.from_pretrained(model, lora_path)


# import os
# lora_path = os.path.abspath("./lora-output")
# model = PeftModel.from_pretrained(model, lora_path)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

raw_input = sys.stdin.read()
try:
    data = json.loads(raw_input)
    prompt = data["prompt"]
except Exception as e:
    json.dump({"error": f"Invalid input format: {str(e)}"}, sys.stdout)
    sys.exit(1)

# Tokenize and prepare input
#inputs = tokenizer(prompt, return_tensors="pt").to(device)
inputs = tokenizer(prompt, return_tensors="pt").to(device)

# try:
#     with torch.no_grad():
#         output = model.generate(
#             **inputs,
#             max_new_tokens=200,
#             do_sample=False,
#             temperature=0.0,
#             top_k=0,
#             top_p=1.0,
#             pad_token_id=tokenizer.eos_token_id,
#         )
    
#     decoded = tokenizer.decode(output[0], skip_special_tokens=True)
#     completion = decoded[len(prompt):].strip()  # Remove echoed prompt

#     json.dump({"response": completion}, sys.stdout)
# except Exception as e:
#     json.dump({"error": f"Inference error: {str(e)}"}, sys.stdout)
#     sys.exit(1)

# Generate output
try:
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=128,
            do_sample=True,
            temperature=0.5,
            top_k=20,
            top_p=0.7,
            pad_token_id=tokenizer.eos_token_id,
            # **inputs,
            # max_new_tokens=200,
            # do_sample=False,
            # pad_token_id=tokenizer.eos_token_id,
        )
    completion = tokenizer.decode(output[0], skip_special_tokens=True)
    json.dump({"response": completion}, sys.stdout)
except Exception as e:
    json.dump({"error": f"Inference error: {str(e)}"}, sys.stdout)
    sys.exit(1)

# import sys
# import json
# import torch
# from transformers import AutoTokenizer, AutoModelForCausalLM
# from peft import PeftModel
# import os

# # Load base model and tokenizer
# base_model = "EleutherAI/gpt-neo-125M"
# tokenizer = AutoTokenizer.from_pretrained(base_model)
# model = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=torch.float32)

# # Load LoRA fine-tuned weights
# script_dir = os.path.dirname(os.path.abspath(__file__))
# lora_path = os.path.join(script_dir, "lora-output")
# model = PeftModel.from_pretrained(model, lora_path)

# # Move model to CPU or GPU
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model = model.to(device)

# # Read prompt from stdin
# raw_input = sys.stdin.read()
# try:
#     data = json.loads(raw_input)
#     prompt = data["prompt"].strip()
# except Exception as e:
#     json.dump({"error": f"Invalid input format: {str(e)}"}, sys.stdout)
#     sys.exit(1)

# # Tokenize and prepare input
# inputs = tokenizer(prompt, return_tensors="pt").to(device)

# # Generate output (greedy decoding for stability)
# try:
#     with torch.no_grad():
#         output_ids = model.generate(
#             **inputs,
#             max_new_tokens=200,
#             do_sample=False,                  # Deterministic output
#             temperature=0.0,                  # Greedy decoding
#             top_k=0,
#             top_p=1.0,
#             pad_token_id=tokenizer.eos_token_id,
#         )
    
#     # Decode and trim the echoed prompt from the beginning
#     decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
#     completion = decoded[len(prompt):].strip()

#     json.dump({"response": completion}, sys.stdout)
# except Exception as e:
#     json.dump({"error": f"Inference error: {str(e)}"}, sys.stdout)
#     sys.exit(1)
