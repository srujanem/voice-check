import re

with open(r'D:\voice-check\voice-check\auth.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('href="/login.html"', 'href="/login.html?v=v3_fix"')
content = content.replace('href="login.html"', 'href="login.html?v=v3_fix"')

with open(r'D:\voice-check\voice-check\auth.js', 'w', encoding='utf-8') as f:
    f.write(content)
