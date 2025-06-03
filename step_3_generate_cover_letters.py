# generate_cover_letters.py

import time
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from fpdf import FPDF
import hashlib
import datetime
import re

# Load environment variables (for OpenAI key)
load_dotenv()

# Path to file with job links
LINK_FILE = "step_2_jobsch_results.txt"
CV_FILE = "CV.txt"  # your CV as plain text file
OUTPUT_DIR = "step_3_cover_letters"

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

# Date formatting for header
month_names = {
    1: "Januar", 2: "Februar", 3: "März", 4: "April", 5: "Mai", 6: "Juni",
    7: "Juli", 8: "August", 9: "September", 10: "Oktober", 11: "November", 12: "Dezember"
}

today = datetime.date.today()
date_str = f"Zürich, {today.day}. {month_names[today.month]} {today.year}"

print(f"Generating tailored cover letters for {len(links)} job listings...")

# Generate and save cover letters
for link in links:
    print(f"Processing job listing: {link}")
    try:
        response = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        job_description = soup.get_text()[:3000]  # limit input size
        prompt = prompt_template.format(job_description=job_description, cv_text=user_cv)
        cover_letter = llm.predict(prompt)
        cover_letter = cover_letter.replace("ß", "ss")

        # Extract company name, job title, and location if available
        raw_text = soup.get_text()
        company_match = re.search(r"(?i)\b(?:bei|at|Unternehmen|Firma)[:\s]*([\w\s\-&]+)", raw_text)
        role_match = re.search(r"(?i)(Projektmanagerin|Projektmanager|Project Manager[\w\s]*)", raw_text)
        postal_city_match = re.search(r"\b\d{4,5}\s+\w+", raw_text)

        company_name = company_match.group(1).strip() if company_match else "Unbekannt"
        job_role = role_match.group(0).strip() if role_match else "Projektmanagerin"
        postal_city = postal_city_match.group(0).strip() if postal_city_match else "8000 Zürich"

        # Add metadata block
        metadata_block = (
            f"Date: {date_str}\n"
            f"Business: {company_name}\n"
            f"Postal Code / City: {postal_city}\n"
            f"Link to job ad: {link}\n"
            f"Job title: {job_role}\n\n"
        )

        # Add intro and date header
        header = f"Bewerbung für die Position als {job_role}\n{date_str}\n\n"
        full_text = metadata_block + header + cover_letter

        print("Generated cover letter:")
        print(full_text)

        # Create filename from company and role
        safe_company = re.sub(r"[^a-zA-Z0-9_-]", "_", company_name)[:30]
        safe_role = re.sub(r"[^a-zA-Z0-9_-]", "_", job_role)[:30]
        filename = f"{safe_company}_{safe_role}.pdf"
        pdf_path = os.path.join(OUTPUT_DIR, filename)

        # Export to PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        for line in full_text.split('\n'):
            pdf.multi_cell(0, 10, line)
        pdf.output(pdf_path)

    except Exception as e:
        print(f"Failed to process {link}: {e}")

print("Cover letter generation completed. Files saved in 'step_3_cover_letters/' folder.")
