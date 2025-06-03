# cover_letter_factcheck_agent.py

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader

# Load OpenAI API key
load_dotenv()

llm = ChatOpenAI(temperature=0.4, model_name="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY"))

# Path to cover letters and your profile constraints
FOLDER = "step_3_cover_letters"
OUTPUT = "step_4_checked_cover_letters"
CV_RESTRICTIONS = """
- I no longer work at ASSEPRO.
- Do not refer to any current role.
- Do not state that I am a Programm Manager.
- Only refer to previous roles from my CV.
- Keep it concise, factual, and professional.
- Write in German as a native speaker use Umlaut and ss instead of ß.
"""

# Prompt Template
template = PromptTemplate(
    input_variables=["original_text", "constraints"],
    template="""
Überarbeite folgendes Bewerbungsschreiben basierend auf diesen Einschränkungen:

{constraints}

Text:
{original_text}

Gib den überarbeiteten Text in professionellem Deutsch zurück.
"""
)

os.makedirs(OUTPUT, exist_ok=True)

# Process each PDF cover letter and extract text if needed
for filename in os.listdir(FOLDER):
    if filename.endswith(".pdf"):
        pdfpath = os.path.join(FOLDER, filename)
        txtname = filename.replace(".pdf", ".txt")
        txtpath = os.path.join(FOLDER, txtname)
        outpath = os.path.join(OUTPUT, txtname)

        # Convert PDF to TXT if .txt doesn't exist
        if not os.path.exists(txtpath):
            try:
                reader = PdfReader(pdfpath)
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                with open(txtpath, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"📝 Converted: {filename} to {txtname}")
            except Exception as e:
                print(f"⚠️ Failed to convert {filename}: {e}")
                continue

        # Read extracted or existing TXT
        with open(txtpath, "r", encoding="utf-8") as file:
            original = file.read()

        if not original.strip():
            print(f"⚠️ Empty content in: {txtname}, skipping...")
            continue

        prompt = template.format(original_text=original, constraints=CV_RESTRICTIONS)
        cleaned = llm.predict(prompt)

        with open(outpath, "w", encoding="utf-8") as f:
            f.write(cleaned)

        print(f"✔️ Überarbeitet: {filename} -> {outpath}")
