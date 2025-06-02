# job_scraper_agent.py

import os
from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -- Tool 1: Scraper for jobs.ch (updated to return up to 20 results) -- #
def scrape_jobs_ch():
    url = "https://www.jobs.ch/en/vacancies/?term=project+manager"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []

    for job_card in soup.select("a[data-cy='job-link']"):
        title = job_card.text.strip()
        link = "https://www.jobs.ch" + job_card['href']
        jobs.append(f"{title}: {link}")

    result = "\n".join(jobs[:20])  # return top 20

    print("--- Jobs from jobs.ch ---")
    print(result)

    # Export to TXT file
    with open("jobsch_results.txt", "w", encoding="utf-8") as file:
        file.write(result)

    return result

jobs_ch_tool = Tool(
    name="JobsCHScraper",
    func=lambda x: scrape_jobs_ch(),
    description="Use this tool to get current job ads from jobs.ch."
)

# -- Tool 2: Placeholder for LinkedIn (since LinkedIn restricts scraping) -- #
def linkedin_placeholder(_: str) -> str:
    return "LinkedIn job scraping is restricted. Please use their official API or manual search."

linkedin_tool = Tool(
    name="LinkedInScraper",
    func=linkedin_placeholder,
    description="Returns a message about LinkedIn job search limitations."
)

# -- Initialize Agent -- #
llm = ChatOpenAI(temperature=0, model_name="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY"))

agent = initialize_agent(
    tools=[jobs_ch_tool, linkedin_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# -- Run Agent -- #
if __name__ == "__main__":
    with open("prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read().strip()

    result = agent.run(prompt)
    print(result)
