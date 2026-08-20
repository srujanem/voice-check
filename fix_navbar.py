import re

with open(r'D:\voice-check\voice-check\auth.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('href="/login.html?v=v3_fix"', 'href="/signin.html"')
content = content.replace('href="login.html?v=v3_fix"', 'href="signin.html"')
content = content.replace('href="/login.html"', 'href="/signin.html"')
content = content.replace('href="login.html"', 'href="signin.html"')

with open(r'D:\voice-check\voice-check\auth.js', 'w', encoding='utf-8') as f:
    f.write(content)
    
with open(r'D:\voice-check\voice-check\dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('login.html', 'signin.html')
with open(r'D:\voice-check\voice-check\dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
