"""
build_career_graph.py
Builds a skill <-> job-title graph from jobs.db and trains a GCN
encoder to produce embeddings for career pathway recommendations.

Run this ONCE after setup_db.py — like build_vectors.py.
"""

import sqlite3
import pandas as pd
import numpy as np
import pickle
import re
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv


# ── Skill Vocabulary ──────────────────────────────────────────────
# Keyword-matched against job responsibilities and resumes.
SKILL_VOCAB = [
    # Technology & IT
    "python", "java", "javascript", "sql", "html", "css", "react", "node.js",
    "machine learning", "data analysis", "data science", "cloud computing",
    "aws", "azure", "docker", "kubernetes", "git", "api", "software development",
    "web development", "database management", "cybersecurity", "networking",
    "linux", "c++", "c#", "excel", "power bi", "tableau", "devops",

    # Trades & Technical
    "carpentry", "welding", "electrical", "plumbing", "hvac", "construction",
    "blueprint reading", "power tools", "safety compliance", "mechanical repair",
    "equipment maintenance", "automotive repair", "cnc machining", "millwright",

    # Healthcare
    "patient care", "nursing", "first aid", "cpr", "medical terminology",
    "clinical", "healthcare administration", "pharmacy", "phlebotomy",
    "electronic health records",

    # Business & Finance
    "accounting", "bookkeeping", "financial analysis", "budgeting",
    "auditing", "taxation", "payroll", "quickbooks", "financial reporting",
    "investment analysis", "risk management",

    # Management
    "leadership", "project management", "team management", "strategic planning",
    "operations management", "supervision", "staff scheduling", "budget management",
    "performance management", "change management",

    # Education
    "curriculum development", "classroom management", "lesson planning",
    "teaching", "tutoring", "special education", "student assessment",

    # Service & Retail
    "customer service", "sales", "cash handling", "inventory management",
    "merchandising", "retail operations", "point of sale",

    # Cross-category soft skills
    "communication", "problem solving", "time management", "teamwork",
    "critical thinking", "attention to detail", "organization", "adaptability",
]


def extract_skills_from_text(text, vocab=SKILL_VOCAB):
    """Find which vocabulary skills appear in a block of text."""
    text_lower = str(text).lower()
    found = []
    for skill in vocab:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)
    return found


def build_graph():
    print("Loading jobs from database...")
    conn = sqlite3.connect('data/jobs.db')
    df = pd.read_sql("SELECT * FROM jobs", conn)
    conn.close()

    job_titles = sorted(df['title'].str.lower().unique().tolist())
    jobtitle_to_idx = {t: i for i, t in enumerate(job_titles)}
    skill_to_idx = {s: i + len(job_titles) for i, s in enumerate(SKILL_VOCAB)}
    num_nodes = len(job_titles) + len(SKILL_VOCAB)

    print(f"Graph: {len(job_titles)} job-title nodes, {len(SKILL_VOCAB)} skill nodes")

    edges = set()
    job_to_skills = {t: set() for t in job_titles}

    print("Extracting skills from job postings...")
    for idx, row in df.iterrows():
        title = str(row['title']).lower()
        text = f"{title} {row.get('responsibilities', '')}"
        found_skills = extract_skills_from_text(text)
        job_idx = jobtitle_to_idx[title]
        for skill in found_skills:
            skill_idx = skill_to_idx[skill]
            edges.add((job_idx, skill_idx))
            edges.add((skill_idx, job_idx))
            job_to_skills[title].add(skill)
        if idx % 1000 == 0:
            print(f"  Processed {idx}/{len(df)} postings...")

    if not edges:
        raise RuntimeError("No skill-job edges found. Check SKILL_VOCAB matches your data.")

    edge_index = torch.tensor(list(zip(*edges)), dtype=torch.long)
    print(f"Built graph: {num_nodes} nodes, {len(edges)} directed edges")

    # ── Train GCN encoder (unsupervised link prediction) ──────────
    embedding_dim = 64
    node_embedding = nn.Embedding(num_nodes, embedding_dim)

    class GCNEncoder(nn.Module):
        def __init__(self, in_dim, hidden_dim, out_dim):
            super().__init__()
            self.conv1 = GCNConv(in_dim, hidden_dim)
            self.conv2 = GCNConv(hidden_dim, out_dim)

        def forward(self, x, edge_index):
            x = F.relu(self.conv1(x, edge_index))
            x = self.conv2(x, edge_index)
            return x

    encoder = GCNEncoder(embedding_dim, 64, 32)
    optimizer = torch.optim.Adam(
        list(node_embedding.parameters()) + list(encoder.parameters()), lr=0.01
    )

    all_edges = torch.tensor(list(edges), dtype=torch.long)
    num_pos = all_edges.shape[0]

    print("Training GCN encoder via link prediction (100 epochs)...")
    for epoch in range(100):
        optimizer.zero_grad()
        x = node_embedding.weight
        z = encoder(x, edge_index)

        pos_src = all_edges[:, 0]
        pos_dst = all_edges[:, 1]
        pos_score = (z[pos_src] * z[pos_dst]).sum(dim=1)

        neg_src = torch.randint(0, num_nodes, (num_pos,))
        neg_dst = torch.randint(0, num_nodes, (num_pos,))
        neg_score = (z[neg_src] * z[neg_dst]).sum(dim=1)

        scores = torch.cat([pos_score, neg_score])
        labels = torch.cat([torch.ones(num_pos), torch.zeros(num_pos)])
        loss = F.binary_cross_entropy_with_logits(scores, labels)

        loss.backward()
        optimizer.step()

        if epoch % 10 == 0:
            print(f"  Epoch {epoch}: loss = {loss.item():.4f}")

    print("Training complete!")

    with torch.no_grad():
        final_embeddings = encoder(node_embedding.weight, edge_index).numpy()

    with open('data/career_graph.pkl', 'wb') as f:
        pickle.dump({
            'embeddings': final_embeddings,
            'jobtitle_to_idx': jobtitle_to_idx,
            'skill_to_idx': skill_to_idx,
            'job_to_skills': job_to_skills,
            'skill_vocab': SKILL_VOCAB,
        }, f)

    print("✅ Saved data/career_graph.pkl — GNN career pathway system ready!")


if __name__ == "__main__":
    build_graph()