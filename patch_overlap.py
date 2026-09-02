import re

path = 'c:/voice-check/index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove Blog from nav
html = re.sub(r'<a href="/blog\.html[^>]+>Blog</a>', '', html)

# 2. Remove Blog from mobile drawer
html = re.sub(r'<a href="/blog\.html[^>]+><i class="fa-solid fa-newspaper"></i>\s*Cybersecurity Blog</a>', '', html)

# 3. Fix inline media queries for cards-grid
html = re.sub(r'\.cards-grid\s*\{\s*grid-template-columns:\s*repeat\(2,\s*1fr\);\s*gap:\s*12px;\s*padding:\s*16px;\s*\}', '.cards-grid { grid-template-columns: 1fr; gap: 12px; padding: 16px; }', html)
html = re.sub(r'\.cards-grid\s*\{\s*grid-template-columns:\s*1fr 1fr;\s*gap:\s*10px;\s*padding:\s*12px;\s*\}', '.cards-grid { grid-template-columns: 1fr; gap: 10px; padding: 12px; }', html)

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
