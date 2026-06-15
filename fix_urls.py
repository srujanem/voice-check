import os
import re

dirs = ['voice-ui', 'deepfake-ui', 'text-ui', 'video-ui', 'url-ui', 'watermark-ui', 'document-ui']
files = [os.path.join(d, 'script.js') for d in dirs] + ['history.js']

for f in files:
    if os.path.exists(f):
        content = open(f).read()
        # Replace fetch('/endpoint') or fetch("/endpoint") with fetch('http://localhost:5000/endpoint')
        new_content = re.sub(r'fetch\([\'\"]/([a-z_]+)[\'\"]', r"fetch('http://localhost:5000/\1'", content)
        if new_content != content:
            open(f, 'w').write(new_content)
            print(f"Fixed {f}")
