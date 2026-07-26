import glob
import re

js_files = glob.glob('c:/voice-check/**/*.js', recursive=True)

for filepath in js_files:
    if 'node_modules' in filepath: continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the localStorage fetch with a hardcoded localhost:5000
    new_content = re.sub(
        r"localStorage\.getItem\('zrok_url'\)\s*\|\|\s*'http://localhost:5000'",
        "'http://localhost:5000'",
        content
    )
    
    # Also fix any remaining 8000 ports that weren't caught
    new_content = re.sub(
        r"localStorage\.getItem\('zrok_url'\)\s*\|\|\s*'http://localhost:8000'",
        "'http://localhost:5000'",
        new_content
    )
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")
