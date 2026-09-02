import os

with open('c:/voice-check/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

live_scan = """<a class="nav-card tilt-card purple" href="/live-ui/index.html?v=20260825">
  <div style="font-size: 48px; margin-bottom: 20px; color: var(--accent-purple);"><i class="fa-solid fa-camera-web"></i></div>
  <h2>Live Scanner</h2>
  <p>Real-time deepfake detection directly from your webcam stream.</p>
  <div class="card-glare"></div>
</a>"""

document_scan = """<a class="nav-card tilt-card" href="/document-ui/index.html?v=20260825">
  <div style="font-size: 48px; margin-bottom: 20px; color: var(--accent-cyan);"><i class="fa-solid fa-file-invoice"></i></div>
  <h2>Document Scanner</h2>
  <p>Detect altered text, fake signatures, and forged documents instantly.</p>
  <div class="card-glare"></div>
</a>"""

if 'Live Scanner' not in html:
    html = html.replace('<div class="cards-grid " id="tools" style="scroll-margin-top: 80px;">', '<div class="cards-grid " id="tools" style="scroll-margin-top: 80px;">\n' + live_scan + '\n' + document_scan)
    with open('c:/voice-check/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
