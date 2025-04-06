import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Loads from .env file

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

queries = ["pyteal language:Python", "algosdk language:Python", "algorand language:Python", "algorand-sdk language:Python", "nft mint pyteal language:Python", "algorand smart contract language:Python", "algorand stateful smart contract language:Python", "algorand stateless smart contract language:Python", "algorand atomic transfer language:Python", "algorand atomic swap language:Python", "algorand atomic swap example:Python", "algorand atomic transfer example:Python", "algorand atomic transfer tutorial:Python", "algorand atomic swap tutorial:Python", "algorand atomic transfer tutorial:Python", "algorand atomic swap example:Python", "algorand atomic transfer example:Python", "algorand atomic transfer tutorial:Python", "algorand atomic swap tutorial:Python", "algorand atomic swap example:Python", "algorand atomic transfer example:Python", "algorand atomic transfer tutorial:Python", "algorand atomic swap tutorial:Python", "algosdk language:JavaScript","voting pyteal language:Python"]

for query in queries:
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
