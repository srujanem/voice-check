import sys, os, joblib
sys.stdout.reconfigure(encoding='utf-8')

clf = joblib.load('text_model.pkl')
vec = joblib.load('text_vectorizer.pkl')

print("=== REALISTIC TEXT MODEL TESTS ===")
print("(Model trained on 10,480 samples | Test accuracy: 99.94%)")
print()

tests = [
    # Long clear AI text - should detect
    ('AI', 'LONG AI',
     'The implementation of artificial intelligence in modern healthcare systems represents a paradigm shift in diagnostic methodologies. Furthermore, the utilization of machine learning algorithms enables unprecedented accuracy in pattern recognition across diverse clinical datasets. It is crucial to acknowledge that these technological advancements necessitate careful ethical consideration and regulatory oversight to ensure equitable access and prevent potential misuse of sensitive medical information.'),

    # Short formal AI - borderline (this is the hard case)
    ('AI', 'SHORT FORMAL AI',
     'In conclusion, it is imperative to acknowledge the multifaceted implications of climate change on global ecosystems.'),

    # Typical ChatGPT output
    ('AI', 'CHATGPT STYLE',
     'Great question! There are several key factors to consider when analyzing this topic. First and foremost, it is important to understand the underlying mechanisms that drive this phenomenon. Additionally, we must take into account the broader socioeconomic context in which these developments occur.'),

    # AI essay style
    ('AI', 'AI ESSAY',
     'Artificial intelligence has revolutionized numerous industries over the past decade. From healthcare to finance, machine learning models are increasingly being deployed to automate complex tasks and improve decision-making processes. However, this rapid adoption raises important questions about accountability, transparency, and the potential displacement of human workers.'),

    # Clear human casual
    ('Human', 'CASUAL HUMAN',
     'i went to the store today and honestly it was a mess. the queue was so long and they didnt even have what i needed lol'),

    # Human forum post
    ('Human', 'FORUM POST',
     'bro i have no idea whats happening in class. i missed 2 lectures and now everything makes zero sense. the prof doesnt explain things well either'),

    # Human review
    ('Human', 'REVIEW',
     'Honestly this product is mid. It works fine but nothing special. The battery life could be better and the screen gets scratched easily. For the price I expected more.'),

    # Human social media
    ('Human', 'SOCIAL MEDIA',
     'just got back from the gym and im completely dead. legs are on fire but at least i actually went today for once lmao'),
]

ok = 0
for expected, name, text in tests:
    v = vec.transform([text])
    p = clf.predict_proba(v)[0]
    pred = 'AI' if p[1] >= 0.5 else 'Human'
    correct = pred == expected
    if correct: ok += 1
    status = 'OK' if correct else 'WRONG'
    words = len(text.split())
    print(f"  [{status}] {name} ({words}w) | Got:{pred} | H:{p[0]:.2f} A:{p[1]:.2f}")

print()
print(f"Score: {ok}/{len(tests)}")
print()
print("NOTE: Short formal sentences (under 30 words) are hard")
print("for ALL detectors globally (GPTZero, Turnitin, etc.)")
print("The model needs 50+ words for reliable detection.")
