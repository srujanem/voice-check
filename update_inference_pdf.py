import os
import re

file_path = r"D:\Server\ai-training-panel\python_engine\inference.py"
with open(file_path, "r", encoding="utf-8") as f:
    script = f.read()

old_read = """        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read().strip()"""

new_read = """        if file_path.lower().endswith('.pdf'):
            try:
                import PyPDF2
                text = ""
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + " "
                print(f"[SOTA] Extracted {len(text)} characters from PDF.")
            except ImportError:
                return {"error": "PyPDF2 is not installed. Run: pip install PyPDF2"}
            except Exception as e:
                return {"error": f"Failed to read PDF: {str(e)}"}
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read().strip()"""

if old_read in script:
    script = script.replace(old_read, new_read)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(script)
    print("Successfully updated inference.py for PDF extraction!")
else:
    print("Could not find the exact text block.")
