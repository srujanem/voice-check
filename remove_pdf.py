import os
import glob
import re

def process_html_files():
    html_files = glob.glob('c:/voice-check/*-ui/*.html')
    html_files.append('c:/voice-check/result.html')
    for filepath in html_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove html2pdf script tag
        content = re.sub(r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/html2pdf\.js/[^"]+"></script>\s*', '', content)

        # Remove buttons
        # In document-ui, it's inside a flex div with reset-btn
        if 'document-ui' in filepath:
            content = re.sub(
                r'<div style="display: flex; gap: 15px; margin-top: 20px;">\s*<button id="reset-btn" class="btn-secondary" style="flex: 1; justify-content: center;">\s*<i class="fa-solid fa-rotate-right"></i> Scan New Document\s*</button>\s*<button id="download-btn" class="btn-primary" style="flex: 1; justify-content: center;">\s*<i class="fa-solid fa-file-pdf"></i> Download PDF Report\s*</button>\s*</div>',
                '<button id="reset-btn" class="btn-secondary" style="width: 100%; margin-top: 20px; justify-content: center;">\n                <i class="fa-solid fa-rotate-right"></i> Scan New Document\n            </button>',
                content
            )
        else:
            # Other files have button id="download-btn" or id="downloadPdfBtn"
            content = re.sub(r'<button[^>]*id="download(?:Pdf|-)?btn"[^>]*>.*?</button>\s*', '', content, flags=re.DOTALL | re.IGNORECASE)
            
            # Voice UI has some aria-label variant
            content = re.sub(r'<button[^>]*aria-label="Download PDF report"[^>]*>.*?</button>\s*', '', content, flags=re.DOTALL | re.IGNORECASE)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Processed HTML: {filepath}")

def process_js_files():
    js_files = glob.glob('c:/voice-check/*-ui/*.js')
    for filepath in js_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # General PDF download block block
        content = re.sub(
            r'// PDF Download logic\s*const downloadBtn = document\.getElementById\(\'download-btn\'\);\s*if \(downloadBtn\) {.*?\}\s*}\);\s*}',
            '',
            content,
            flags=re.DOTALL
        )
        
        # Another variant
        content = re.sub(
            r'const downloadBtn = document\.getElementById\(\'download-btn\'\);\s*if \(downloadBtn\) {.*?\}\s*}\);\s*}',
            '',
            content,
            flags=re.DOTALL
        )

        # document-ui variant (inline addEventListener)
        content = re.sub(
            r'document\.getElementById\(\'download-btn\'\)\.addEventListener\(\'click\', \(\) => {.*?html2pdf\(\)\.set\(opt\)\.from\(element\)\.save\(\);\s*}\);',
            '',
            content,
            flags=re.DOTALL
        )

        # Batch UI variant
        content = re.sub(
            r'const downloadPdfBtn = document\.getElementById\(\'downloadPdfBtn\'\);\s*if \(downloadPdfBtn\) {.*?\}\s*}\);\s*}',
            '',
            content,
            flags=re.DOTALL
        )

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Processed JS: {filepath}")

if __name__ == '__main__':
    process_html_files()
    process_js_files()
