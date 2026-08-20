import re

with open('dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the hardcoded metrics and table body with IDs so we can inject them via JS
html = html.replace('<div class="metric-value">1,248</div>', '<div class="metric-value" id="dash-total-scans">0</div>')
html = html.replace('<div class="metric-value">342</div>', '<div class="metric-value" id="dash-ai-threats">0</div>')
html = html.replace('<div class="metric-value">98.4%</div>', '<div class="metric-value" id="dash-avg-conf">0%</div>')

table_start = html.find('<tbody>')
table_end = html.find('</tbody>') + len('</tbody>')

if table_start != -1 and table_end != -1:
    html = html[:table_start] + '<tbody id="dash-recent-scans"></tbody>' + html[table_end:]

# Add history.js to the scripts
html = html.replace('<script src="auth.js"></script>', '<script src="auth.js"></script>\n    <script src="history.js"></script>')

# Add JS logic to populate real data
js_inject = """
            // 2.5 Populate Real Data from history.js
            try {
                const historyStr = localStorage.getItem('ai_detection_history') || '[]';
                const scans = JSON.parse(historyStr);
                
                document.getElementById('dash-total-scans').textContent = scans.length;
                const aiBlocked = scans.filter(s => s.isAi).length;
                document.getElementById('dash-ai-threats').textContent = aiBlocked;
                
                let avg = 0;
                if (scans.length > 0) {
                    const totalConf = scans.reduce((acc, s) => acc + (s.confidence || 0), 0);
                    avg = (totalConf / scans.length).toFixed(1);
                }
                document.getElementById('dash-avg-conf').textContent = avg + '%';

                const tbody = document.getElementById('dash-recent-scans');
                if (scans.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-secondary);">No scans yet. Start using the tools to see data here.</td></tr>';
                } else {
                    tbody.innerHTML = scans.slice(0, 8).map(scan => {
                        let icon = 'fa-file';
                        let color = '#94a3b8';
                        if (scan.type.toLowerCase() === 'voice') { icon = 'fa-microphone'; color = '#06b6d4'; }
                        if (scan.type.toLowerCase() === 'image') { icon = 'fa-image'; color = '#8b5cf6'; }
                        if (scan.type.toLowerCase() === 'text') { icon = 'fa-file-lines'; color = '#06b6d4'; }
                        if (scan.type.toLowerCase() === 'url') { icon = 'fa-link'; color = '#8b5cf6'; }
                        if (scan.type.toLowerCase() === 'video') { icon = 'fa-video'; color = '#06b6d4'; }

                        const badge = scan.isAi 
                            ? '<span class="status-badge status-fake">' + Math.round(scan.confidence) + '% AI Generated</span>'
                            : '<span class="status-badge status-authentic">' + Math.round(scan.confidence) + '% Human</span>';

                        return <tr>
                            <td><i class="fa-solid \" style="color:\; margin-right:8px;"></i> \</td>
                            <td>\</td>
                            <td>\</td>
                            <td>\</td>
                            <td><a href="#" style="color:var(--text-secondary);"><i class="fa-solid fa-file-pdf"></i> PDF</a></td>
                        </tr>;
                    }).join('');
                }
            } catch(e) { console.error('Dashboard data error', e); }
"""

# Insert JS logic right after Initialize Chart.js
html = html.replace('// 3. Initialize Chart.js', js_inject + '\n            // 3. Initialize Chart.js')

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
