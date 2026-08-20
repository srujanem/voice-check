import codecs

with codecs.open('login.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace(
    'const btn = event.currentTarget;',
    'if(event) event.preventDefault(); const btn = event.currentTarget;'
)

with codecs.open('login.html', 'w', encoding='utf-8') as f:
    f.write(html)
