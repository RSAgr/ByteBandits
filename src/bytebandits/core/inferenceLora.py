import sys
import json
import torch
import os
from transformers import AutoTokenizer, AutoModelForCausalLM

# Initialize device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load base model and tokenizer
base_model = "EleutherAI/gpt-neo-125M"
tokenizer = AutoTokenizer.from_pretrained(base_model)
model = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=torch.float32).to(device)

# Try to load LoRA fine-tuned weights if available
try:
    from peft import PeftModel
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lora_path = os.path.join(script_dir, "lora-output")
    
    if os.path.exists(lora_path):
        print(f"[INFO] Loading LoRA weights from {lora_path}", file=sys.stderr)
        model = PeftModel.from_pretrained(model, lora_path).to(device)
    else:
        print("[WARNING] LoRA weights not found. Using base model without fine-tuning.", file=sys.stderr)
except Exception as e:
    print(f"[WARNING] Could not load LoRA weights: {str(e)}. Using base model.", file=sys.stderr)


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
    system_prompt = """You are a Python code generator that responds only with code.
    For simple instructions, provide only the exact code needed.
    Do not include any explanations, comments, or additional text.
    
    Examples:
    Instruction: print 5
    Response: print(5)
    
    Instruction: create a function to add two numbers
    Response: def add(a, b):\n    return a + b
    
    Instruction: print hello world
    Response: print("Hello, World!")
    
    Important: For simple tasks like printing numbers or strings, 
    only provide the exact code needed without any additional context.
    """
    
    # Format the prompt more clearly
    instruction = prompt.lower().strip()
    
    # Handle simple print requests directly
    if instruction.startswith('print ') or instruction.startswith('display '):
        # Extract what needs to be printed
        to_print = instruction.split('print ')[1] if 'print ' in instruction else instruction.split('display ')[1]
        # Remove any trailing punctuation or whitespace
        to_print = to_print.strip(' .,!?;:')
        
        # For numbers
        if to_print.isdigit():
            completion = f"print({to_print})"
        # For simple strings without spaces
        elif to_print.replace('_', '').isalnum():
            completion = f"print('{to_print}')"
        # For more complex strings
        else:
            completion = f'print("{to_print}")'
            
        json.dump({"response": completion}, sys.stdout, ensure_ascii=False)
        sys.exit(0)
    
    # For other cases, use the model
    full_prompt = f"{system_prompt}\n\nInstruction: {instruction}\nResponse:\n"
    
    # Tokenize the new prompt
    inputs = tokenizer(full_prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=300,           # Increased for code generation
            do_sample=True,              # Enable sampling for better quality
            temperature=0.3,             # Lower temperature for more focused output
            top_k=30,                    # Consider top 30 tokens
            top_p=0.95,                  # Nucleus sampling with 95% probability mass
            num_beams=1,                 # Use greedy search for now
            pad_token_id=tokenizer.eos_token_id,
            no_repeat_ngram_size=3,      # Prevent 3-gram repetition
            early_stopping=True,         # Stop generation when complete
            length_penalty=1.5,          # Encourage longer, more complete code
            repetition_penalty=1.2,      # Discourage repetition
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
