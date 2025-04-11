from datasets import load_dataset
from transformers import AutoTokenizer
from tokenizers import Tokenizer
from transformers import AutoModelForSeq2SeqLM, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq


dataset = load_dataset("json", data_files={"train": "./data/ipop.jsonl"})

# No need to split

# Load model and tokenizer
model_name = "Salesforce/codet5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Tokenize
def preprocess(example):
    inputs = tokenizer(example["instruction"], padding="max_length", truncation=True, max_length=128)
    targets = tokenizer(example["output"], padding="max_length", truncation=True, max_length=512)
    inputs["labels"] = targets["input_ids"]
    return inputs

tokenized = dataset.map(preprocess, batched=True)

# Training args
args = Seq2SeqTrainingArguments(
    output_dir="./codet5-algorand",
    #evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    num_train_epochs=5,
    save_total_limit=1,
    predict_with_generate=True,
    logging_dir="./logs",
)

# Trainer
trainer = Seq2SeqTrainer(
    model=model,
    args=args,
    train_dataset=tokenized["train"],
    tokenizer=tokenizer,
    data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
)

# Train!
trainer.train()

print("Saving model...")
trainer.save_model("codet5_algorand")
tokenizer.save_pretrained("codet5_algorand")
print("Saved to ./codet5_algorand")



