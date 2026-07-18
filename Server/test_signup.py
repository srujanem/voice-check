import urllib.request
import json
import urllib.error

req = urllib.request.Request(
    'https://architects-gray-raised-providers.trycloudflare.com/api/db/auth/signup',
    method='POST',
    headers={
        'Origin': 'https://authguard.vercel.app',
        'Content-Type': 'application/json'
    },
    data=json.dumps({
        'username': 'testuser2',
        'email': 'test2@test.com',
        'password': 'password123'
    }).encode()
)

try:
    res = urllib.request.urlopen(req)
    print(f"SUCCESS: {res.read().decode()}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
