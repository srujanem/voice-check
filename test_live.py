import sys, urllib.request, json, time
sys.stdout.reconfigure(encoding='utf-8')

# Hot-reload
req = urllib.request.Request('http://127.0.0.1:5000/reload_text_model',
      data=b'{}', headers={'Content-Type':'application/json','X-API-Key':'authguard-default-key-2024'})
res = json.loads(urllib.request.urlopen(req, timeout=10).read())
print('Reload:', res)
time.sleep(1)

print()
print('=== Live Text API Test ===')
tests = [
    ('AI',    'The implementation of artificial intelligence in modern healthcare systems represents a paradigm shift in diagnostic methodologies. Furthermore, the utilization of machine learning algorithms enables unprecedented accuracy in pattern recognition.'),
    ('AI',    'In this essay I will delve into the multifaceted dimensions of climate change and its far-reaching implications. It is important to note that the ramifications of greenhouse gas emissions extend beyond mere temperature fluctuations.'),
    ('Human', 'I went to the store today and bought some groceries. It was pretty hot outside but the walk was nice. My dog came with me.'),
    ('Human', 'honestly i have no idea why my code isnt working. ive been staring at it for 2 hours. maybe ill just restart lol'),
]
ok = 0
for label, text in tests:
    data = json.dumps({'text': text}).encode()
    req2 = urllib.request.Request('http://127.0.0.1:5000/predict_text', data=data,
           headers={'Content-Type':'application/json','X-API-Key':'authguard-default-key-2024'})
    res2 = json.loads(urllib.request.urlopen(req2, timeout=10).read())
    pred = res2.get('prediction','?')
    conf = res2.get('confidence','?')
    correct = (label=='AI' and 'AI' in pred) or (label=='Human' and 'Human' in pred)
    if correct: ok += 1
    status = 'OK' if correct else 'WRONG'
    print(f'  [{status}] Expected:{label} | Got:{pred} ({conf}%)')
print(f'Score: {ok}/4')
