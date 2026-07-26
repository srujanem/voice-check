import glob
import re
import os

js_files = glob.glob('c:/voice-check/**/*.js', recursive=True)

for filepath in js_files:
    if 'node_modules' in filepath or 'old_script.js' in filepath: continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Revert the hardcoded localhost:5000 back to dynamic localStorage lookup
    new_content = re.sub(
        r"let zrokUrl = 'http://localhost:5000';\s*if \(zrokUrl === 'http://localhost:8000'\) zrokUrl = 'http://localhost:5000';",
        "let zrokUrl = localStorage.getItem('zrok_url') || 'http://localhost:5000';\n            if (zrokUrl === 'http://localhost:8000') zrokUrl = 'http://localhost:5000';",
        content
    )
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Reverted hardcoded port in {filepath}")
