import re

with open('c:/voice-check/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove Live Scanner block
content = re.sub(
    r'<a class="nav-card tilt-card purple" href="/live-ui/index\.html[^>]*>.*?<h2>Live Scanner</h2>.*?</a>', 
    '', 
    content, 
    flags=re.DOTALL
)

# Remove Document Scanner blocks
content = re.sub(
    r'<a class="nav-card tilt-card" href="/document-ui/index\.html[^>]*>.*?<h2>Document Scanner</h2>.*?</a>', 
    '', 
    content, 
    flags=re.DOTALL
)

with open('c:/voice-check/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Successfully removed Live Scanner and Document Scanner cards from index.html')
