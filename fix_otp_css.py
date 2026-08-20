import re
import codecs

with codecs.open('login.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Make OTP grid responsive so it doesn't crash iPhone SE screens
html = re.sub(
    r'\.otp-grid\s*\{\s*display:\s*flex;\s*gap:\s*8px;\s*margin-top:\s*6px;\s*\}', 
    r'.otp-grid { display: flex; gap: 6px; margin-top: 6px; justify-content: space-between; }', 
    html
)
html = re.sub(
    r'\.otp-box\s*\{\s*width:\s*44px;\s*height:\s*50px;', 
    r'.otp-box { flex: 1; min-width: 0; height: 50px;', 
    html
)

with codecs.open('login.html', 'w', encoding='utf-8') as f:
    f.write(html)
