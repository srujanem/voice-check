import requests

url = "http://localhost:5000/api/infer"
import glob
import os
files = os.listdir('dataset_image/fake/')
test_img = os.path.join('dataset_image/fake/', files[0])
files = {'file': open(test_img, 'rb')}
data = {'type': 'image'}
try:
    response = requests.post(url, files=files, data=data)
    print(response.status_code)
    print(response.json())
except Exception as e:
    print(f"Error: {e}")
