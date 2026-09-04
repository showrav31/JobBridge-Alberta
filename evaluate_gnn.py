"""
evaluate_gnn.py

Standalone evaluation script. Does NOT touch career_graph.pkl or your
live app in any way — it rebuilds a SEPARATE copy of the graph, holds
out 15% of real skill-job connections, trains a fresh model on the
remaining 85%, and checks whether it can correctly identify the
held-out real connections vs random fake ones it never saw.

This produces a legitimate held-out AUC score (Area Under the ROC
Curve) for your GNN — the standard evaluation metric for link
prediction. 0.5 = random guessing, 1.0 = perfect.

Run this once, note the printed score, and use it in your slides/brief.
It does not modify anything your app.py uses.
"""

import sqlite3
import pandas as pd
import random
import re
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from sklearn.metrics import roc_auc_score

from build_career_graph import SKILL_VOCAB, extract_skills_from_text


def build_full_edge_list():
    conn = sqlite3.connect('data/jobs.db')
    df = pd.read_sql("SELECT * FROM jobs", conn)
    conn.close()

    job_titles = sorted(df['title'].str.lower().unique().tolist())
    jobtitle_to_idx = {t: i for i, t in enumerate(job_titles)}
    skill_to_idx = {s: i + len(job_titles) for i, s in enumerate(SKILL_VOCAB)}
    num_nodes = len(job_titles) + len(SKILL_VOCAB)

    edges = set()
    for _, row in df.iterrows():
        title = str(row['title']).lower()
        text = f"{title} {row.get('responsibilities', '')}"
        found_skills = extract_skills_from_text(text, SKILL_VOCAB)
        job_idx = jobtitle_to_idx[title]
        for skill in found_skills:
            skill_idx = skill_to_idx[skill]
            edges.add((job_idx, skill_idx))
            edges.add((skill_idx, job_idx))

    return list(edges), num_nodes


class GCNEncoder(nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim):
        super().__init__()
        self.conv1 = GCNConv(in_dim, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, out_dim)

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        x = self.conv2(x, edge_index)
        return x


def evaluate():
    print("Rebuilding graph for evaluation (separate copy, app is untouched)...")
    all_edges, num_nodes = build_full_edge_list()
    random.shuffle(all_edges)

    split = int(len(all_edges) * 0.85)
    train_edges = all_edges[:split]
    test_edges = all_edges[split:]
    print(f"Training edges: {len(train_edges)}  |  Held-out test edges: {len(test_edges)}")

    train_edge_index = torch.tensor(list(zip(*train_edges)), dtype=torch.long)

    embedding_dim = 64
    node_embedding = nn.Embedding(num_nodes, embedding_dim)
    encoder = GCNEncoder(embedding_dim, 64, 32)
    optimizer = torch.optim.Adam(
        list(node_embedding.parameters()) + list(encoder.parameters()), lr=0.01
    )

    train_tensor = torch.tensor(train_edges, dtype=torch.long)
    num_pos = train_tensor.shape[0]

    print("Training on the 85% split only (held-out edges never seen)...")
    for epoch in range(100):
        optimizer.zero_grad()
        x = node_embedding.weight
        z = encoder(x, train_edge_index)

        pos_score = (z[train_tensor[:, 0]] * z[train_tensor[:, 1]]).sum(dim=1)
        neg_src = torch.randint(0, num_nodes, (num_pos,))
        neg_dst = torch.randint(0, num_nodes, (num_pos,))
        neg_score = (z[neg_src] * z[neg_dst]).sum(dim=1)

        scores = torch.cat([pos_score, neg_score])
        labels = torch.cat([torch.ones(num_pos), torch.zeros(num_pos)])
        loss = F.binary_cross_entropy_with_logits(scores, labels)
        loss.backward()
        optimizer.step()

        if epoch % 20 == 0:
            print(f"  Epoch {epoch}: loss = {loss.item():.4f}")

    print("Evaluating on held-out test edges the model never trained on...")
    with torch.no_grad():
        z = encoder(node_embedding.weight, train_edge_index)

        test_tensor = torch.tensor(test_edges, dtype=torch.long)
        pos_score = (z[test_tensor[:, 0]] * z[test_tensor[:, 1]]).sum(dim=1)

        neg_src = torch.randint(0, num_nodes, (len(test_edges),))
        neg_dst = torch.randint(0, num_nodes, (len(test_edges),))
        neg_score = (z[neg_src] * z[neg_dst]).sum(dim=1)

        all_scores = torch.cat([pos_score, neg_score]).numpy()
        all_labels = torch.cat([torch.ones(len(test_edges)), torch.zeros(len(test_edges))]).numpy()

    auc = roc_auc_score(all_labels, all_scores)
    print("\n" + "=" * 50)
    print(f"HELD-OUT LINK PREDICTION AUC: {auc:.3f}")
    print("=" * 50)
    print("\n(0.5 = random guessing, 1.0 = perfect separation)")
    print("This model was trained fresh for evaluation only —")
    print("your live app's career_graph.pkl was NOT modified.")


if __name__ == "__main__":
    evaluate()