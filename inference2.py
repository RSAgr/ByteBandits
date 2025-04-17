from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Load model & tokenizer
model_path = "./codet5Algorand"
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path, local_files_only=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# Exact same prompt used in training
instruction = "Write a PyTeal clear state program."
inputs = tokenizer(instruction, return_tensors="pt", truncation=True, padding=True).to(device)

# Greedy decoding
with torch.no_grad():
    outputs = model.generate(**inputs, max_length=128, do_sample=False)

# Decode
result = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("\n📜 Output:\n", result)
