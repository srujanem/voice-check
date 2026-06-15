import os
import re

dirs = ['voice-ui', 'deepfake-ui', 'text-ui', 'video-ui', 'url-ui', 'watermark-ui', 'document-ui']
files = [os.path.join(d, 'script.js') for d in dirs] + ['history.js']

for f in files:
    if os.path.exists(f):
        content = open(f).read()
        
        # Replace localtunnel or localhost with the NEW localtunnel URL
        new_content = re.sub(r'https://[a-zA-Z0-9-]+\.loca\.lt', r'https://large-hoops-sit.loca.lt', content)
        new_content = re.sub(r'http://localhost:5000', r'https://large-hoops-sit.loca.lt', new_content)
        
        # Add Bypass-Tunnel-Reminder header to all fetch headers if not present
        if 'Bypass-Tunnel-Reminder' not in new_content:
            new_content = re.sub(r'(headers:\s*{)', r"\1\n                    'Bypass-Tunnel-Reminder': 'true',", new_content)
        
        if new_content != content:
            open(f, 'w').write(new_content)
            print(f"Fixed {f}")
