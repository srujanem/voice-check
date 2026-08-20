import codecs

with codecs.open('login.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the mock user localstorage setting to match auth.js
old_js = '''localStorage.setItem('authguard_user', JSON.stringify(mockUser));
                localStorage.setItem('auth_token', mockUser.token);'''

new_js = '''localStorage.setItem('auth_email', mockUser.email);
                localStorage.setItem('user_name', mockUser.name);
                localStorage.setItem('auth_token', mockUser.token);'''

html = html.replace(old_js, new_js)

with codecs.open('login.html', 'w', encoding='utf-8') as f:
    f.write(html)
