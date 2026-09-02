import os

dirs = ['voice-ui', 'deepfake-ui', 'document-ui', 'video-ui']

for ui in dirs:
    index_path = f'c:/voice-check/{ui}/index.html'
    if not os.path.exists(index_path): continue
    
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 1. Add Ethers.js & web3.js if not present
    if 'web3.js' not in html:
        scripts = '''<script src="https://cdnjs.cloudflare.com/ajax/libs/ethers/6.10.0/ethers.umd.min.js"></script>
    <script src="/web3.js?v=20260825"></script>
    <script src="/theme.js'''
        html = html.replace('<script src="/theme.js', scripts)
        
    # 2. Add Connect Wallet btn if not present
    if 'connectWalletBtn' not in html:
        wallet_btn = '''<button id="connectWalletBtn" class="btn-secondary" style="margin-left: 10px; border-color: rgba(255,255,255,0.1);"><i class="fa-solid fa-wallet"></i> Connect Wallet</button>
                <a href="/index.html'''
        html = html.replace('<a href="/index.html', wallet_btn, 1)
        
    # 3. Add Mint btn if not present
    if 'mint-report-btn' not in html:
        mint_btn = '''<button id="mint-report-btn" class="btn-primary" style="justify-content: center; padding: 14px; display: none; background: linear-gradient(135deg, #8b5cf6, #d946ef); border: none; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);">
                    <i class="fa-brands fa-ethereum"></i> Anchor to Blockchain
                </button>'''
        
        # Inject after download-pdf-btn or reset-btn
        if 'id="download-pdf-btn"' in html:
            html = html.replace('</button>\n            </div>\n        </section>', '</button>\n                ' + mint_btn + '\n            </div>\n        </section>')
            html = html.replace('</button>\r\n            </div>\r\n        </section>', '</button>\r\n                ' + mint_btn + '\r\n            </div>\r\n        </section>')
        elif 'id="reset-btn"' in html:
            html = html.replace('Check Another\n                </button>', 'Check Another\n                </button>\n                ' + mint_btn)
            html = html.replace('Check Another\r\n                </button>', 'Check Another\r\n                </button>\r\n                ' + mint_btn)
            
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)

    # 4. Modify script.js
    script_path = f'c:/voice-check/{ui}/script.js'
    if not os.path.exists(script_path): continue
    
    with open(script_path, 'r', encoding='utf-8') as f:
        js = f.read()
        
    if 'mintBtn.dataset.ready' not in js:
        mint_logic = '''
        // Make Mint button ready
        const mintBtn = document.getElementById('mint-report-btn');
        if (mintBtn) {
            mintBtn.dataset.ready = "true";
            if (typeof updateWalletUI === 'function') updateWalletUI();
        }
        '''
        
        if "resultsSection.classList.remove('hidden')" in js:
            js = js.replace("resultsSection.classList.remove('hidden');", "resultsSection.classList.remove('hidden');" + mint_logic)
        elif "resultsSection.style.display" in js:
            js = js.replace("resultsSection.style.display = 'block';", "resultsSection.style.display = 'block';" + mint_logic)
            
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(js)
