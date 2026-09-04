"""
auto_apply.py
Handles automatic job application in two modes:

1. Email mode — if the posting text contains an application email,
   the agent drafts and sends the tailored resume + cover letter directly.

2. Web-form mode (best effort) — opens a real browser via Playwright,
   detects and fills common form fields, then PAUSES so the user reviews
   and submits manually. This is intentional: form structures vary too
   much across employer sites to safely auto-submit blind.
"""
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import subprocess
import sys
import json
import tempfile
import os


def extract_application_email(text):
    """Look for an email address inside job posting text."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, str(text))
    return matches[0] if matches else None


def send_application_email(sender_email, sender_app_password,
                            recipient_email, subject,
                            cover_letter_text, resume_text, applicant_name):
    """
    Sends an application email with the cover letter as the body
    and the tailored resume attached as a text file.

    sender_app_password: a Gmail "App Password", NOT the regular
    Gmail password. Generate one at myaccount.google.com/apppasswords
    (requires 2-Step Verification enabled on the Gmail account).
    """
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(cover_letter_text, 'plain'))

    resume_attachment = MIMEApplication(resume_text.encode('utf-8'), _subtype='txt')
    resume_attachment.add_header(
        'Content-Disposition', 'attachment',
        filename=f"{applicant_name.replace(' ', '_')}_Resume.txt"
    )
    msg.attach(resume_attachment)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_app_password)
        server.send_message(msg)

    return True


def auto_fill_web_form(job_url, applicant_info):
    """
    Fills the application form using a separate worker process
    (fill_form_worker.py) instead of calling Playwright directly.
    This avoids the Windows + Streamlit event-loop conflict, and runs
    fully headless — required for cloud deployment where there's no
    display anyway.

    Returns: (filled_fields: list, screenshot_bytes: bytes or None, error: str or None)
    """
    screenshot_path = os.path.join(tempfile.gettempdir(), f"jobbridge_screenshot_{os.getpid()}.png")
    worker_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fill_form_worker.py")

    result = subprocess.run(
        [sys.executable, worker_script, job_url,
         applicant_info.get('name', ''),
         applicant_info.get('email', ''),
         applicant_info.get('phone', ''),
         screenshot_path],
        capture_output=True, text=True, timeout=60
    )

    try:
        data = json.loads(result.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return [], None, f"Worker process failed: {result.stderr[:500]}"

    if data.get("error"):
        return [], None, data["error"]

    screenshot_bytes = None
    if data.get("screenshot_path") and os.path.exists(data["screenshot_path"]):
        with open(data["screenshot_path"], "rb") as f:
            screenshot_bytes = f.read()
        os.remove(data["screenshot_path"])

    return data.get("filled", []), screenshot_bytes, None

#old auto fill
# def auto_fill_web_form(job_url, applicant_info):
#     """
#     Opens the job posting in a visible Chromium browser and attempts
#     to fill commonly-named fields (name, email, phone) and attach a
#     resume file if a file input is found.

#     The browser window is left OPEN for the user to review and submit
#     manually — this is a deliberate safety choice, not a limitation
#     to hide. Different employer sites use very different form layouts,
#     so blind auto-submission risks sending incorrect or incomplete
#     applications.

#     Requires: pip install playwright && playwright install chromium
#     """
#     from playwright.sync_api import sync_playwright

#     playwright = sync_playwright().start()
#     browser = playwright.chromium.launch(headless=False)
#     page = browser.new_page()
#     page.goto(job_url, timeout=30000)

#     field_map = {
#         'name': ['input[name*="name" i]', 'input[id*="name" i]'],
#         'email': ['input[type="email"]', 'input[name*="email" i]'],
#         'phone': ['input[type="tel"]', 'input[name*="phone" i]'],
#     }

#     filled_fields = []
#     for field_key, selectors in field_map.items():
#         for selector in selectors:
#             try:
#                 if page.locator(selector).count() > 0:
#                     page.fill(selector, applicant_info.get(field_key, ''))
#                     filled_fields.append(field_key)
#                     break
#             except Exception:
#                 continue

#     try:
#         if applicant_info.get('resume_path') and page.locator('input[type="file"]').count() > 0:
#             page.set_input_files('input[type="file"]', applicant_info['resume_path'])
#             filled_fields.append('resume')
#     except Exception:
#         pass

#     # Intentionally NOT calling browser.close() — window stays open
#     # on the user's screen so they can review and click submit themselves.
#     return filled_fields