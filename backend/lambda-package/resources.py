from pypdf import PdfReader
import json
import os

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Read LinkedIn PDF
try:
    linkedin_path = os.path.join(DATA_DIR, "linkedin.pdf")
    reader = PdfReader(linkedin_path)
    linkedin = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            linkedin += text
except (FileNotFoundError, Exception) as e:
    print(f"Warning: Could not read LinkedIn PDF: {e}")
    linkedin = "LinkedIn profile not available"

# Read other data files with error handling
try:
    summary_path = os.path.join(DATA_DIR, "summary.txt")
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = f.read()
except FileNotFoundError:
    print(f"Error: summary.txt not found at {summary_path}")
    summary = "Summary not available"
except Exception as e:
    print(f"Error reading summary.txt: {e}")
    summary = "Summary not available"

try:
    style_path = os.path.join(DATA_DIR, "style.txt")
    with open(style_path, "r", encoding="utf-8") as f:
        style = f.read()
except FileNotFoundError:
    print(f"Error: style.txt not found at {style_path}")
    style = "Communication style not available"
except Exception as e:
    print(f"Error reading style.txt: {e}")
    style = "Communication style not available"

try:
    facts_path = os.path.join(DATA_DIR, "facts.json")
    with open(facts_path, "r", encoding="utf-8") as f:
        facts = json.load(f)
except FileNotFoundError:
    print(f"Error: facts.json not found at {facts_path}")
    facts = {"full_name": "Unknown", "name": "Unknown"}
except Exception as e:
    print(f"Error reading facts.json: {e}")
    facts = {"full_name": "Unknown", "name": "Unknown"}