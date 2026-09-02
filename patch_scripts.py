import os

mint_logic = '''
        // Make Mint button ready
        const mintBtn = document.getElementById('mint-report-btn');
        if (mintBtn) {
            mintBtn.dataset.ready = "true";
            if (typeof updateWalletUI === 'function') updateWalletUI();
        }
        '''

for ui in ['voice-ui', 'video-ui', 'document-ui']:
    script_path = f'c:/voice-check/{ui}/script.js'
    if not os.path.exists(script_path): continue
    with open(script_path, 'r', encoding='utf-8') as f:
        js = f.read()
    
    if 'mintBtn.dataset.ready' not in js:
        if ui == 'voice-ui':
            js = js.replace("resultState.classList.remove('hidden');", "resultState.classList.remove('hidden');" + mint_logic)
        else:
            js = js.replace("resultsSection.classList.remove('hidden');", "resultsSection.classList.remove('hidden');" + mint_logic)
            
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(js)
