import codecs
import re

with codecs.open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(
    r'<div class="nav-right">\s*<div class="theme-toggle"',
    '<div class="nav-right">\n  <div id="nav-auth"></div>\n  <div class="theme-toggle"',
    html
)

with codecs.open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
