import os
pricing_path = r'D:\voice-check\voice-check\pricing.html'

with open(pricing_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("<button class=\"btn-pricing btn-primary\" onclick=\"alert('Payment integration coming soon!')\">Upgrade to Pro</button>", "<a href=\"checkout.html\" class=\"btn-pricing btn-primary\">Upgrade to Pro</a>")

with open(pricing_path, 'w', encoding='utf-8') as f:
    f.write(content)
