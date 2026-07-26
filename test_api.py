import requests

url = "https://authguard-cuejehgfd-srujanems-projects.vercel.app/api/infer"
text = "10 BIOLOGY Since the dawn of civilisation, there have been many attempts to classify living organisms. It was done instinctively not using criteria that were scientific but borne out of a need to use"

print("Testing live Vercel API...")
try:
    r = requests.post(url, data={"type": "text", "text": text})
    print("Status:", r.status_code)
    try:
        print("Response:", r.json())
    except:
        print("Response Text:", r.text.encode('utf-8')[:200])
except Exception as e:
    print("Error:", e)
