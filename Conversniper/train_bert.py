# train_bert.py
import pandas as pd
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import torch
import accelerate  # Add this import

# Load synthetic dataset
df = pd.read_csv("D:/Intern/Survey_sparrow/Conversniper/social_synthetic_data.csv")
df["label"] = df["sentiment"].map({"Positive": 1, "Neutral": 0, "Negative": 2})
dataset = Dataset.from_pandas(df[["text", "label"]])

# Split train/test
train_test = dataset.train_test_split(test_size=0.2)
train_dataset = train_test["train"]
test_dataset = train_test["test"]

# Tokenizer
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")

def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)

train_dataset = train_dataset.map(tokenize_function, batched=True)
test_dataset = test_dataset.map(tokenize_function, batched=True)

# Model
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=3)

# Training args
training_args = TrainingArguments(
    output_dir="./conversniper_bert",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=10,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

# Train
trainer.train()

# Save
model.save_pretrained("D:/Intern/Survey_sparrow/Conversniper/conversniper_bert")
tokenizer.save_pretrained("D:/Intern/Survey_sparrow/Conversniper/conversniper_bert")
print("BERT trained and saved as conversniper_bert!")