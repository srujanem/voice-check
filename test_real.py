import requests
import io
url = 'http://localhost:5000/api/infer'
files = {'file': ('test.wav', io.BytesIO(b'dummy_audio_data'))}
data = {'type': 'voice'}
r = requests.post(url, files=files, data=data)
print(r.status_code)
print(r.json())
