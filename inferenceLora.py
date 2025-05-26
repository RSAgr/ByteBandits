import sys
import json
import os
import google.generativeai as genai

from dotenv import load_dotenv  
# Configure your API key
load_dotenv()  # Load environment variables from .env file

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
    json.dump({"error": "GEMINI_API_KEY environment variable not set"}, sys.stdout)
    sys.exit(1)

genai.configure(api_key=GOOGLE_API_KEY)

# === Read prompt from stdin ===
raw_input = sys.stdin.read()
try:
    data = json.loads(raw_input)
    prompt = data["prompt"]
except Exception as e:
    json.dump({"error": f"Invalid input format: {str(e)}"}, sys.stdout)
    sys.exit(1)

# === Build System Prompt and Full Prompt ===
system_prompt = """You are a helpful AI coding assistant that generates Python code. 
When given an instruction, respond with only the code that implements it.
Do not include any explanations or additional text.

Example 1:
Instruction: generate a function to add two numbers
Response:
def add(a, b):
    return a + b

Example 2:
Instruction: print hello world
Response:
print("Hello, World!")

Example 3:
Instruction: check if a number is prime
Response:
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True
"""

instruction = prompt.lower().strip()
if not instruction.startswith('generate') and not instruction.startswith('write'):
    instruction = f'generate code to {instruction}'

full_prompt = f"{system_prompt}\n\nInstruction: {instruction}\nResponse:\n"

# === Call Gemini API ===
try:
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(full_prompt)
    completion = response.text.strip()

    # Clean output if inside code blocks
    if '```python' in completion:
        code = completion.split('```python')[1].split('```')[0].strip()
        completion = code
    elif '```' in completion:
        code = completion.split('```')[1].split('```')[0].strip()
        if code.startswith('python'):
            code = code[6:].strip()
        completion = code
    json.dump({"response": completion}, sys.stdout)

except Exception as e:
    error_msg = f"Inference error: {str(e)}"
    print(f"Error: {error_msg}", file=sys.stderr)
    json.dump({"error": error_msg}, sys.stdout)
    sys.exit(1)
