import urllib.request
import json
import urllib.error

# Test local server directly
req = urllib.request.Request(
    'http://localhost:8000/api/db/auth/signup',
    method='POST',
    headers={
        'Content-Type': 'application/json'
    },
    data=json.dumps({
        'username': 'testuser3',
        'email': 'test3@test.com',
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
