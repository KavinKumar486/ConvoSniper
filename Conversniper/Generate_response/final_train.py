# Import necessary libraries
import pandas as pd
from transformers import GPT2Tokenizer, GPT2LMHeadModel, AdamW
import torch
from torch.utils.data import Dataset, DataLoader

# Step 1: Define a custom dataset class for your CSV
class ResponseDataset(Dataset):
    def __init__(self, csv_file, tokenizer, max_length=128):
        # Load the CSV file
        self.data = pd.read_csv(csv_file)
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Ensure your CSV has 'Post' and 'Response' columns
        self.posts = self.data['Post'].tolist()
        self.responses = self.data['Response'].tolist()

    def __len__(self):
        return len(self.posts)

    def __getitem__(self, idx):
        # Combine post and response into one string with delimiters
        input_text = f"<|post|>{self.posts[idx]}<|response|>{self.responses[idx]}"
        
        # Tokenize the combined string
        encodings = self.tokenizer(
            input_text,
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )

        return {
            'input_ids': encodings['input_ids'].squeeze(),  # Remove extra dim
            'attention_mask': encodings['attention_mask'].squeeze()
        }

# Step 2: Set up the training function
def train_model(model, dataloader, epochs=3, device='cuda' if torch.cuda.is_available() else 'cpu'):
    model.to(device)
    optimizer = AdamW(model.parameters(), lr=5e-5)  # Learning rate for fine-tuning

    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for batch in dataloader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)

            # Forward pass
            outputs = model(input_ids, attention_mask=attention_mask, labels=input_ids)
            loss = outputs.loss
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch + 1}/{epochs}, Average Loss: {avg_loss:.4f}")

# Step 3: Main execution
if __name__ == "__main__":
    # Path to your CSV file (replace with your actual path)
    dataset_path = "D:\\Intern\\Survey_sparrow\\Conversniper\\Generate_response\\output.csv"  # e.g., "C:/Users/You/training_data.csv"

    # Load tokenizer and model
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')

    # GPT-2 needs a padding token (use EOS as pad)
    tokenizer.pad_token = tokenizer.eos_token

    # Load your dataset
    dataset = ResponseDataset(csv_file=dataset_path, tokenizer=tokenizer, max_length=128)
    dataloader = DataLoader(dataset, batch_size=8, shuffle=True)  # Batch size 8, tweak as needed

    # Train the model
    train_model(model, dataloader, epochs=3)

    # Save the trained model
    model.save_pretrained("D:\\Intern\\Survey_sparrow\\Conversniper")  # e.g., "./my_swaggy_model"
    tokenizer.save_pretrained("D:\\Intern\\Survey_sparrow\\Conversniper")
    print("Model training complete and saved!")