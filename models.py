import google.generativeai as genai
import os

# Configure your API key
GOOGLE_API_KEY = "AIzaSyBkyHKIW_LmTQr029mky-9ImgDQm7i6grs"
genai.configure(api_key=GOOGLE_API_KEY)

for m in genai.list_models():
  print(f"Name: {m.name}")
  print(f"Supported generation methods: {m.supported_generation_methods}\n")