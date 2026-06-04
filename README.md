# 💼 JobBridge Alberta

 AI-powered job matching platform for Alberta's job market.

## What It Does
- Matches resumes to 5,132 real Canadian job postings using semantic AI search
- Uses Hugging Face embeddings + ChromaDB for vector similarity matching
- Claude AI generates personalized career analysis
- AI Career Agent tailors resumes and writes cover letters per job
- Market Insights dashboard with interactive charts

## Tech Stack
- **Scraping:** Python, BeautifulSoup
- **Database:** SQLite + ChromaDB
- **AI Matching:** Hugging Face (all-MiniLM-L6-v2)
- **LLM Analysis:** Anthropic Claude (Haiku)
- **AI Agent:** Groq (Llama 3.3-70b)
- **Frontend:** Streamlit

## Setup Instructions

### 1. Clone the repo
git clone https://github.com/showrav31/JobBridge-Alberta.git
cd JobBridge-Alberta
## API Keys Setup

This project requires two free API keys.
Create a `.env` file in the root folder:

ANTHROPIC_API_KEY=your-key-here
GROQ_API_KEY=your-key-here

Get your free keys here:
- Anthropic: https://console.anthropic.com
- Groq: https://console.groq.com

Note: The .env file is excluded from GitHub for security.
You must create it manually after cloning.

### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Add API keys
Create a file called `.env` in the root folder:
ANTHROPIC_API_KEY=your-key-here
GROQ_API_KEY=your-key-here

Or paste them directly in app.py at the top.

### 5. Set up the database
python setup_db.py

### 6. Build the vector database
python build_vectors.py

### 7. Run the app
streamlit run app.py