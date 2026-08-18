import sys, os, time, joblib
sys.stdout.reconfigure(encoding='utf-8')

print('=== TEXT MODEL FILES ===')
for f in ['text_model.pkl', 'text_vectorizer.pkl']:
    if os.path.exists(f):
        size = os.path.getsize(f)/1024
        mtime = time.ctime(os.path.getmtime(f))
        print(f'  [OK] {f}: {size:.0f} KB | Trained: {mtime}')
    else:
        print(f'  [MISSING] {f}')

print()
print('=== DATASET ===')
total_ai = 0
total_human = 0
for cls, label in [('human','Human'), ('ai','AI'), ('ai_generated','AI Extra')]:
    path = f'dataset_text/{cls}'
    if os.path.exists(path):
        files = [f for f in os.listdir(path) if f.endswith('.txt')]
        print(f'  {label}: {len(files)} files')
        if 'human' in cls:
            total_human += len(files)
        else:
            total_ai += len(files)
    else:
        print(f'  {label}: FOLDER MISSING')
print(f'  --- Total Human: {total_human} | Total AI: {total_ai} | Grand total: {total_human+total_ai}')

print()
print('=== MODEL SANITY TEST ===')
clf = joblib.load('text_model.pkl')
vec = joblib.load('text_vectorizer.pkl')
print(f'  Model type : {type(clf).__name__}')
print(f'  Classes    : {list(clf.classes_)}  (0=Human, 1=AI)')

tests = [
    ('AI',    'The implementation of artificial intelligence in modern healthcare systems represents a paradigm shift in diagnostic methodologies. Furthermore, the utilization of machine learning algorithms enables unprecedented accuracy in pattern recognition across diverse clinical datasets.'),
    ('AI',    'In conclusion, it is imperative to acknowledge the multifaceted implications of climate change on global ecosystems. The ramifications of unchecked carbon emissions are far-reaching and require immediate collaborative action.'),
    ('AI',    'ChatGPT is a large language model developed by OpenAI. It uses transformer architecture trained on vast amounts of internet text data to generate human-like responses.'),
    ('Human', 'i went to the store today and honestly it was a mess. the queue was so long and they didnt even have what i needed lol'),
    ('Human', 'bro i have no idea whats happening in class. i missed 2 lectures and now everything makes zero sense'),
    ('Human', 'just got back from the gym and im completely dead. legs are on fire but at least i actually went today'),
]

ok = 0
print()
for label, text in tests:
    v = vec.transform([text])
    p = clf.predict_proba(v)[0]
    pred = 'AI' if p[1] >= 0.5 else 'Human'
    status = 'OK' if pred == label else 'WRONG'
    if pred == label:
        ok += 1
    print(f'  [{status}] Expected:{label:5} | Got:{pred:5} | Human:{p[0]:.2f} AI:{p[1]:.2f}')

print()
print(f'  Sanity Score: {ok}/{len(tests)}')
flag = 'GOOD' if ok >= 5 else 'NEEDS RETRAINING'
print(f'  Status: {flag}')
