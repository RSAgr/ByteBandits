############This file is not been used, go to train.py#################

from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from datasets import load_dataset
import torch

# Load model and tokenizer
model_id = "deepseek-ai/deepseek-coder-1.3b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="cpu",  # Change to "auto" if you want GPU
    trust_remote_code=True
)

# Load dataset from JSONL file
dataset = load_dataset("json", data_files="./data/opip.jsonl", split="train")
print("Original Sample:", dataset[0])  # Debug print to verify format

# Tokenization function
def tokenize_and_add_labels(example):
    # Combine instruction and response into a formatted prompt
    prompt = f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['output']}"
    
    # Tokenize the prompt
    tokenized = tokenizer(
        prompt,
        truncation=True,
        padding="max_length",
        max_length=512,
    )

    # Set labels equal to input_ids for causal LM
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

# Apply tokenization to dataset
tokenized_dataset = dataset.map(tokenize_and_add_labels)
print("Tokenized Sample:", tokenized_dataset[0])  # Debug print to verify

# Training configuration
training_args = TrainingArguments(
    output_dir="./deepseek-finetune",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=1,
    num_train_epochs=1,
    logging_dir="./logs",
    save_total_limit=1,
    save_steps=1000,
)

# Define Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
)

# Train and save
trainer.train()
trainer.save_model("./deepseek-finetune")
tokenizer.save_pretrained("./deepseek-finetune")
model.config.save_pretrained("./deepseek-finetune")
