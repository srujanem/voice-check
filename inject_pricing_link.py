import os
import glob
import re

html_files = glob.glob(r'D:\voice-check\voice-check\*.html')
html_files += glob.glob(r'D:\voice-check\voice-check\*-ui\*.html')

for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    if '<a href="pricing.html">Pricing</a>' not in content and '<a href="/pricing.html">Pricing</a>' not in content and '<a href="../pricing.html">Pricing</a>' not in content:
        if '-ui' in filepath or 'creator' in filepath:
            pricing_link = '<a href="../pricing.html">Pricing</a>'
        else:
            pricing_link = '<a href="pricing.html">Pricing</a>'
            
        if '<a href="#faq">FAQ</a>' in content:
            content = content.replace('<a href="#faq">FAQ</a>', f'{pricing_link}\n  <a href="#faq">FAQ</a>')
        elif '<a href="../index.html#faq">FAQ</a>' in content:
            content = content.replace('<a href="../index.html#faq">FAQ</a>', f'{pricing_link}\n  <a href="../index.html#faq">FAQ</a>')
        elif '<a href="api-docs.html">Documentation</a>' in content:
             content = content.replace('<a href="api-docs.html">Documentation</a>', f'{pricing_link}\n  <a href="api-docs.html">Documentation</a>')
        elif '<a href="../api-docs.html">Documentation</a>' in content:
             content = content.replace('<a href="../api-docs.html">Documentation</a>', f'{pricing_link}\n  <a href="../api-docs.html">Documentation</a>')
        
        with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(content)
            
print("Injected pricing links")
