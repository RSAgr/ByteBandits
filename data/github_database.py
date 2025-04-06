import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Loads from .env file

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

query = "pyteal language:Python"
url = f"https://api.github.com/search/code?q={query}&per_page=10"

response = requests.get(url, headers=HEADERS)
results = response.json()

for item in results.get("items", []):
    file_url = item["html_url"]
    raw_url = item["html_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    print("Downloading from:", raw_url)

    code = requests.get(raw_url).text
    with open("algorand_github_dataset.txt", "a", encoding="utf-8") as f:
        f.write(f"\n# File: {file_url}\n{code}\n")
