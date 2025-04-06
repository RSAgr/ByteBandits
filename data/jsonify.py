import json

with open("algorand_github_dataset.txt", "r", encoding="utf-8") as f:
    raw = f.read()

# Split on file headers
chunks = raw.split("# File: ")

entries = []

for chunk in chunks[1:]:  # skip the first empty chunk
    try:
        # First line is the file path
        lines = chunk.splitlines()
        file_path = lines[0].strip()
        code = "\n".join(lines[1:]).strip()

        # Skip if code is empty or code looks like a URL (error)
        if not code or code.startswith("http"):
            continue

        entries.append({
            "file_path": file_path,
            "code": code
        })
    except Exception as e:
        print("Error processing a chunk:", e)

# Save to .jsonl
with open("algorand_github_clean.jsonl", "w", encoding="utf-8") as f:
    for item in entries:
        f.write(json.dumps(item) + "\n")



# import re
# import json

# with open("algorand_github_dataset.txt", "r", encoding="utf-8") as file:
#     raw_data = file.read()

# pattern = r'# File: (.+)\n'


# file_paths = re.findall(pattern, raw_data)


# code_blocks = re.split(pattern, raw_data)[1:] 


# grouped = [(file_paths[i], code_blocks[i+1]) for i in range(len(file_paths))]


# with open("github_code_data.jsonl", "a") as outfile:
#     for file_path, code in grouped:
#         json_obj = {
#             "file_path": file_path.strip(),
#             "code": code.strip()
#         }
#         outfile.write(json.dumps(json_obj) + "\n")

# print("Converted to github_code_data.jsonl successfully!")
