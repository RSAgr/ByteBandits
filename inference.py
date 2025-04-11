from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Load the fine-tuned model and tokenizer
model_path = "./codet5-algorand"

tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path, local_files_only=True)

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Sample input instruction
instruction = "Write a PyTeal clear state program."  #  use a known training example first
print("Instruction:\n", instruction)

# Tokenize input
inputs = tokenizer(instruction, return_tensors="pt", truncation=True, padding=True).to(device)

#  Debug: print tokenized input
print(" Tokenized Input IDs:\n", inputs["input_ids"])
print("Token 203 is:", tokenizer.decode([203]))

# Generate output
with torch.no_grad():
    outputs = model.generate(**inputs, max_length=128, do_sample=True, top_k=50, top_p=0.95)


# Debug: print raw output token IDs
print(" Raw Output IDs:\n", outputs)

# Decode and print
result = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("\n Generated Smart Contract:\n")
print(result)
