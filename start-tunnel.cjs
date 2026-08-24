const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const rootDir = path.resolve(__dirname);
const configPath = path.join(rootDir, 'server-config.js');

console.log("===================================================");
console.log("      AUTHGUARD AI - GLOBAL ACCESS ACTIVATOR       ");
console.log("===================================================");
console.log("");
console.log("[1/2] Establishing secure global tunnel...");

// Find cloudflared executable
let cfCmd = 'npx';
let cfArgs = ['-y', 'cloudflared', 'tunnel', '--url', 'http://localhost:5000', '--no-autoupdate'];
let cfCwd = rootDir;

const localCf = path.join(rootDir, 'cloudflared.exe');
const serverCf = 'D:\\Server\\ai-training-panel\\cloudflared.exe';

if (fs.existsSync(localCf)) {
    cfCmd = localCf;
    cfArgs = ['tunnel', '--url', 'http://localhost:5000', '--no-autoupdate'];
} else if (fs.existsSync(serverCf)) {
    cfCmd = serverCf;
    cfArgs = ['tunnel', '--url', 'http://localhost:5000', '--no-autoupdate'];
    cfCwd = 'D:\\Server\\ai-training-panel';
}

const tunnelProc = spawn(cfCmd, cfArgs, { cwd: cfCwd, shell: true });

let urlFound = false;

function handleOutput(data) {
    const text = data.toString();
    const match = text.match(/https:\/\/[a-z0-9-]+\.trycloudflare\.com/);
    
    if (match && !urlFound) {
        urlFound = true;
        const globalUrl = match[0];
        console.log(`      -> SUCCESS! Global URL acquired: ${globalUrl}`);
        
        console.log("[2/2] Updating website to point to your PC (via GitHub push)...");
        
        let configStr = fs.readFileSync(configPath, 'utf8');
        configStr = configStr.replace(/const DEFAULT_URL = '[^']+';/, `const DEFAULT_URL = '${globalUrl}';`);
        fs.writeFileSync(configPath, configStr);
        
        const gitAdd = spawn('git', ['add', 'server-config.js'], { cwd: rootDir, shell: true });
        gitAdd.on('close', () => {
            const gitCommit = spawn('git', ['commit', '-m', `chore: update tunnel url to ${globalUrl}`], { cwd: rootDir, shell: true });
            gitCommit.on('close', () => {
                const gitPush = spawn('git', ['push', 'origin', 'main'], { cwd: rootDir, shell: true });
                gitPush.stdout.on('data', d => process.stdout.write(d));
                gitPush.stderr.on('data', d => process.stderr.write(d));
                gitPush.on('close', (code) => {
                    if (code === 0) {
                        console.log("\n===================================================");
                        console.log("  ALL DONE! Your hosted website is now connected!");
                        console.log("  Visit: https://authguard.vercel.app (or https://voice-check.vercel.app)");
                        console.log("===================================================\n");
                    } else {
                        console.log(`\n Git push completed with code: ${code}.`);
                    }
                });
            });
        });
    }
}

tunnelProc.stdout.on('data', handleOutput);
tunnelProc.stderr.on('data', handleOutput);

process.on('SIGINT', () => {
    tunnelProc.kill();
    process.exit(0);
});
