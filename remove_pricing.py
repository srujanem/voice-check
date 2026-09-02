import os
import re

auth_path = r'D:\voice-check\voice-check\auth.js'
with open(auth_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the checkScanGate with a dummy that always returns True
dummy_gate = '''window.checkScanGate = function() {
    return true; // Pricing and scan limits have been removed
};
'''

# Find the old checkScanGate definition and replace it
content = re.sub(r'window\.checkScanGate = function\(\) \{[\s\S]*?(?=// --- END PREMIUM SCAN GATE ---|export|window\.)', dummy_gate + '\n\n', content)

# Remove the '1/2 Free Scans' badge from the navbar in auth.js
content = re.sub(r'let scans = parseInt\(localStorage\.getItem\(\'free_scans_used\'\) \|\| \'0\', 10\);.*?<div class="pro-badge guest-badge">.*?</div>', '', content, flags=re.DOTALL)
content = re.sub(r'<div class="pro-badge guest-badge">\s*\$\{scans\}/2 Free\s*</div>', '', content, flags=re.DOTALL)

with open(auth_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Remove Pricing links from index.html
index_path = r'D:\voice-check\voice-check\index.html'
with open(index_path, 'r', encoding='utf-8') as f:
    idx_content = f.read()
idx_content = re.sub(r'<a href="pricing\.html".*?>Pricing</a>', '', idx_content)
with open(index_path, 'w', encoding='utf-8') as f:
    f.write(idx_content)

# Remove Pricing links from blog.html
blog_path = r'D:\voice-check\voice-check\blog.html'
if os.path.exists(blog_path):
    with open(blog_path, 'r', encoding='utf-8') as f:
        blog_content = f.read()
    blog_content = re.sub(r'<a href="pricing\.html".*?>Pricing</a>', '', blog_content)
    with open(blog_path, 'w', encoding='utf-8') as f:
        f.write(blog_content)
        
print("Pricing removed from UI files.")
