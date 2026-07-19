import urllib.request
import json
import urllib.error

req = urllib.request.Request(
    'https://cute-paws-rule.loca.lt/api/db/auth/signup', 
    method='POST', 
    headers={
        'Origin': 'https://authguard.vercel.app', 
        'Content-Type': 'application/json', 
        'Bypass-Tunnel-Reminder': 'true'
    }, 
    data=json.dumps({
        'username': 'testuser', 
        'email': 'test@test.com', 
        'password': 'password123'
    }).encode()
)

try:
    urllib.request.urlopen(req)
    print("Success!")
except urllib.error.HTTPError as e:
    print(f"Status: {e.code}")
    print(f"Headers:\n{e.headers}")
    print(f"Body:\n{e.read().decode()}")
