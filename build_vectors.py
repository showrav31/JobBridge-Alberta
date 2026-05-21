# build_vectors.py
import sqlite3
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

print("Loading jobs from database...")
conn = sqlite3.connect('data/jobs.db')
df = pd.read_sql("SELECT * FROM jobs", conn)
conn.close()

def create_job_text(row):
    return f"""
Job Title: {row.get('title', 'Not specified')}
Company: {row.get('company', 'Not specified')}
Location: {row.get('location', 'Not specified')}
City: {row.get('city', 'Not specified')}
Province: {row.get('province', 'Not specified')}
Salary: {row.get('salary', 'Not specified')}
Education Required: {row.get('education', 'Not specified')}
Experience Required: {row.get('experience', 'Not specified')}
Responsibilities: {row.get('responsibilities', 'Not specified')}
"""

print("Loading AI model... (first time takes 1-2 mins to download)")
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Setting up vector database...")
client = chromadb.PersistentClient(path="./data/vectordb")
collection = client.get_or_create_collection("jobs")

print("Embedding all 5,132 jobs... (this takes 5-10 minutes, please wait)")
for i, row in df.iterrows():
    text = create_job_text(row)
    embedding = model.encode(text).tolist()
    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[str(row['id'])],
        metadatas={
            "title": str(row.get('title', '')),
            "company": str(row.get('company', '')),
            "location": str(row.get('location', '')),
            "city": str(row.get('city', '')),
            "province": str(row.get('province', ''))
        }
    )
    if i % 500 == 0:
        print(f"  Progress: {i}/5132 jobs embedded...")

print("✅ Done! Vector database saved to data/vectordb/")