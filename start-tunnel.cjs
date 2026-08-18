const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const configPath = 'C:\\voice-check\\server-config.js';
const nodeServerCwd = 'C:\\\\voice-check';
const vercelCwd = 'C:\\\\voice-check';

console.log("===================================================");
console.log("      AUTHGUARD AI - GLOBAL ACCESS ACTIVATOR       ");
console.log("===================================================");
console.log("");
console.log("[1/2] Establishing secure global tunnel...");
const tunnelProc = spawn('C:\\voice-check\\cloudflared.exe', ['tunnel', '--url', 'http://localhost:8000'], { cwd: 'C:\\Server\\ai-training-panel' });

let urlFound = false;

tunnelProc.stderr.on('data', (data) => {
    const text = data.toString();
    
    // Look for the TryCloudflare URL in the logs
    const match = text.match(/https:\/\/[a-z0-9-]+\.trycloudflare\.com/);
    if (match && !urlFound) {
        urlFound = true;
        const globalUrl = match[0];
        console.log(`      -> SUCCESS! Global URL acquired: ${globalUrl}`);
        
        console.log("[2/2] Updating website to point to your PC...");
        
        // 3. Update server-config.js
        let configStr = fs.readFileSync(configPath, 'utf8');
        configStr = configStr.replace(/const DEFAULT_URL\s*=\s*['"][^'"]+['"];/, `const DEFAULT_URL = '${globalUrl}';`);
        fs.writeFileSync(configPath, configStr);
        
        // 3b. Register the URL with the running server so frontend can fetch it live
        const http = require('http');
        const body = JSON.stringify({ url: globalUrl });
        const reg = http.request('http://localhost:8000/api/tunnel-url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
        });
        reg.on('error', () => {});  // Ignore if server isn't up yet
        reg.write(body);
        reg.end();
        
        // 4. Trigger Vercel Deploy (uses saved token â€” never needs manual login)
        const tokenPath = 'C:\\voice-check\\vercel_token.txt';
        let vercelToken = '';
        try { vercelToken = fs.readFileSync(tokenPath, 'utf8').trim(); } catch {}
        
        const vercelArgs = ['vercel', '--prod', '--yes'];
        if (vercelToken) vercelArgs.push('--token', vercelToken);
        
        const vercelProc = spawn('npx', vercelArgs, { cwd: vercelCwd, shell: true });
        
        vercelProc.stdout.on('data', d => process.stdout.write(d));
        vercelProc.stderr.on('data', d => process.stderr.write(d));
        
        vercelProc.on('close', (code) => {
            if (code === 0) {
                console.log("\n===================================================");
                console.log("âœ… ALL DONE! Your phone can now connect to your PC!");
                console.log("ðŸŒ Visit: https://authguard.vercel.app");
                console.log("âš ï¸ Keep this window OPEN while using the app.");
                console.log("===================================================\n");
            } else {
                console.log("\nâŒ Deployment failed â€” trying without token...");
                // Fallback: try without token
                const fallback = spawn('npx', ['vercel', '--prod', '--yes'], { cwd: vercelCwd, shell: true });
                fallback.stdout.on('data', d => process.stdout.write(d));
                fallback.stderr.on('data', d => process.stderr.write(d));
            }
        });
    }
});

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log("\nShutting down global access...");
    tunnelProc.kill();
    process.exit(0);
});

