import os
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
from peft import get_peft_model, LoraConfig, TaskType, PeftModel
import json

# Load model and tokenizer
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32)

model.config.use_cache = False  # Disable cache for training

# Setup PEFT (LoRA)
peft_path = "./trainedModel"
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

model.print_trainable_parameters()

# Freeze base model parameters, only LoRA params trainable
for name, param in model.named_parameters():
    if "lora" not in name:
        param.requires_grad = False
    else:
        param.requires_grad = True

model.print_trainable_parameters()
num_trainable = sum(p.requires_grad for p in model.parameters())
if num_trainable == 0:
    raise RuntimeError("No parameters are trainable! Check LoRA setup.")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

model.train()

# Load dataset
def load_jsonl_dataset(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]
    return Dataset.from_list([
        {"text": f"Input:\n{ex['instruction']}\nOutput:\n{ex['output']}"}
        for ex in lines
    ])

# NOTE: This path must exist locally with proper .jsonl data
sample_path = "data/samples.jsonl"
if not os.path.exists(sample_path):
    print("Sample data file not found")
else:
    dataset = load_jsonl_dataset(sample_path)
    dataset = dataset.select(range(0, 10))

    def tokenize(example):
        tokenized = tokenizer(example["text"], truncation=True, padding="max_length", max_length=256)
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized

    tokenized_dataset = dataset.map(tokenize, batched=True)
    print(tokenized_dataset[0])

    # Training Arguments
    training_args = TrainingArguments(
        output_dir="./trainedModel",
        per_device_train_batch_size=1,
        num_train_epochs=10,
        save_steps=99999999,
        save_total_limit=2,
        learning_rate=1e-4,
        logging_dir="./logs",
        logging_steps=1000,
        gradient_checkpointing=False,  # Disable for debugging
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

    trainer.train()
    trainer.save_model("./trainedModel")
    print("Model training complete and saved to ./trainedModel")
