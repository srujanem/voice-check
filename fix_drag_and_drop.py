import glob
import re

js_files = glob.glob('c:/voice-check/**/*.js', recursive=True)

for filepath in js_files:
    if 'node_modules' in filepath or 'old_script.js' in filepath: continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Fix the dangling });
    new_content = re.sub(
        r'// PDF Download logic\s*}\);\s*function preventDefaults',
        '// PDF Download logic\n\n    function preventDefaults',
        content
    )
    
    # 2. Add the missing preventDefaults attachment if it's missing but preventDefaults exists
    if 'function preventDefaults' in new_content and 'dropZone.addEventListener(eventName, preventDefaults' not in new_content:
        new_content = re.sub(
            r'(function preventDefaults\(e\) \{\s*e\.preventDefault\(\);\s*e\.stopPropagation\(\);\s*\})',
            r"\1\n\n    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {\n        if (typeof dropZone !== 'undefined') dropZone.addEventListener(eventName, preventDefaults, false);\n    });",
            new_content
        )
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")
