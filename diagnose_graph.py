"""
diagnose_graph.py

Checks how many job titles in career_graph.pkl are actually connected
to each of a given set of skills. This tells us whether "only Java
Programmer shows up" is a ranking bug or a data-sparsity issue in the
underlying skill-job graph.

Run: python diagnose_graph.py
"""

import pickle

with open('data/career_graph.pkl', 'rb') as f:
    graph_data = pickle.load(f)

job_to_skills = graph_data['job_to_skills']

# The candidate's specific skills from the resume we've been testing with
check_skills = [
    "python", "java", "sql", "html", "css", "aws", "git", "api",
    "machine learning", "networking", "excel", "c++"
]

print(f"Total job titles in graph: {len(job_to_skills)}\n")
print(f"{'Skill':<20} {'# job titles requiring it':<28} {'Example job titles'}")
print("-" * 90)

for skill in check_skills:
    matching_jobs = [title for title, skills in job_to_skills.items() if skill in skills]
    examples = ", ".join(matching_jobs[:4])
    print(f"{skill:<20} {len(matching_jobs):<28} {examples}")

print("\n" + "=" * 90)
print("If most of these show 0-1 job titles, the graph itself is too sparse")
print("for these skills — that's a data-coverage issue, not a ranking bug.")