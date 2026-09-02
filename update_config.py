import re
path = 'server-config.js'
content = open(path, encoding='utf-8').read()
new_content = re.sub(
    r"const DEFAULT_URL = '[^']*'",
    "const DEFAULT_URL = 'https://auction-jeremy-builds-cardiff.trycloudflare.com'",
    content
)
open(path, 'w', encoding='utf-8').write(new_content)
print('Updated config')
