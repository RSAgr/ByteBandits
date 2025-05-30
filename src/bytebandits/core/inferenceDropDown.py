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

# Move model to CPU or GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Read prompt from stdin
raw_input = sys.stdin.read()
try:
    data = json.loads(raw_input)
    prompt = data["prompt"]
except Exception as e:
    json.dump({"error": f"Invalid input format: {str(e)}"}, sys.stdout)
    sys.exit(1)

# Common Python completions for dropdown
COMMON_COMPLETIONS = [
    "import ",
    "def ",
    "class ",
    "for ",
    "while ",
    "if ",
    "else:",
    "elif ",
    "try:",
    "except ",
    "finally:",
    "with ",
    "return ",
    "yield ",
    "from ",
    "as ",
    "lambda ",
    "assert ",
    "raise ",
    "pass",
    "break",
    "continue"
]

# Tokenize and prepare input
try:
    # Check if we should use common completions (for empty or very short prompts)
    if len(prompt.strip()) < 3:
        json.dump({"suggestions": COMMON_COMPLETIONS}, sys.stdout)
        sys.exit(0)
    
    # For longer prompts, use the model
    system_prompt = """You are a helpful Python code completion assistant. 
    Provide ONLY code completions (no explanations) for the given code context.
    Return each completion on a new line. Only include the completion text, not the prompt.
    """
    
    full_prompt = f"{system_prompt}\n\nCode context: {prompt}\nCompletions:\n"
    
    inputs = tokenizer(full_prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=50,
            do_sample=True,
            temperature=0.7,
            top_k=30,
            top_p=0.9,
            num_return_sequences=5,
            pad_token_id=tokenizer.eos_token_id,
            no_repeat_ngram_size=2,
        )
    
    # Decode and process suggestions
    completions = set()
    for out in output:
        text = tokenizer.decode(out, skip_special_tokens=True)
        # Extract only the new completion part
        completion = text[len(full_prompt):].strip()
        # Split by newlines and clean up
        for line in completion.split('\n'):
            line = line.strip()
            if line and len(line) > 1:  # Filter out very short completions
                completions.add(line)
    
    # If we didn't get good completions, fall back to common ones
    if not completions:
        completions = set(COMMON_COMPLETIONS)
    
    # Convert to list and limit number of suggestions
    suggestions = list(completions)[:8]  # Max 8 suggestions
    
    # Ensure we always return at least some completions
    if not suggestions:
        suggestions = COMMON_COMPLETIONS[:5]
    
    json.dump({"suggestions": suggestions}, sys.stdout)
    
except Exception as e:
    print(f"Error in dropdown completion: {str(e)}", file=sys.stderr)
    # Fallback to common completions on error
    json.dump({"suggestions": COMMON_COMPLETIONS[:5]}, sys.stdout)
    sys.exit(1)

    # Decode and extract new text only (removing echoed prompt)
    


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
