import os
import re

file_path = r"D:\Server\ai-training-panel\python_engine\inference.py"
with open(file_path, "r", encoding="utf-8") as f:
    script = f.read()

# Replace the text reading part
old_read = """        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read().strip()"""

new_read = """        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read().strip()
            
        # If it looks like HTML (like from URL Scanner), parse it to get clean text
        if '<html' in text.lower() or '<body' in text.lower() or '<div' in text.lower():
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(text, "html.parser")
                # Remove script and style elements
                for script_or_style in soup(["script", "style"]):
                    script_or_style.extract()
                text = soup.get_text(separator=' ')
                # clean up whitespace
                text = ' '.join(text.split())
                print("[SOTA] Stripped HTML tags from URL scan.")
            except ImportError:
                # If bs4 is not installed, fallback to simple regex
                import re
                text = re.sub(r'<[^>]+>', ' ', text)
                text = ' '.join(text.split())"""

if old_read in script:
    script = script.replace(old_read, new_read)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(script)
    print("Successfully updated inference.py for Text/URL scraping!")
else:
    print("Could not find the exact text block.")
