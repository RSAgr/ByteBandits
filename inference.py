import sys
import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

import os
from pathlib import Path

model_path = Path(__file__).parent / "codet5Algorand"
tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
model = AutoModelForSeq2SeqLM.from_pretrained(str(model_path), local_files_only=True)

#model_path = os.path.abspath("./codet5-algorand")

# Load locally fine-tuned model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path, local_files_only=True)

# Load the fine-tuned model and tokenizer once
# model_path = "./codet5-algorand"
# tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
# model = AutoModelForSeq2SeqLM.from_pretrained(model_path, local_files_only=True)

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def generate_response(instruction):
    # Tokenize input
    inputs = tokenizer(instruction, return_tensors="pt", truncation=True, padding=True).to(device)

    # Generate output
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=1024,
            do_sample=True,
            temperature=0.9,
            num_return_sequences=1
        )

    # Decode and return result
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result

if __name__ == "__main__":
    for line in sys.stdin:
        try:
            request = json.loads(line)
            instruction = request["prompt"]

            inputs = tokenizer(instruction, return_tensors="pt", truncation=True, padding=True).to(device)

            with torch.no_grad():
                outputs = model.generate(**inputs, max_length=1024, do_sample=True, temperature=0.9, num_return_sequences=1)

            result = tokenizer.decode(outputs[0], skip_special_tokens=True)

            print(json.dumps({ "response": result }))
            sys.stdout.flush()

        except Exception as e:
            print(json.dumps({ "error": str(e) }))
            sys.stdout.flush()

# Accept input from stdin (loop for future scalability)
# for line in sys.stdin:
#     try:
#         data = json.loads(line)
#         prompt = data.get("prompt", "")
#         if not prompt:
#             continue

#         response = generate_response(prompt)
#         print(json.dumps({ "response": response }))
#         sys.stdout.flush()

#     except Exception as e:
#         print(json.dumps({ "error": str(e) }))
#         sys.stdout.flush()
