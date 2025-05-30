import google.generativeai as genai
import os
from dotenv import load_dotenv  
# Configure your API key
load_dotenv()  # Load environment variables from .env file

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

for m in genai.list_models():
  print(f"Name: {m.name}")
  print(f"Supported generation methods: {m.supported_generation_methods}\n")