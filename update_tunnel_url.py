import re

url = 'https://primary-southwest-demonstrates-modify.trycloudflare.com'
path = 'D:/voice-check/voice-check/server-config.js'

content = open(path, encoding='utf-8').read()
new_content = re.sub(
    r"const DEFAULT_URL = '[^']*'",
    f"const DEFAULT_URL = '{url}'",
    content
)
open(path, 'w', encoding='utf-8').write(new_content)
print('Updated server-config.js with:', url)
