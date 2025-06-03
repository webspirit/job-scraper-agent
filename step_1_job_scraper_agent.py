# job_scraper_agent_all.py

import os
from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HEADERS = {"User-Agent": "Mozilla/5.0"}

# Scraper for jobs.ch
def scrape_jobs_ch():
    url = "https://www.jobs.ch/en/vacancies/?term=IT+project+manager&location=Zurich"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []

    for job_card in soup.select("a[data-cy='job-link']"):
        title = job_card.text.strip()
        link = "https://www.jobs.ch" + job_card['href']
        jobs.append((title, link))

    jobs = jobs[:20][::-1]
    result = "\n\n".join([f"{title}\n{link}" for title, link in jobs])

    with open("step_2_jobsch_results.txt", "w", encoding="utf-8") as file:
        file.write(result)

    return result

# Scraper for experis.ch
def scrape_experis():
    url = "https://www.experis.ch/jobs?sort_type=relevance&query=it+project+manager&radius_location=2657895&radius=320km&submit=Search"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []

    for link_tag in soup.select("article.teaser-item a.teaser-item__title"):
        href = link_tag.get("href")
        title = link_tag.text.strip()
        if href and title:
            full_url = f"https://www.experis.ch{href}"
            jobs.append((title, full_url))

    result = "\n\n".join([f"{title}\n{link}" for title, link in jobs])

    with open("step_2_experis_results.txt", "w", encoding="utf-8") as file:
        file.write(result)

    return result

# Scraper for jobagent.ch
def scrape_jobagent():
    url = "https://www.jobagent.ch/search?terms=ICT+Project+Manager&provinces=ZH"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []

    for job_card in soup.select("div.results article a"):
        href = job_card.get("href")
        title = job_card.text.strip()
        if href and title and href.startswith("/job"):
            full_link = f"https://www.jobagent.ch{href}"
            jobs.append((title, full_link))

    result = "\n\n".join([f"{title}\n{link}" for title, link in jobs])

    with open("step_2_jobagent_results.txt", "w", encoding="utf-8") as file:
        file.write(result)

    return result

# Define LangChain tools
jobs_ch_tool = Tool(name="JobsCHScraper", func=lambda x: scrape_jobs_ch(), description="Scrape jobs.ch")
experis_tool = Tool(name="ExperisScraper", func=lambda x: scrape_experis(), description="Scrape experis.ch")
jobagent_tool = Tool(name="JobagentScraper", func=lambda x: scrape_jobagent(), description="Scrape jobagent.ch")

# Initialize Agent
llm = ChatOpenAI(temperature=0, model_name="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY"))

agent = initialize_agent(
    tools=[jobs_ch_tool, experis_tool, jobagent_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Run Agent
if __name__ == "__main__":
    print("--- Scraping jobs.ch ---")
    scrape_jobs_ch()
    print("--- Scraping experis.ch ---")
    scrape_experis()
    print("--- Scraping jobagent.ch ---")
    scrape_jobagent()
