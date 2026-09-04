import streamlit as st
import sqlite3
import pandas as pd
import chromadb
import anthropic
from sentence_transformers import SentenceTransformer
from groq import Groq
import os
import PyPDF2
import io
import time
import altair as alt
import pickle
import numpy as np
import streamlit.components.v1 as components
from auto_apply import extract_application_email, send_application_email, auto_fill_web_form
from dotenv import load_dotenv
load_dotenv()

# ── API Keys ──────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JobBridge Alberta",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS (Light Theme — unchanged from your original) ───────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: #F8FAFC; color: #0F172A; }

.top-nav {
    display: flex; justify-content: space-between; align-items: center;
    background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px;
    padding: 16px 32px; margin-bottom: 32px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}
.nav-logo { font-family:'Outfit',sans-serif; font-size:1.5rem; font-weight:800; color:#1E293B; }
.nav-logo span { color: #2563EB; }
.nav-links { display:flex; gap:24px; font-size:0.95rem; font-weight:600; color:#64748B; }
.nav-links span:first-child { color:#2563EB; border-bottom:2px solid #2563EB; padding-bottom:4px; }

.hero {
    background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
    border: 1px solid #BFDBFE; border-radius: 24px;
    padding: 56px 48px; margin-bottom: 40px;
    box-shadow: 0 10px 30px rgba(37,99,235,0.05);
}
.hero-title {
    font-family:'Outfit',sans-serif; font-size:3.5rem; font-weight:800;
    color:#1E3A8A; margin:0 0 12px 0; line-height:1.1;
}
.hero-sub { font-size:1.15rem; color:#334155; font-weight:500; margin:0; line-height:1.6; }
.hero-badge {
    display:inline-block; background:#FFFFFF; border:1px solid #93C5FD;
    color:#2563EB; padding:6px 16px; border-radius:30px;
    font-size:0.8rem; font-weight:800; letter-spacing:1px;
    text-transform:uppercase; margin-bottom:20px;
}

.stat-row { display:flex; gap:20px; margin-bottom:40px; }
.stat-card {
    flex:1; background:#FFFFFF; border:1px solid #E2E8F0;
    border-radius:16px; padding:24px; text-align:center;
    box-shadow:0 4px 15px rgba(0,0,0,0.03);
}
.stat-number { font-family:'Outfit',sans-serif; font-size:2.5rem; font-weight:800; color:#2563EB; line-height:1; margin-bottom:8px; }
.stat-label { font-size:0.85rem; color:#64748B; text-transform:uppercase; letter-spacing:1px; font-weight:700; }

.section-title {
    font-family:'Outfit',sans-serif; font-size:1.3rem; font-weight:800;
    color:#0F172A; letter-spacing:0.5px; margin-bottom:20px;
    padding-bottom:12px; border-bottom:2px solid #E2E8F0;
}

.job-card {
    background:#FFFFFF; border:1px solid #E2E8F0; border-radius:16px;
    padding:24px; margin-bottom:8px; position:relative; overflow:hidden;
    box-shadow:0 2px 10px rgba(0,0,0,0.02);
}
.job-card::before {
    content:''; position:absolute; left:0; top:0; bottom:0; width:5px;
    background:linear-gradient(180deg,#3B82F6,#60A5FA);
}
.job-rank { font-family:'Outfit',sans-serif; font-size:0.75rem; font-weight:800; color:#2563EB; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:8px; }
.job-title { font-family:'Outfit',sans-serif; font-size:1.25rem; font-weight:800; color:#0F172A; margin-bottom:6px; }
.job-meta { font-size:0.9rem; color:#475569; margin-bottom:12px; font-weight:600; }
.job-detail { font-size:0.85rem; color:#334155; line-height:1.6; }

.agent-panel {
    background:#F0F7FF; border:1px solid #BFDBFE;
    border-radius:12px; padding:20px; margin-top:8px; margin-bottom:16px;
}
.agent-panel-title {
    font-family:'Outfit',sans-serif; font-size:1rem; font-weight:800;
    color:#1D4ED8; margin-bottom:16px;
}
.output-box {
    background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px;
    padding:20px; font-size:0.88rem; color:#334155;
    line-height:1.8; white-space:pre-wrap; margin-top:12px;
    max-height:600px; overflow-y:auto;
}
.chat-user {
    background:#DBEAFE; border-radius:10px; padding:10px 14px;
    margin:6px 0; font-size:0.88rem; color:#1E3A8A; text-align:right;
}
.chat-bot {
    background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px;
    padding:10px 14px; margin:6px 0; font-size:0.88rem; color:#334155;
}

.stButton > button {
    background:linear-gradient(135deg,#2563EB,#3B82F6) !important;
    color:white !important; border:none !important; border-radius:12px !important;
    padding:16px 32px !important; font-family:'Outfit',sans-serif !important;
    font-weight:700 !important; font-size:1.05rem !important;
    box-shadow:0 8px 20px rgba(37,99,235,0.25) !important;
}
.stSelectbox > div > div, .stTextArea > div > textarea {
    background:#FFFFFF !important; border:1px solid #CBD5E1 !important;
    color:#0F172A !important; border-radius:12px !important;
}
[data-testid="stFileUploadDropzone"] {
    background-color:#FFFFFF !important; border:2px dashed #94A3B8 !important;
    border-radius:16px !important; padding:24px !important;
}
[data-testid="stFileUploadDropzone"] div { color:#334155 !important; font-weight:500 !important; }
[data-testid="stFileUploadDropzone"] button {
    background-color:#2563EB !important; color:#FFFFFF !important;
    font-weight:700 !important; border-radius:8px !important; border:none !important;
}
section[data-testid="stSidebar"] { background:#F1F5F9 !important; border-right:1px solid #E2E8F0 !important; }
.stTabs [data-baseweb="tab-list"] { background:transparent !important; gap:10px; }
.stTabs [data-baseweb="tab"] {
    color:#64748B !important; font-family:'Outfit',sans-serif !important;
    font-weight:700 !important; font-size:1.1rem !important;
    padding:12px 24px !important; background:#FFFFFF !important;
    border-radius:12px !important; border:1px solid #E2E8F0 !important;
}
.stTabs [aria-selected="true"] { background:#EFF6FF !important; color:#2563EB !important; border:1px solid #93C5FD !important; }

.ai-dashboard { display:grid; grid-template-columns:1fr; gap:20px; margin-bottom:40px; margin-top:20px; }
.ai-card { background:#ffffff; border:1px solid #e2e8f0; border-radius:16px; padding:24px; box-shadow:0 4px 15px rgba(0,0,0,0.03); border-left-width:6px; border-left-style:solid; }
.ai-card-title { display:flex; align-items:center; font-family:'Outfit',sans-serif; font-size:1.15rem; font-weight:800; margin-bottom:12px; text-transform:uppercase; letter-spacing:1px; }
.ai-card-icon { font-size:1.5rem; margin-right:12px; }
.ai-card-body { font-size:0.95rem; color:#334155; line-height:1.6; }
.ai-match { border-left-color:#10B981; background:#F0FDF4; }
.ai-match .ai-card-title { color:#047857; }
.ai-skills { border-left-color:#3B82F6; background:#EFF6FF; }
.ai-skills .ai-card-title { color:#1D4ED8; }
.ai-gaps { border-left-color:#F59E0B; background:#FFFBEB; }
.ai-gaps .ai-card-title { color:#B45309; }
.ai-advice { border-left-color:#8B5CF6; background:#F5F3FF; }
.ai-advice .ai-card-title { color:#6D28D9; }
</style>
""", unsafe_allow_html=True)


# ── Load Models ───────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_resource
def load_vectordb():
    client = chromadb.PersistentClient(path="./data/vectordb")
    return client.get_or_create_collection("jobs")

@st.cache_data
def load_db_stats():
    conn = sqlite3.connect('data/jobs.db')
    total_jobs = pd.read_sql("SELECT COUNT(*) as c FROM jobs", conn).iloc[0]['c']
    total_companies = pd.read_sql("SELECT COUNT(DISTINCT company) as c FROM jobs", conn).iloc[0]['c']
    province_counts = pd.read_sql("""
        SELECT province, COUNT(*) as count FROM jobs
        WHERE province != 'Not specified'
        GROUP BY province ORDER BY count DESC
    """, conn)
    category_counts = pd.read_sql("""
        SELECT title, COUNT(*) as count FROM jobs
        GROUP BY title ORDER BY count DESC LIMIT 8
    """, conn)
    conn.close()
    return total_jobs, total_companies, province_counts, category_counts

model = load_model()
collection = load_vectordb()
total_jobs, total_companies, province_counts, category_counts = load_db_stats()
init_feedback_table()


# ── Core Helpers ──────────────────────────────────────────────────────────────
def extract_pdf_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text.strip()

def find_jobs(input_text, num_results, province_filter="All"):
    embedding = model.encode(input_text).tolist()
    where = {"province": province_filter} if province_filter != "All" else None
    results = collection.query(
        query_embeddings=[embedding],
        n_results=num_results,
        where=where
    )
    return results
def find_jobs(input_text, num_results, province_filter="All"):
    embedding = model.encode(input_text).tolist()
    where = {"province": province_filter} if province_filter != "All" else None
    results = collection.query(
        query_embeddings=[embedding],
        n_results=num_results,
        where=where
    )
    return results

# 👇 PASTE THE TWO NEW FUNCTIONS RIGHT HERE 👇

def init_feedback_table():
    conn = sqlite3.connect('data/jobs.db')
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT,
            company TEXT,
            matched_skills TEXT,
            rating INTEGER,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_feedback(job_title, company, matched_skills, rating):
    conn = sqlite3.connect('data/jobs.db')
    conn.execute(
        "INSERT INTO feedback (job_title, company, matched_skills, rating) VALUES (?, ?, ?, ?)",
        (job_title, company, ", ".join(matched_skills), rating)
    )
    conn.commit()
    conn.close()


def get_ai_explanation(input_text, job_results):
    # FIX 3: Uses ALL matched jobs as context
    jobs_context = "\n\n---\n\n".join(job_results['documents'][0])
    prompt = f"""You are JobBridge, an expert Canadian career advisor helping Alberta job seekers.

CANDIDATE PROFILE:
{input_text[:2000]}

ALL TOP MATCHING JOBS FROM CANADIAN JOB BANK:
{jobs_context}

Based on ALL the jobs above, respond in EXACTLY this format:

**TOP MATCH:**
[Name the single best matching job and company. 2 sentences explaining why.]

**SKILLS MATCH:**
[List 3-5 specific skills from the candidate that match across ALL these job postings.]

**SKILL GAPS:**
[List 2-3 skills the candidate should develop to be competitive across ALL these roles in Alberta.]

**CAREER ADVICE:**
[2-3 actionable sentences based on ALL these postings and the Alberta job market.]

Be specific, encouraging, and practical."""

    ai_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = ai_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def parse_ai_sections(text):
    sections = {"TOP MATCH": "", "SKILLS MATCH": "", "SKILL GAPS": "", "CAREER ADVICE": ""}
    current = None
    for line in text.split('\n'):
        matched = False
        for key in sections:
            if key in line.upper():
                current = key
                matched = True
                clean = line.replace(f"**{key}:**", "").replace(f"{key}:", "").strip()
                if clean:
                    sections[current] += clean + " "
                break
        if not matched and current:
            sections[current] += line + " "
    return {k: v.strip() for k, v in sections.items()}

def create_interactive_bar_chart(data, x_col, y_col, x_label, y_label):
    hover = alt.selection_point(on='mouseover', empty='none', clear='mouseout')
    chart = alt.Chart(data).mark_bar(
        cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=35
    ).encode(
        x=alt.X(f'{x_col}:N', title=x_label, sort='-y',
                axis=alt.Axis(labelAngle=-45, labelOverlap=False, labelLimit=500,
                              labelColor='#475569', titleColor='#0F172A', titleFontWeight=700)),
        y=alt.Y(f'{y_col}:Q', title=y_label,
                axis=alt.Axis(grid=True, gridColor='#E2E8F0',
                              labelColor='#475569', titleColor='#0F172A', titleFontWeight=700)),
        color=alt.condition(hover, alt.value('#FFC107'), alt.value('#3B82F6')),
        tooltip=[alt.Tooltip(x_col, title=x_label), alt.Tooltip(y_col, title=y_label)]
    ).add_params(hover).properties(height=350).configure_view(strokeWidth=0)
    return chart


# ── GNN Career Pathway ────────────────────────────────────────────────────────
CAREER_SKILL_VOCAB = None  # populated on load

@st.cache_resource
def load_career_graph():
    with open('data/career_graph.pkl', 'rb') as f:
        return pickle.load(f)

def extract_skills_from_text(text, vocab):
    import re
    text_lower = str(text).lower()
    found = []
    for skill in vocab:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)
    return found

SOFT_SKILLS = {
    "communication", "problem solving", "time management", "teamwork",
    "critical thinking", "attention to detail", "organization", "adaptability"
}

def get_career_pathway(resume_text, top_k=5):
    graph_data = load_career_graph()
    embeddings = graph_data['embeddings']
    jobtitle_to_idx = graph_data['jobtitle_to_idx']
    skill_to_idx = graph_data['skill_to_idx']
    job_to_skills = graph_data['job_to_skills']
    skill_vocab = graph_data['skill_vocab']

    candidate_skills = extract_skills_from_text(resume_text, skill_vocab)
    if not candidate_skills:
        return [], []

    # Only SPECIFIC (non-soft) skills drive the ranking. Soft skills like
    # "communication" appear in almost every job title's required-skill set,
    # so including them in the averaged vector lets generic overlap dominate
    # and drown out technical/domain signal.
    specific_skills = [s for s in candidate_skills if s not in SOFT_SKILLS]
    ranking_skills = specific_skills if specific_skills else candidate_skills

    skill_indices = [skill_to_idx[s] for s in ranking_skills]
    candidate_vector = embeddings[skill_indices].mean(axis=0)

    idx_to_jobtitle = {v: k for k, v in jobtitle_to_idx.items()}
    job_indices = list(jobtitle_to_idx.values())
    job_embeddings = embeddings[job_indices]

    norms = np.linalg.norm(job_embeddings, axis=1) * np.linalg.norm(candidate_vector)
    similarities = (job_embeddings @ candidate_vector) / (norms + 1e-8)

    ranked = sorted(zip(job_indices, similarities), key=lambda x: -x[1])

    results = []
    candidate_set = set(candidate_skills)
    for job_idx, score in ranked:
        title = idx_to_jobtitle[job_idx]
        required = job_to_skills.get(title, set())
        matched = required & candidate_set
        matched_specific = matched - SOFT_SKILLS

        # Require at least one SPECIFIC skill overlap so generic soft-skill
        # matches alone can't surface an unrelated role.
        if not matched_specific and specific_skills:
            continue

        missing = required - candidate_set
        results.append({
            'title': title.title(),
            'match_score': round(float(score) * 100, 1),
            'matched_skills': list(matched),
            'missing_skills': list(missing)
        })
        if len(results) >= top_k:
            break

    return candidate_skills, results
def build_pathway_network_html(candidate_skills, pathway_results):
    from pyvis.network import Network
    import tempfile

    net = Network(height="600px", width="100%", bgcolor="#FFFFFF",
                   font_color="#1E293B", directed=False)
    net.barnes_hut(gravity=-8000, spring_length=120)

    net.add_node("You", label="You", color="#7C3AED", size=32, shape="star")

    for skill in candidate_skills:
        net.add_node(f"skill_{skill}", label=skill, color="#3B82F6", size=18)
        net.add_edge("You", f"skill_{skill}")

    for r in pathway_results:
        job_id = f"job_{r['title']}"
        job_size = 22 + (r['match_score'] / 5)
        net.add_node(job_id, label=r['title'], color="#10B981", size=job_size)

        for skill in r['matched_skills']:
            skill_id = f"skill_{skill}"
            if skill_id not in [n['id'] for n in net.nodes]:
                net.add_node(skill_id, label=skill, color="#3B82F6", size=18)
            net.add_edge(skill_id, job_id, color="#86EFAC")

        for skill in r['missing_skills'][:5]:
            skill_id = f"gap_{skill}"
            if skill_id not in [n['id'] for n in net.nodes]:
                net.add_node(skill_id, label=skill, color="#F59E0B", size=14)
            net.add_edge(job_id, skill_id, color="#FDE68A", dashes=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        net.write_html(tmp.name, open_browser=False)
        html_content = open(tmp.name, 'r', encoding='utf-8').read()

    return html_content


# def get_career_pathway(resume_text, top_k=5):
#     graph_data = load_career_graph()
#     embeddings = graph_data['embeddings']
#     jobtitle_to_idx = graph_data['jobtitle_to_idx']
#     skill_to_idx = graph_data['skill_to_idx']
#     job_to_skills = graph_data['job_to_skills']
#     skill_vocab = graph_data['skill_vocab']

#     candidate_skills = extract_skills_from_text(resume_text, skill_vocab)
#     if not candidate_skills:
#         return [], []

#     skill_indices = [skill_to_idx[s] for s in candidate_skills]
#     candidate_vector = embeddings[skill_indices].mean(axis=0)

#     idx_to_jobtitle = {v: k for k, v in jobtitle_to_idx.items()}
#     job_indices = list(jobtitle_to_idx.values())
#     job_embeddings = embeddings[job_indices]

#     norms = np.linalg.norm(job_embeddings, axis=1) * np.linalg.norm(candidate_vector)
#     similarities = (job_embeddings @ candidate_vector) / (norms + 1e-8)

#     ranked = sorted(zip(job_indices, similarities), key=lambda x: -x[1])

#     results = []
#     for job_idx, score in ranked[:top_k]:
#         title = idx_to_jobtitle[job_idx]
#         required = job_to_skills.get(title, set())
#         missing = required - set(candidate_skills)
#         matched = required & set(candidate_skills)
#         results.append({
#             'title': title.title(),
#             'match_score': round(float(score) * 100, 1),
#             'matched_skills': list(matched),
#             'missing_skills': list(missing)
#         })

#     return candidate_skills, results


# ── AI Agent Functions (Groq — Free) ─────────────────────────────────────────
def convert_to_pdf(text, filename):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_LEFT
    import io

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        spaceAfter=6,
        fontName='Helvetica'
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=13,
        leading=18,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )

    story = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 8))
        elif line.startswith('**') and line.endswith('**'):
            clean = line.replace('**', '')
            story.append(Paragraph(clean, heading_style))
        elif line.isupper() and len(line) < 50:
            story.append(Paragraph(line, heading_style))
        else:
            safe_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(safe_line, normal_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
def get_groq_client():
    return Groq(api_key=GROQ_API_KEY)

def tailor_resume(resume_text, job_description):
    # FIX 5: max_tokens=4000 + strict instructions = full resume always
    client = get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert Canadian resume writer. "
                    "You MUST return the COMPLETE resume from start to finish. "
                    "Never stop halfway. Never add notes like 'Note: ...' at the end. "
                    "Always include every section: Summary, Core Skills, Work Experience (ALL roles fully), Education, Certifications."
                )
            },
            {
                "role": "user",
                "content": f"""Tailor this resume for the job below. Return the COMPLETE resume — do not cut anything short.

ORIGINAL RESUME:
{resume_text}

JOB POSTING:
{job_description[:2000]}

Rules:
- Keep every fact true — do not invent experience
- Rephrase and reorder bullet points to match job keywords
- Include ALL sections completely: Summary, Core Skills, Work Experience (every role with all bullet points), Education, Certifications
- Make it ATS-friendly for Canadian employers
- Return the full resume from top to bottom — nothing cut off
- Do not add any notes or commentary after the resume"""
            }
        ],
        max_tokens=4000,
        temperature=0.4
    )
    return response.choices[0].message.content

def write_cover_letter(resume_text, job_description, company_name, job_title):
    client = get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an expert Canadian cover letter writer. Write professional, specific, and warm cover letters."
            },
            {
                "role": "user",
                "content": f"""Write a professional cover letter for this candidate.

CANDIDATE RESUME:
{resume_text[:2000]}

JOB TITLE: {job_title}
COMPANY: {company_name}

JOB DESCRIPTION:
{job_description[:2000]}

Rules:
- 3 clear paragraphs
- Opening: why this company and role specifically
- Middle: 2-3 achievements that directly match the job requirements
- Closing: confident call to action
- Canadian professional tone
- Do NOT use 'I am writing to apply'
- Return only the cover letter, ready to send"""
            }
        ],
        max_tokens=1000,
        temperature=0.7
    )
    return response.choices[0].message.content

def chat_with_agent(conversation_history, user_message, resume_text, job_description, job_title, company):
    client = get_groq_client()
    system_prompt = f"""You are JobBridge AI Agent — a helpful Canadian career assistant.

You are helping a candidate apply for this SPECIFIC job:
JOB TITLE: {job_title}
COMPANY: {company}

JOB DESCRIPTION:
{job_description[:1500]}

CANDIDATE RESUME:
{resume_text[:2000]}

Help with: interview prep, resume questions, salary advice for Alberta, application tips.
Always be specific to THIS exact job and company. Be encouraging and practical."""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1000,
        temperature=0.7
    )
    return response.choices[0].message.content


# ── Session State ─────────────────────────────────────────────────────────────
if 'search_done' not in st.session_state:
    st.session_state.search_done = False
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'ai_explanation' not in st.session_state:
    st.session_state.ai_explanation = ""
if 'current_resume' not in st.session_state:
    st.session_state.current_resume = ""
if 'num_results' not in st.session_state:
    st.session_state.num_results = 5
if 'agent_open' not in st.session_state:
    st.session_state.agent_open = {}
if 'tailored_resume' not in st.session_state:
    st.session_state.tailored_resume = {}
if 'cover_letter' not in st.session_state:
    st.session_state.cover_letter = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {}
if 'pathway_results' not in st.session_state:
    st.session_state.pathway_results = None
if 'pathway_skills' not in st.session_state:
    st.session_state.pathway_skills = None    


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 24px 0;'>
        <div style='font-family:Outfit,sans-serif; font-size:1.8rem; font-weight:800; color:#0F172A;'>
            JobBridge <span style='color:#2563EB;'>Alberta</span>
        </div>
        <div style='font-size:0.85rem; color:#64748B; margin-top:4px; font-weight:600;'>
            AI Career Matching Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-title' style='color:#0F172A; border-color:#CBD5E1;'>📊 Live Database</div>", unsafe_allow_html=True)
    st.metric("Job Postings", f"{total_jobs:,}")
    st.metric("Companies", f"{total_companies:,}")
    st.metric("Provinces", "3")
    st.divider()

    st.markdown("<div class='section-title' style='color:#0F172A; border-color:#CBD5E1;'>🗺️ Coverage</div>", unsafe_allow_html=True)
    for _, row in province_counts.iterrows():
        pct = int(row['count'] / total_jobs * 100)
        st.markdown(f"""
        <div style='margin-bottom:16px;'>
            <div style='display:flex; justify-content:space-between;
                        font-size:0.9rem; color:#334155; margin-bottom:6px; font-weight:700;'>
                <span>{row['province']}</span>
                <span style='color:#2563EB;'>{row['count']:,}</span>
            </div>
            <div style='background:#E2E8F0; border-radius:6px; height:6px;'>
                <div style='width:{pct}%; background:linear-gradient(90deg,#3B82F6,#60A5FA);
                            height:6px; border-radius:6px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.divider()
    st.markdown("<div style='font-size:0.75rem; color:#94A3B8; text-align:center; font-weight:600;'>Data: Job Bank Canada · Feb 2026</div>", unsafe_allow_html=True)


# ── Top Nav ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-nav">
    <div class="nav-logo">JobBridge <span>Alberta</span></div>
    <div class="nav-links">
        <span>Platform</span>
        <span>Analytics</span>
        <span>Methodology</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
    <div class='hero-badge'>✦ Powered by AI · Hugging Face · Claude · Groq</div>
    <h1 class='hero-title'>Find Your Perfect<br>Job in Alberta</h1>
    <p class='hero-sub'>Upload your resume and let AI match you with real Canadian opportunities —<br>
    then use the AI Agent on each job to tailor your resume, write a cover letter, and get career advice.</p>
</div>
""", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='stat-row'>
    <div class='stat-card'><div class='stat-number'>5,132</div><div class='stat-label'>Live Postings</div></div>
    <div class='stat-card'><div class='stat-number'>1,533</div><div class='stat-label'>Companies</div></div>
    <div class='stat-card'><div class='stat-number'>8</div><div class='stat-label'>Categories</div></div>
    <div class='stat-card'><div class='stat-number'>17%</div><div class='stat-label'>Youth Unemp.</div></div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
# tab1, tab2 = st.tabs(["🔍  Job Matcher", "📊  Market Insights"])

tab1, tab2, tab3 = st.tabs(["🔍  Job Matcher", "📊  Market Insights", "🧠  Career Pathway (GNN)"])
# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — JOB MATCHER
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("<div class='section-title'>📄 Upload Resume</div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("PDF format only", type=["pdf"], label_visibility="collapsed")
        if uploaded_file:
            st.success(f"✅ **{uploaded_file.name}** uploaded successfully!")
            resume_text = extract_pdf_text(uploaded_file)
            st.session_state.current_resume = resume_text
            with st.expander("👁️ Preview extracted text (Full Resume)"):
                # FIX 2: Full resume shown in scrollable box
                st.markdown(f"""
<div style='background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:16px;
            max-height:400px; overflow-y:auto; font-size:0.85rem; color:#475569;
            line-height:1.6; white-space:pre-wrap;'>{resume_text}</div>
                """, unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='section-title'>✍️ Or Describe Your Skills</div>", unsafe_allow_html=True)
        manual_text = st.text_area(
            "Skills input",
            placeholder="Example: 3 years Python experience, data analysis, machine learning, Bachelor's in Computer Science...",
            height=160,
            label_visibility="collapsed"
        )

    # Filters
    st.markdown("<div class='section-title' style='margin-top:32px;'>🔧 Filters</div>", unsafe_allow_html=True)
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        province_filter = st.selectbox("Province", ["All", "Alberta", "British Columbia", "Manitoba"])
    with fcol2:
        num_results = st.selectbox("Number of Results", [3, 5, 7, 10], index=1)
    with fcol3:
        sort_by = st.selectbox("Sort By", ["Best Match", "Most Recent"])

    st.markdown("<br>", unsafe_allow_html=True)
    search_clicked = st.button("🚀 Find My Matching Jobs", type="primary", use_container_width=True)

    if search_clicked:
        if uploaded_file:
            input_text = resume_text
        elif manual_text.strip():
            input_text = manual_text.strip()
            st.session_state.current_resume = input_text
        else:
            st.error("⚠️ Please upload a resume or describe your skills first!")
            st.stop()

        progress_placeholder = st.empty()
        steps = [
            ("🔍", "Reading your profile..."),
            ("📂", "Searching job postings in Database..."),
            ("🤖", "AI is analyzing your matches..."),
        ]
        for icon, msg in steps:
            progress_placeholder.markdown(f"""
<div style='background:#FFFFFF; border:1px solid #93C5FD; border-radius:12px;
            padding:20px 24px; margin:8px 0; box-shadow:0 4px 10px rgba(0,0,0,0.03);'>
    <div style='font-family:Outfit,sans-serif; font-weight:700; font-size:1.05rem; color:#1E3A8A;'>
        {icon} {msg}
    </div>
</div>
            """, unsafe_allow_html=True)
            time.sleep(0.8)

        results = find_jobs(input_text, num_results, province_filter)
        explanation = get_ai_explanation(input_text, results)
        progress_placeholder.empty()

        st.session_state.search_done = True
        st.session_state.search_results = results
        st.session_state.ai_explanation = explanation
        st.session_state.num_results = num_results
        # Reset all agent state on new search
        st.session_state.agent_open = {}
        st.session_state.tailored_resume = {}
        st.session_state.cover_letter = {}
        st.session_state.chat_history = {}

    # ── Show Results ──────────────────────────────────────────────────────────
    if st.session_state.search_done and st.session_state.search_results:
        results = st.session_state.search_results
        explanation = st.session_state.ai_explanation
        resume = st.session_state.current_resume

        # AI Analysis cards — based on ALL matched jobs (FIX 3)
        sections = parse_ai_sections(explanation)
        card_configs = {
            "TOP MATCH":     {"class": "ai-match",  "icon": "🏆"},
            "SKILLS MATCH":  {"class": "ai-skills", "icon": "✅"},
            "SKILL GAPS":    {"class": "ai-gaps",   "icon": "📉"},
            "CAREER ADVICE": {"class": "ai-advice", "icon": "💡"}
        }
        st.markdown("<div class='section-title' style='margin-top:20px;'>🤖 AI Candidate Analysis</div>", unsafe_allow_html=True)
        ai_html = "<div class='ai-dashboard'>\n"
        for key, content in sections.items():
            if content and key in card_configs:
                cfg = card_configs[key]
                formatted = content.replace('\n', '<br>')
                ai_html += (
                    f"<div class='ai-card {cfg['class']}'>"
                    f"<div class='ai-card-title'><span class='ai-card-icon'>{cfg['icon']}</span> {key}</div>"
                    f"<div class='ai-card-body'>{formatted}</div>"
                    f"</div>\n"
                )
        ai_html += "</div>"
        st.markdown(ai_html, unsafe_allow_html=True)

        # Load URLs from DB
        conn = sqlite3.connect('data/jobs.db')
        url_df = pd.read_sql("SELECT title, company, url FROM jobs", conn)
        conn.close()

        st.markdown(f"<div class='section-title'>📋 Top {st.session_state.num_results} Matching Jobs</div>", unsafe_allow_html=True)

        for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            title = meta.get('title', 'Job Position').title()
            company = meta.get('company', 'Company')
            city = meta.get('city', '')
            province_val = meta.get('province', '')
            location = f"{city}, {province_val}".strip(', ')

            lines = [l.strip() for l in doc.split('\n') if l.strip() and ':' in l]
            details = '<br>'.join(lines[:6])

            # Get URL for this job
            match = url_df[
                (url_df['title'].str.lower() == meta.get('title','').lower()) &
                (url_df['company'].str.lower() == meta.get('company','').lower())
            ]
            job_url = match['url'].iloc[0] if not match.empty else None

            # Job Card
            st.markdown(f"""
<div class='job-card'>
    <div class='job-rank'>Match #{i+1}</div>
    <div class='job-title'>{title}</div>
    <div class='job-meta'>🏢 {company} &nbsp;·&nbsp; 📍 {location}</div>
    <div class='job-detail'>{details}</div>
</div>
            """, unsafe_allow_html=True)

            # Buttons row — Apply + AI Agent (FIX 4 & 6)
            btn1, btn2 = st.columns([1, 1])

            with btn1:
                # FIX 6: Apply button with real job URL
                if job_url and str(job_url).startswith('http'):
                    st.markdown(f"""
<a href='{job_url}' target='_blank' style='
    display:inline-block;
    background:linear-gradient(135deg,#10B981,#059669);
    color:white; padding:12px 28px; border-radius:10px;
    font-family:Outfit,sans-serif; font-weight:700; font-size:0.95rem;
    text-decoration:none; box-shadow:0 4px 12px rgba(16,185,129,0.3);'>
    🔗 Apply for this Job
</a>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("<span style='font-size:0.85rem; color:#94A3B8; padding:12px 0; display:block;'>No direct link available</span>", unsafe_allow_html=True)

            with btn2:
                # FIX 4: AI Agent button per job card
                agent_label = "❌ Close AI Agent" if st.session_state.agent_open.get(i, False) else "🤖 Launch AI Agent"
                if st.button(agent_label, key=f"agent_btn_{i}"):
                    st.session_state.agent_open[i] = not st.session_state.agent_open.get(i, False)
                    st.rerun()
            fb_col1, fb_col2, fb_col3 = st.columns([1, 1, 4])
            with fb_col1:
                if st.button("👍", key=f"fb_up_{i}"):
                    save_feedback(title, company, [], 1)
                    st.toast("Thanks for the feedback!")
            with fb_col2:
                if st.button("👎", key=f"fb_down_{i}"):
                    save_feedback(title, company, [], 0)
                    st.toast("Thanks for the feedback!")            

            # AI Agent Panel — opens directly below this job card
            if st.session_state.agent_open.get(i, False):
                st.markdown(f"""
<div class='agent-panel'>
    <div class='agent-panel-title'>🤖 AI Career Agent — Helping you apply for: {title} at {company}</div>
</div>
                """, unsafe_allow_html=True)

                # a_tab1, a_tab2, a_tab3 = st.tabs([
                #     "📄  Tailor My Resume",
                #     "✉️  Write Cover Letter",
                #     "💬  Chat with Agent"
                # ])
                a_tab1, a_tab2, a_tab3, a_tab4 = st.tabs([
                      "📄  Tailor My Resume",
                      "✉️  Write Cover Letter",
                      "💬  Chat with Agent",
                      "🚀  Auto Apply"
                 ])

                # # Tab A — Tailor Resume (FIX 5: full resume)
                # with a_tab1:
                #     st.markdown(f"Rewriting your resume specifically for **{title}** at **{company}**")
                #     if not resume:
                #         st.warning("⚠️ Upload a resume or type your skills above first.")
                #     else:
                #         if st.button("✨ Generate Full Tailored Resume", key=f"tailor_{i}", type="primary"):
                #             with st.spinner("Writing your complete tailored resume... (30-45 seconds)"):
                #                 tailored = tailor_resume(resume, doc)
                #                 st.session_state.tailored_resume[i] = tailored

                #         if st.session_state.tailored_resume.get(i):
                #             st.success("✅ Full tailored resume ready!")
                #             st.markdown(f"<div class='output-box'>{st.session_state.tailored_resume[i]}</div>", unsafe_allow_html=True)
                #             st.download_button(
                #                 "⬇️ Download Tailored Resume (.txt)",
                #                 data=st.session_state.tailored_resume[i],
                #                 file_name=f"resume_{title.replace(' ','_')}_{company.replace(' ','_')}.txt",
                #                 mime="text/plain",
                #                 key=f"dl_resume_{i}"
                #             )
                # Tab A — Tailor Resume with Editable Text + PDF Download
                with a_tab1:
                    st.markdown(f"Tailoring your resume specifically for **{title}** at **{company}**")
                    if not resume:
                        st.warning("⚠️ Upload a resume or type your skills above first.")
                    else:
                        if st.button("✨ Generate Full Tailored Resume", key=f"tailor_{i}", type="primary"):
                            with st.spinner("AI is writing your full tailored resume... (may take 30-45 seconds)"):
                                tailored = tailor_resume(resume, doc)
                                st.session_state.tailored_resume[i] = tailored

                        if st.session_state.tailored_resume.get(i):
                            st.success("✅ Full tailored resume ready! You can edit it below before downloading.")

                            # Editable text area
                            edited_resume = st.text_area(
                                "✏️ Edit your resume here",
                                value=st.session_state.tailored_resume[i],
                                height=500,
                                key=f"edit_resume_{i}",
                                label_visibility="visible"
                            )

                            # Save edits back to session state
                            st.session_state.tailored_resume[i] = edited_resume

                            st.markdown("<br>", unsafe_allow_html=True)

                            # Download buttons side by side
                            dl_col1, dl_col2 = st.columns(2)

                            with dl_col1:
                                # Download as PDF
                                pdf_buffer = convert_to_pdf(
                                    edited_resume,
                                    f"resume_{title}_{company}"
                                )
                                st.download_button(
                                    "⬇️ Download as PDF",
                                    data=pdf_buffer,
                                    file_name=f"resume_{title.replace(' ','_')}_{company.replace(' ','_')}.pdf",
                                    mime="application/pdf",
                                    key=f"dl_resume_pdf_{i}",
                                    type="primary"
                                )

                            with dl_col2:
                                # Download as TXT
                                st.download_button(
                                    "⬇️ Download as TXT",
                                    data=edited_resume,
                                    file_name=f"resume_{title.replace(' ','_')}_{company.replace(' ','_')}.txt",
                                    mime="text/plain",
                                    key=f"dl_resume_txt_{i}"
                                )

                # Tab B — Cover Letter with Editable Text + PDF Download
                with a_tab2:
                    st.markdown(f"Writing a cover letter for **{title}** at **{company}**")
                    if not resume:
                        st.warning("⚠️ Upload a resume or type your skills above first.")
                    else:
                        if st.button("✨ Generate Cover Letter", key=f"cover_{i}", type="primary"):
                            with st.spinner("AI is writing your cover letter..."):
                                letter = write_cover_letter(resume, doc, company, title)
                                st.session_state.cover_letter[i] = letter

                        if st.session_state.cover_letter.get(i):
                            st.success("✅ Cover letter ready! You can edit it below before downloading.")

                            # Editable text area
                            edited_letter = st.text_area(
                                "✏️ Edit your cover letter here",
                                value=st.session_state.cover_letter[i],
                                height=400,
                                key=f"edit_cover_{i}",

                                label_visibility="visible"
                            )

                            # Save edits back to session state
                            st.session_state.cover_letter[i] = edited_letter

                            st.markdown("<br>", unsafe_allow_html=True)

                            # Download buttons side by side
                            dl_col1, dl_col2 = st.columns(2)

                            with dl_col1:
                                # Download as PDF
                                pdf_buffer = convert_to_pdf(
                                    edited_letter,
                                    f"cover_letter_{company}"
                                )
                                st.download_button(
                                    "⬇️ Download as PDF",
                                    data=pdf_buffer,
                                    file_name=f"cover_letter_{company.replace(' ','_')}.pdf",
                                    mime="application/pdf",
                                    key=f"dl_cover_pdf_{i}",
                                    type="primary"
                                )

                            with dl_col2:
                                # Download as TXT
                                st.download_button(
                                    "⬇️ Download as TXT",
                                    data=edited_letter,
                                    file_name=f"cover_letter_{company.replace(' ','_')}.txt",
                                    mime="text/plain",
                                    key=f"dl_cover_txt_{i}"
                                )
                # # Tab B — Cover Letter
                # with a_tab2:
                #     st.markdown(f"Writing a cover letter for **{title}** at **{company}**")
                #     if not resume:
                #         st.warning("⚠️ Upload a resume or type your skills above first.")
                #     else:
                #         if st.button("✨ Generate Cover Letter", key=f"cover_{i}", type="primary"):
                #             with st.spinner("Writing your cover letter..."):
                #                 letter = write_cover_letter(resume, doc, company, title)
                #                 st.session_state.cover_letter[i] = letter

                #         if st.session_state.cover_letter.get(i):
                #             st.success("✅ Cover letter ready!")
                #             st.markdown(f"<div class='output-box'>{st.session_state.cover_letter[i]}</div>", unsafe_allow_html=True)
                #             st.download_button(
                #                 "⬇️ Download Cover Letter (.txt)",
                #                 data=st.session_state.cover_letter[i],
                #                 file_name=f"cover_letter_{company.replace(' ','_')}.txt",
                #                 mime="text/plain",
                #                 key=f"dl_cover_{i}"
                #             )

                # Tab C — Chat
                with a_tab3:
                    st.markdown(f"Ask anything about applying for **{title}** at **{company}**")

                    if i not in st.session_state.chat_history:
                        st.session_state.chat_history[i] = []

                    for msg in st.session_state.chat_history[i]:
                        if msg['role'] == 'user':
                            st.markdown(f"<div class='chat-user'>👤 {msg['content']}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='chat-bot'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

                    user_input = st.text_input(
                        "Your question",
                        placeholder=f"e.g. What salary should I expect for {title} in Alberta?",
                        label_visibility="collapsed",
                        key=f"chat_input_{i}"
                    )

                    c1, c2 = st.columns([3, 1])
                    with c1:
                        if st.button("Send →", key=f"send_{i}", type="primary", use_container_width=True):
                            if user_input and resume:
                                with st.spinner("Agent is thinking..."):
                                    reply = chat_with_agent(
                                        st.session_state.chat_history[i],
                                        user_input, resume, doc, title, company
                                    )
                                st.session_state.chat_history[i].append({"role": "user", "content": user_input})
                                st.session_state.chat_history[i].append({"role": "assistant", "content": reply})
                                st.rerun()
                            elif not resume:
                                st.warning("Please upload a resume first.")
                    with c2:
                        if st.button("🗑️ Clear", key=f"clear_{i}", use_container_width=True):
                            st.session_state.chat_history[i] = []
                            st.rerun()

# Tab D — Auto Apply
                with a_tab4:
                    st.markdown(f"Auto-apply for **{title}** at **{company}**")
                    st.warning("⚠️ This gives the AI agent permission to act on your behalf. Always review before final submission.")

                    ac1, ac2, ac3 = st.columns(3)
                    with ac1:
                        applicant_name = st.text_input("Full name", key=f"apply_name_{i}")
                    with ac2:
                        applicant_email = st.text_input("Your email", key=f"apply_email_{i}")
                    with ac3:
                        applicant_phone = st.text_input("Your phone", key=f"apply_phone_{i}")

                    if st.button("🔍 Check Application Method", key=f"check_apply_{i}"):
                        found_email = extract_application_email(doc)
                        st.session_state[f"apply_email_found_{i}"] = found_email if found_email else "none"

                    found = st.session_state.get(f"apply_email_found_{i}")

                    if found and found != "none":
                        st.success(f"✅ This posting accepts applications by email: {found}")
                        gcol1, gcol2 = st.columns(2)
                        with gcol1:
                            gmail_address = st.text_input("Your Gmail address", key=f"gmail_addr_{i}")
                        with gcol2:
                            gmail_app_password = st.text_input(
                                "Gmail App Password", type="password", key=f"gmail_pass_{i}",
                                help="Generate at myaccount.google.com/apppasswords"
                            )

                        cover = st.session_state.cover_letter.get(i, "")
                        resume_final = st.session_state.tailored_resume.get(i, resume)

                        if st.button("📧 Send Application Now", key=f"send_apply_{i}", type="primary"):
                            if not (gmail_address and gmail_app_password and cover and applicant_name):
                                st.error("Please fill in your Gmail credentials, name, and generate a cover letter first (Cover Letter tab).")
                            else:
                                try:
                                    send_application_email(
                                        gmail_address, gmail_app_password, found,
                                        f"Application for {title} — {applicant_name}",
                                        cover, resume_final, applicant_name
                                    )
                                    st.success(f"✅ Application sent to {found}!")
                                except Exception as e:
                                    st.error(f"Failed to send: {e}")

                    elif found == "none":
                        st.info("No direct application email found in this posting. Use the assisted web form filler instead:")
                        if st.button("🌐 Open & Auto-Fill Application Form", key=f"webform_{i}"):
                            if not job_url:
                                st.error("No application URL available for this job.")
                            elif not (applicant_name and applicant_email):
                                st.error("Please fill in your name and email above first.")
                            else:
                                applicant_info = {
                                    'name': applicant_name,
                                    'email': applicant_email,
                                    'phone': applicant_phone,
                                    'resume_path': None
                                }
                                with st.spinner("Opening browser and filling form... check your taskbar"):
                                    filled = auto_fill_web_form(job_url, applicant_info)
                                st.success(f"✅ Auto-filled: {', '.join(filled) if filled else 'no fields detected'}. A browser window has opened — please review and click submit yourself.")
            st.markdown("<br>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — MARKET INSIGHTS
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📊 Job Market Overview</div>", unsafe_allow_html=True)

    conn = sqlite3.connect('data/jobs.db')
    top_titles = pd.read_sql("SELECT title, COUNT(*) as count FROM jobs GROUP BY title ORDER BY count DESC LIMIT 10", conn)
    top_companies = pd.read_sql("SELECT company, COUNT(*) as count FROM jobs WHERE company != 'Not specified' GROUP BY company ORDER BY count DESC LIMIT 10", conn)
    province_data = pd.read_sql("SELECT province, COUNT(*) as count FROM jobs WHERE province != 'Not specified' GROUP BY province ORDER BY count DESC", conn)
    conn.close()

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown("<div class='section-title' style='font-size:1.1rem; border:none; margin-bottom:0;'>🏆 Top 10 Most In-Demand Jobs</div>", unsafe_allow_html=True)
        st.altair_chart(create_interactive_bar_chart(top_titles, 'title', 'count', 'Job Title', 'Postings'), use_container_width=True, theme="streamlit")

    with col_b:
        st.markdown("<div class='section-title' style='font-size:1.1rem; border:none; margin-bottom:0;'>🏢 Top 10 Hiring Companies</div>", unsafe_allow_html=True)
        st.altair_chart(create_interactive_bar_chart(top_companies, 'company', 'count', 'Company', 'Postings'), use_container_width=True, theme="streamlit")

    st.markdown("<br><br>", unsafe_allow_html=True)
    col_c, col_d = st.columns(2, gap="large")

    with col_c:
        st.markdown("<div class='section-title' style='font-size:1.1rem; border:none; margin-bottom:0;'>🗺️ Jobs by Province</div>", unsafe_allow_html=True)
        st.altair_chart(create_interactive_bar_chart(province_data, 'province', 'count', 'Province', 'Postings'), use_container_width=True, theme="streamlit")

    with col_d:
        st.markdown("<div class='section-title' style='font-size:1.1rem;'>📌 Key Insights</div>", unsafe_allow_html=True)
        st.markdown("""
<div style='background:#FFFFFF; border:1px solid #E2E8F0; border-radius:16px; padding:32px; box-shadow:0 4px 15px rgba(0,0,0,0.03);'>
    <div style='margin-bottom:24px;'>
        <div style='font-family:Outfit,sans-serif; font-size:0.85rem; font-weight:800; color:#2563EB; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;'>Alberta Context</div>
        <div style='font-size:0.95rem; color:#334155; line-height:1.6;'>Youth unemployment reached 17% in Alberta in 2025, highlighting the urgent need for smarter job matching tools.</div>
    </div>
    <div style='margin-bottom:24px;'>
        <div style='font-family:Outfit,sans-serif; font-size:0.85rem; font-weight:800; color:#2563EB; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;'>Top Sectors Hiring</div>
        <div style='font-size:0.95rem; color:#334155; line-height:1.6;'>Management, Trades & Technical, and Technology & IT make up over 57% of all job postings in the dataset.</div>
    </div>
    <div>
        <div style='font-family:Outfit,sans-serif; font-size:0.85rem; font-weight:800; color:#2563EB; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;'>Data Source</div>
        <div style='font-size:0.95rem; color:#334155; line-height:1.6;'>5,132 job postings scraped from Job Bank Canada — the official Government of Canada employment database.</div>
    </div>
</div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — CAREER PATHWAY (GNN)
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🧠 GNN-Powered Career Pathway</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#EFF6FF; border:1px solid #BFDBFE; border-radius:12px; padding:16px 20px; margin-bottom:24px; font-size:0.9rem; color:#1E3A8A;'>
    This uses a Graph Neural Network trained on skill-to-job relationships across all 5,132 postings.
    It maps your resume's skills into the graph and recommends roles you're positioned to grow into —
    not just jobs matching today, but where your career can go next.
    </div>
    """, unsafe_allow_html=True)

    pathway_resume = st.session_state.current_resume
    if not pathway_resume:
        st.info("👆 Upload a resume or enter your skills in the Job Matcher tab first.")
    else:
        if st.button("🧠 Generate Career Pathway", type="primary", use_container_width=True):
            with st.spinner("Mapping your skills onto the career graph..."):
                candidate_skills, pathway_results = get_career_pathway(pathway_resume, top_k=5)
                st.session_state.pathway_results = pathway_results
                st.session_state.pathway_skills = candidate_skills

        if st.session_state.get('pathway_results'):
            skills = st.session_state.pathway_skills
            st.markdown("**Skills detected in your profile:**")
            chips = " ".join([f"<span style='background:#DBEAFE;color:#1E3A8A;padding:4px 12px;border-radius:20px;font-size:0.8rem;font-weight:600;margin-right:6px;'>{s}</span>" for s in skills])
            st.markdown(f"<div style='margin-bottom:24px;'>{chips}</div>", unsafe_allow_html=True)

            st.markdown("<div class='section-title'>🎯 Recommended Career Pathway</div>", unsafe_allow_html=True)

            for r in st.session_state.pathway_results:
                missing_html = "".join([f"<span style='background:#FFFBEB;color:#B45309;padding:3px 10px;border-radius:14px;font-size:0.78rem;margin-right:6px;'>{m}</span>" for m in r['missing_skills'][:6]]) or "<span style='color:#94A3B8;font-size:0.85rem;'>None — you're fully qualified!</span>"
                matched_html = "".join([f"<span style='background:#F0FDF4;color:#047857;padding:3px 10px;border-radius:14px;font-size:0.78rem;margin-right:6px;'>{m}</span>" for m in r['matched_skills'][:6]]) or "<span style='color:#94A3B8;font-size:0.85rem;'>None yet</span>"

                st.markdown(f"""
<div class='job-card'>
    <div class='job-rank'>Match Score: {r['match_score']}%</div>
    <div class='job-title'>{r['title']}</div>
    <div style='margin-top:12px; font-size:0.85rem; color:#334155;'><b>✅ Skills you already have:</b><br>{matched_html}</div>
    <div style='margin-top:10px; font-size:0.85rem; color:#334155;'><b>📈 Skills to develop:</b><br>{missing_html}</div>
</div>
                """, unsafe_allow_html=True)
                st.markdown("<div class='section-title' style='margin-top:32px;'>🕸️ Interactive Skill Graph</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='font-size:0.85rem; color:#64748B; margin-bottom:12px;'>
        🟣 You &nbsp;·&nbsp; 🔵 Your skills &nbsp;·&nbsp; 🟢 Recommended roles &nbsp;·&nbsp; 🟠 Skills to develop
        <br>Drag nodes, scroll to zoom.
        </div>
        """, unsafe_allow_html=True)

        graph_html = build_pathway_network_html(
            st.session_state.pathway_skills,
            st.session_state.pathway_results
        )
        components.html(graph_html, height=620, scrolling=False)                        