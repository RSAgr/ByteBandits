from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

visited = set()
base_url = "https://developer.algorand.org/docs/"
domain = urlparse(base_url).netloc
output = "scraped_content.txt"

# Define unwanted URL patterns
EXCLUDE_PATTERNS = [
    "/accounts/login",
    "/accounts/signup",
    "/accounts/github",
    "login",
    "signup"
]

SKIP_PHRASES = [
    "Don’t have an account",
    "head over to dev.algorand.co",
    "Please excuse us",
    "Gitcoin bounties",
    "sign up", "log in",
    "See the full list"
]

def is_meaningful_text(text):
    if len(text) < 40:  # Skip too short
        return False
    for phrase in SKIP_PHRASES:
        if phrase.lower() in text.lower():
            return False
    return True


# Helper function to check if URL should be skipped
def is_excluded(url):
    return any(pattern in url for pattern in EXCLUDE_PATTERNS)


def crawl(url):
    
        
    if url in visited:
        return
    visited.add(url)

    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')

        # 📝 Extract and process content here
        print(f"Scraping: {url}")
        
              
        
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if is_meaningful_text(text):
                with open(output, 'a') as file:
                    file.write(text + '\n')

            
        # 🖼️ Extract images
        # 🔗 Find more links to follow
        for a_tag in soup.find_all('a', href=True):
            next_link = urljoin(url, a_tag['href'])
            if domain in urlparse(next_link).netloc and not is_excluded(next_link):
                crawl(next_link)

    except Exception as e:
        print(f"Failed to crawl {url}: {e}")

crawl(base_url)
