import requests

tests = [
    ('AI', 'Artificial Intelligence represents a significant paradigm shift in technology. The underlying architecture leverages advanced neural networks and machine learning algorithms. By utilizing deep learning frameworks, these systems can process and analyze vast amounts of data with remarkable efficiency. The implementation of such technologies requires careful consideration of ethical implications and societal impact.'),
    ('Human', 'Yesterday I went to the market with my mother. We bought some vegetables and fruits. The shopkeeper was very friendly and gave us a discount. On the way back, we stopped at a temple to pray. It was a good day overall and I felt happy spending time with family.'),
    ('Human', 'India became independent on 15th August 1947. The British ruled India for nearly 200 years. Many freedom fighters like Mahatma Gandhi, Subhas Chandra Bose and Bhagat Singh fought for the country. Gandhiji believed in non-violence and truth. The people of India made many sacrifices to get freedom from the British rule.'),
]

print('=' * 70)
print('  Expected     Got              AI%     Human%    Label')
print('=' * 70)
for expected, text in tests:
    try:
        r = requests.post('http://localhost:5000/predict_text', json={'text': text}, timeout=5)
        d = r.json()
        got = 'AI' if d.get('is_ai') else 'Human'
        status = 'OK' if got == expected else 'WRONG'
        ai_pct = d.get('prob_ai', 0)
        hm_pct = d.get('prob_human', 0)
        label = d.get('confidence_label', '?')
        print(f"  {expected:<12} {got:<16} {ai_pct:>5.1f}%   {hm_pct:>6.1f}%    [{label}]  {status}")
    except Exception as e:
        print(f"  {expected:<12} ERROR: {e}")
print('=' * 70)
