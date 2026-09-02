with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the mobile bottom nav
old_nav = '''<a class="mob-nav-item" href="text-ui/index.html" id="mnav-text">
<i class="fa-solid fa-file-lines mn-icon"></i>
<span>Text (Chatbot)</span>'''
new_nav = '''<a class="mob-nav-item" href="text-ui/index.html" id="mnav-text">
<i class="fa-solid fa-robot mn-icon"></i>
<span>Chatbot</span>'''
html = html.replace(old_nav, new_nav)

# Replace the drawer nav
old_drawer = '''<a class="drawer-tool-card" href="text-ui/index.html">
<i class="fa-solid fa-font" style="color:#06b6d4"></i>
Text (Chatbot)
</a>'''
new_drawer = '''<a class="drawer-tool-card" href="text-ui/index.html">
<i class="fa-solid fa-robot" style="color:#06b6d4"></i>
Chatbot
</a>'''
html = html.replace(old_drawer, new_drawer)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
