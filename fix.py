import re
with open('D:/voice-check/voice-check/server-config.js', 'r', encoding='utf-8') as f:
    code = f.read()
code = code.replace('          }\n          }\n      ;', '          }\n      ;')
with open('D:/voice-check/voice-check/server-config.js', 'w', encoding='utf-8') as f:
    f.write(code)
