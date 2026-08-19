import os
import glob
import re

js_files = glob.glob('D:/voice-check/voice-check/*-ui/*.js')

for filepath in js_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the start of PDF download logic and remove the whole block.
    # We can match: const downloadBtn = document.getElementById('download-btn');
    # Then match everything up to the first }); that closes it.
    
    # Let's just use regex to remove anything involving html2pdf
    
    lines = content.split('\n')
    new_lines = []
    skip = False
    brace_count = 0
    
    for line in lines:
        if "getElementById('download-btn')" in line or "getElementById('downloadPdfBtn')" in line:
            skip = True
            if '{' in line:
                brace_count += line.count('{') - line.count('}')
            continue
            
        if skip:
            brace_count += line.count('{') - line.count('}')
            if brace_count <= 0 and '});' in line:
                skip = False
            elif brace_count <= 0 and '}' in line and line.strip() == '}':
                 # sometimes the check is if (downloadBtn) { ... btn.addEventListener( ... ) }
                 pass
            
            # just a fallback if we see html2pdf, we are definitely in a block we want to skip.
            if brace_count == 0 and ('});' in line or line.strip() == '}'):
                # Wait, let's just do a simpler approach: 
                # remove any line that has html2pdf, and we already removed the button in HTML so a dangling event listener might error, but actually we need to remove the event listener block properly.
                pass
        
        if not skip:
            new_lines.append(line)
            
    # Simple regex fallback that is more robust:
    # Match from `const downloadBtn = ...` to `save();\n        });\n    }`
    
    text = '\n'.join(new_lines)
    # This matches the full if (downloadBtn) { ... } block
    text = re.sub(r'(?s)// PDF Download logic\s*const downloadBtn.*?html2pdf.*?\}\);?\s*\}?', '', text)
    text = re.sub(r'(?s)const downloadBtn.*?html2pdf.*?\}\);?\s*\}?', '', text)
    text = re.sub(r'(?s)const downloadPdfBtn.*?html2pdf.*?\}\);?\s*\}?', '', text)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Processed JS: {filepath}")
