import codecs

with codecs.open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add nav-auth into nav-right
html = html.replace(
    '<div class="nav-right">\r\n  <div class="theme-toggle" id="themeToggle" style="position:static;">',
    '<div class="nav-right">\r\n  <div id="nav-auth"></div>\r\n  <div class="theme-toggle" id="themeToggle" style="position:static;">'
)

# 2. Add auth.js to the bottom and initialize it
script_inject = '''
<script src="auth.js?v=2"></script>
<script>
    document.addEventListener('DOMContentLoaded', () => {
        if (window.injectNavAuthState) {
            window.injectNavAuthState(document.getElementById('nav-auth'));
        }
    });
</script>
</body>
'''
html = html.replace('</body>', script_inject)

with codecs.open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
