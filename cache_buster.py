import glob
import re

html_files = glob.glob('D:/voice-check/voice-check/**/*.html', recursive=True)

for filepath in html_files:
    if 'node_modules' in filepath: continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = re.sub(r'script\.js\?v=\d+', 'script.js?v=6', content)
    new_content = re.sub(r'theme\.js\?v=\d+', 'theme.js?v=6', new_content)
    new_content = re.sub(r'history\.js\?v=\d+', 'history.js?v=6', new_content)
    new_content = re.sub(r'server-config\.js\?v=\d+', 'server-config.js?v=6', new_content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Busted cache in {filepath}")
