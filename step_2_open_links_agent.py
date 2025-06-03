# open_links_agent.py

import webbrowser
import time

# Path to file with links (each on a new line)
LINK_FILE = "step_2_jobsch_results.txt"

# Read file and extract only URLs
with open(LINK_FILE, "r", encoding="utf-8") as file:
    lines = file.readlines()
    links = [line.strip() for line in lines if line.strip().startswith("https://")]

print(f"Opening {len(links)} links in your default browser...")

# Open each link in the default browser (usually Chrome)
for link in links:
    webbrowser.open_new_tab(link)
    time.sleep(1)  # short pause to avoid overload

print("Done.")
