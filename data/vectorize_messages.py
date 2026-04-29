import json
import pandas as pd
from sentence_transformers import SentenceTransformer
import pathlib

# Base path for messages
base_path = pathlib.Path(__file__).parent / "bulk-export"

# Get all subfolders in the base path
subfolders = [f for f in base_path.iterdir() if f.is_dir()]

# Get all files in the subfolders
files = []
for subfolder in subfolders:
    files.extend(subfolder.glob("*.json"))

# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Get all conversations from files. Make conversations overlap by n messages in to preserve context.
n = 5
conversations = []
for file in files:
    with open(file) as f:
        data = pd.DataFrame(json.load(f))
        for i in range(len(data)):
            conversation = ""
            for j in range(n):
                if i + j < len(data):
                    conversation += data.iloc[i + j].content + " ... "
            conversations.append(conversation.strip())

# Create embeddings for each conversation using the SentenceTransformer model and store them in a dictionary
conversation_embedding_list = model.encode(conversations, show_progress_bar=True)
conversation_embeddings = {conv: embedding for conv, embedding in zip(conversations, conversation_embedding_list)}

# Save the embeddings
with open("repo/data/conversation_embeddings.json", "w") as f:
    json.dump({conv: embedding.tolist() for conv, embedding in conversation_embeddings.items()}, f)