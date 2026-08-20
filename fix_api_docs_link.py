import re
import glob

for filepath in glob.glob(r'D:\voice-check\voice-check\**\*.html', recursive=True):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '>API Docs<' in content:
            content = content.replace('>API Docs<', '>Documentation<')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                print(f'Updated {filepath}')
    except Exception as e:
        pass
