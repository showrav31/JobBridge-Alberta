# setup_db.py
import pandas as pd
import sqlite3
import re

print("Loading CSV...")
df = pd.read_csv('data/raw/jobs_data.csv')

# Clean company name (remove "Employer details\n\n\n" prefix)
df['company'] = df['company'].str.replace(r'Employer details\n+', '', regex=True).str.strip()

# Fill missing values
df = df.fillna('Not specified')

# Save to SQLite
conn = sqlite3.connect('data/jobs.db')
df.to_sql('jobs', conn, if_exists='replace', index=True, index_label='id')
conn.close()

print(f"✅ Done! {len(df)} jobs saved to data/jobs.db")