import os
import re

dirs = ['voice-ui', 'deepfake-ui', 'text-ui', 'video-ui', 'url-ui', 'watermark-ui', 'document-ui']
files = [os.path.join(d, 'script.js') for d in dirs] + ['history.js']

for f in files:
    if os.path.exists(f):
        content = open(f).read()
        
        # Replace localtunnel or localhost with relative paths
        new_content = re.sub(r'https://[a-zA-Z0-9-]+\.loca\.lt/([a-z_]+)', r'/\1', content)
        new_content = re.sub(r'http://localhost:5000/([a-z_]+)', r'/\1', new_content)
        
        # Remove Bypass-Tunnel-Reminder header
        new_content = re.sub(r"\n\s*'Bypass-Tunnel-Reminder':\s*'true',?", "", new_content)
        
        if new_content != content:
            open(f, 'w').write(new_content)
            print(f"Fixed {f}")
