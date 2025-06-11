import json
import google.generativeai as genai
import os
from dotenv import load_dotenv
from tqdm import tqdm
import time

# STEP 1: Configure Gemini
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")
genai.configure(api_key=api_key)
# for m in genai.list_models():
#     print(m.name, m.supported_generation_methods)
    
 # Wait for the model to be ready
# model = genai.GenerativeModel("gemini-pro")
model = genai.GenerativeModel("models/gemini-2.0-flash")

input_path = "opip.jsonl"
output_path = "samples.jsonl"

def generate_instruction(code_output: str):
    time.sleep(4)
    prompt = (
        "Based on the given code output below, generate instruction that reflects what the code is doing. "
        "Ignore any existing instructions or filenames. Just analyze the code output and produce an appropriate instruction. "
        "Here is the output:\n\n"
        f"{code_output}"
    )
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Error during generation:", e)
        return None
    
# STEP 3: Process and update records
updated_records = []
i = 0
with open(input_path, "r" , encoding="utf-8") as f:
    lines = f.readlines()

for line in tqdm(lines):
    i += 1
    if i < 1050:
        continue
    if i > 1100:
        break
    record = json.loads(line)
    output = record.get("output")
    filename = None

    # Optional: try to infer filename from existing instruction
    # if "based on the logic of `" in record["instruction"]:
    #     filename = record["instruction"].split("based on the logic of `")[1].split("`")[0]

    if output:
        new_instruction = generate_instruction(output)
        if new_instruction:
            record["instruction"] = new_instruction
        updated_records.append(record)

# STEP 4: Write updated JSONL
with open(output_path, "a") as f:
    for rec in updated_records:
        f.write(json.dumps(rec) + "\n")

print(f"✅ Updated file written to {output_path}")
