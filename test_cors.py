import requests
import re

config = open('c:/voice-check/server-config.js', encoding='utf-8', errors='replace').read()
pattern = r"const DEFAULT_URL = '(https://[a-z0-9\-]+\.trycloudflare\.com)'"
m = re.search(pattern, config)
tunnel = m.group(1) if m else None
print('Tunnel:', tunnel)

if not tunnel:
    exit()

# Test OPTIONS preflight (browser sends this before cross-origin POST)
try:
    r = requests.options(
        tunnel + '/api/infer',
        headers={
            'Origin': 'https://authguard.vercel.app',
            'Access-Control-Request-Method': 'POST',
        },
        timeout=8
    )
    print('OPTIONS status:', r.status_code)
    print('Allow-Origin:', r.headers.get('Access-Control-Allow-Origin', 'MISSING'))
    print('Allow-Methods:', r.headers.get('Access-Control-Allow-Methods', 'MISSING'))
except Exception as e:
    print('OPTIONS error:', e)

# Test POST via tunnel with Origin header (simulating browser)
try:
    with open('assets/images/srujan_avatar.jpg', 'rb') as f:
        r = requests.post(
            tunnel + '/api/infer',
            files={'file': ('test.jpg', f, 'image/jpeg')},
            data={'type': 'image'},
            headers={'Origin': 'https://authguard.vercel.app'},
            timeout=30
        )
    print('POST status:', r.status_code)
    print('Allow-Origin:', r.headers.get('Access-Control-Allow-Origin', 'MISSING'))
    if r.status_code == 200:
        data = r.json()
        print('Prediction:', data.get('prediction', '?'))
    else:
        print('Error body:', r.text[:300])
except Exception as e:
    print('POST error:', e)
