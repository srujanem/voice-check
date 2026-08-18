import os, sys, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {'X-API-Key': 'authguard-default-key-2024'}

print("=" * 60)
print("AuthGuard Live API Verification")
print("=" * 60)

# 1. Health / Home
try:
    req = urllib.request.Request('http://127.0.0.1:5000/health', headers=HEADERS)
    res = json.loads(urllib.request.urlopen(req, timeout=5).read())
    print(f"✅ Health Check: {res}")
except Exception as e:
    print(f"ℹ️ Health Check: {e}")

# 2. Text Detection
try:
    data = json.dumps({'text': 'Artificial intelligence has revolutionized numerous industries over the past decade. Machine learning models are increasingly deployed to automate complex tasks and improve decision-making processes.'}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:5000/predict_text', data=data, headers={'Content-Type': 'application/json', **HEADERS})
    res = json.loads(urllib.request.urlopen(req, timeout=5).read())
    print(f"✅ Text Predict: {res.get('prediction')} ({res.get('confidence')}%)")
except Exception as e:
    print(f"❌ Text Predict: {e}")

print("\nVerification Complete!")
