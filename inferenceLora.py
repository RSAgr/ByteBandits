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
    # Create a more specific prompt for code generation
    system_prompt = """You are a helpful AI assistant that generates Python code. 
    When given an instruction, respond with only the code that implements it.
    Do not include any explanations or additional text.
    Example:
    Instruction: generate a function to add two numbers
    Response:
    def add(a, b):
        return a + b
    """
    
    full_prompt = f"{system_prompt}\n\nInstruction: {prompt}\nResponse:\n"
    
    # Tokenize the new prompt
    inputs = tokenizer(full_prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=256,  # Increased for code generation
            do_sample=False,     # Use greedy decoding for more deterministic output
            temperature=0.7,     # Slight randomness
            top_k=50,            # Consider top 50 tokens
            top_p=0.9,           # Nucleus sampling
            pad_token_id=tokenizer.eos_token_id,
            no_repeat_ngram_size=2,  # Prevent repetition
        )
    
    # Decode and clean up the output
    completion = tokenizer.decode(output[0], skip_special_tokens=True)
    
    # Remove the input prompt from the output
    completion = completion[len(full_prompt):].strip()
    
    # Ensure we only get the code block if it exists
    if '```python' in completion:
        code = completion.split('```python')[1].split('```')[0].strip()
        completion = code
    elif '```' in completion:
        code = completion.split('```')[1].split('```')[0].strip()
        if code.startswith('python'):
            code = code[6:].strip()
        completion = code
    
    json.dump({"response": completion}, sys.stdout)
    
except Exception as e:
    error_msg = f"Inference error: {str(e)}"
    print(f"Error: {error_msg}", file=sys.stderr)
    json.dump({"error": error_msg}, sys.stdout)
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
