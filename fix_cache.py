import re

with open(r'D:\voice-check\voice-check\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Force bust the cache for login.html
content = content.replace('href="login.html"', 'href="login.html?v=2"')
content = content.replace('href="/login.html"', 'href="/login.html?v=2"')

with open(r'D:\voice-check\voice-check\index.html', 'w', encoding='utf-8') as f:
    f.write(content)
