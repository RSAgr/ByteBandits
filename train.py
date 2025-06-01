import os
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
)
from datasets import load_dataset, Dataset
from peft import get_peft_model, LoraConfig, TaskType
import json

# Load model and tokenizer
# model_name = "deepseek-ai/deepseek-coder-1.3b-base"
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32)

# Enable LoRA
# peft_config = LoraConfig(
#     task_type=TaskType.CAUSAL_LM,
#     inference_mode=False,
#     r=8,
#     lora_alpha=16,
#     lora_dropout=0.05,
# )
# model = get_peft_model(model, peft_config)

from peft import PeftModel, PeftConfig, get_peft_model, LoraConfig, TaskType

peft_path = "./trainedModel"

# if os.path.exists(peft_path):
#     # ✅ Load existing LoRA adapter (continue training)
#     print("🔁 Loading existing LoRA weights...")
#     model = PeftModel.from_pretrained(model, peft_path)
# else:
#     # 🆕 No existing LoRA adapter found — create a new one
#     print("🆕 No previous LoRA weights found. Initializing new adapter...")
#     peft_config = LoraConfig(
#         task_type=TaskType.CAUSAL_LM,
#         inference_mode=False,
#         r=8,
#         lora_alpha=16,
#         lora_dropout=0.05,
#     )
#     model = get_peft_model(model, peft_config)

if os.path.exists(os.path.join(peft_path, "adapter_config.json")):
    print("🔁 Loading existing LoRA weights...")
    model = PeftModel.from_pretrained(model, peft_path)
else:
    print("🆕 No previous LoRA weights found. Initializing new adapter...")
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
    )
    model = get_peft_model(model, peft_config)


model.train()
model.requires_grad_(True)

# Load dataset
def load_jsonl_dataset(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]
    return Dataset.from_list([
        {"text": f"Input:\n{ex['instruction']}\nOutput:\n{ex['output']}"}
        for ex in lines
    ])

dataset = load_jsonl_dataset(r"data\samples.jsonl")
dataset = dataset.select(range(0,10)) 

# Tokenize and add labels
def tokenize(example):
    tokenized = tokenizer(example["text"], truncation=True, padding="max_length", max_length=512)
    #tokenized = tokenizer(example["text"], truncation=True, padding="max_length", max_length=512)
    tokenized["labels"] = tokenized["input_ids"].copy()  # Required for loss computation
    return tokenized

tokenized_dataset = dataset.map(tokenize, batched=True)

print(tokenized_dataset[0])


# Training config
training_args = TrainingArguments(
    output_dir="./trainedModel",
    per_device_train_batch_size=1,
    num_train_epochs=10,
    save_steps=100,
    save_total_limit=2,
    learning_rate=1e-4,
    logging_dir="./logs",
    logging_steps=10,
    gradient_checkpointing=False,  # Disable if no GPU
    fp16=False,
    push_to_hub=False,
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)
logging_steps=1,
logging_first_step=True,

trainer.train()
