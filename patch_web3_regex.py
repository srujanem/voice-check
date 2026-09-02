import os, re

dirs = ['voice-ui', 'deepfake-ui', 'document-ui', 'video-ui']

for ui in dirs:
    index_path = f'c:/voice-check/{ui}/index.html'
    if not os.path.exists(index_path): continue
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()

    mint_btn = '''<button id="mint-report-btn" class="btn-primary" style="justify-content: center; padding: 14px; display: none; background: linear-gradient(135deg, #8b5cf6, #d946ef); border: none; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);">
                    <i class="fa-brands fa-ethereum"></i> Anchor to Blockchain
                </button>'''

    if 'mint-report-btn' not in html:
        # Regex to match download-pdf-btn block
        if 'id="download-pdf-btn"' in html:
            html = re.sub(r'(<button id="download-pdf-btn"[\s\S]*?</button>)', r'\1\n' + mint_btn, html)
        elif 'id="reset-btn"' in html:
            html = re.sub(r'(<button id="reset-btn"[\s\S]*?</button>)', r'\1\n' + mint_btn, html)
            
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html)
