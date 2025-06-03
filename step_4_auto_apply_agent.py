# auto_apply_agent.py
# Placeholder not yet working

import time
import webbrowser
import requests
from bs4 import BeautifulSoup
import pyautogui
import subprocess
import platform
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from fpdf import FPDF
import hashlib

# Load environment variables (for OpenAI key)
load_dotenv()

# Path to file with job links
LINK_FILE = "step_2_jobsch_results.txt"
CV_FILE = "cv.txt"  # your CV as plain text file
CV_PDF_PATH = "/Users/eleni/Documents/CV_Eleni.pdf"  # path to your CV in PDF format
OUTPUT_DIR = "cover_letters"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load job links from file
with open(LINK_FILE, "r", encoding="utf-8") as file:
    lines = file.readlines()
    links = [line.strip() for line in lines if line.strip().startswith("https://")]

# Load your CV
with open(CV_FILE, "r", encoding="utf-8") as f:
    user_cv = f.read()

# Initialize LLM
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY"))

# Prompt template for cover letter generation
prompt_template = PromptTemplate(
    input_variables=["job_description", "cv_text"],
    template="""
Based on the following job description:

{job_description}

And this CV:

{cv_text}

Write a professional cover letter in German as native speaker (max 200 words).
"""
)

print(f"Preparing to apply to {len(links)} job listings...")

# Launch browser in foreground (macOS-specific, adjust for Linux/Windows if needed)
if platform.system() == "Darwin":
    subprocess.run(["open", "-a", "Google Chrome"])
    time.sleep(2)

# Simulated user data for form filling
user_name = "Eleni Huebsch"
user_email = "eleni.huebsch@gmx.ch"
user_phone = "+41 76 266 27 72"

# Open each job and apply with tailored cover letter
for link in links:
    print(f"Opening application page: {link}")
    webbrowser.open_new_tab(link)
    time.sleep(5)

    try:
        response = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        job_description = soup.get_text()[:3000]  # limit input size
        prompt = prompt_template.format(job_description=job_description, cv_text=user_cv)
        cover_letter = llm.predict(prompt)
        print("Generated cover letter:")
        print(cover_letter)

        # Save the cover letter to a PDF file named by hash of URL
        job_id = hashlib.md5(link.encode()).hexdigest()[:8]
        pdf_path = os.path.join(OUTPUT_DIR, f"cover_letter_{job_id}.pdf")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        for line in cover_letter.split('\n'):
            pdf.multi_cell(0, 10, line)
        pdf.output(pdf_path)

    except Exception as e:
        print(f"Failed to fetch job details or generate cover letter for {link}: {e}")
        cover_letter = "I am an experienced IT Project Manager..."

    # Example of simulated typing
    pyautogui.write(user_name)
    pyautogui.press("tab")
    pyautogui.write(user_email)
    pyautogui.press("tab")
    pyautogui.write(user_phone)
    pyautogui.press("tab")
    pyautogui.write(cover_letter)
    pyautogui.press("tab")

    # Simulate file upload (PDF path)
    pyautogui.write(CV_PDF_PATH)
    pyautogui.press("enter")

    time.sleep(10)

print("Semi-automated applications with tailored cover letters and CV uploads completed. Cover letters saved to folder.")
