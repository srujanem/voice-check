/**
 * AuthGuard Node.js API Server
 * Production-quality backend connecting the Vercel frontend to the local GPU AI engine.
 */
const express  = require('express');
const cors     = require('cors');
const fs       = require('fs');
const path     = require('path');
const os       = require('os');
const crypto   = require('crypto');
const { spawn } = require('child_process');
const multer   = require('multer');
const admin    = require('firebase-admin');

const app  = express();
const PORT = 8000;

// ─── Middleware ───────────────────────────────────────────────────────────────
app.use(cors());
app.use(express.json());

// ─── Firebase Admin SDK ───────────────────────────────────────────────────────
let firebaseReady = false;
const SERVICE_ACCOUNT_PATH = 'C:\\voice-check\\serviceAccountKey.json';

if (fs.existsSync(SERVICE_ACCOUNT_PATH)) {
    try {
        const serviceAccount = require(SERVICE_ACCOUNT_PATH);
        admin.initializeApp({ credential: admin.credential.cert(serviceAccount) });
        firebaseReady = true;
        console.log('[AUTH] Firebase Admin SDK initialized.');
    } catch (e) {
        console.error('[AUTH] Firebase init failed:', e.message);
    }
} else {
    console.warn('[AUTH] serviceAccountKey.json not found — using local auth fallback.');
}

// ─── File Upload (Multer) ─────────────────────────────────────────────────────
const UPLOAD_DIR = path.join(__dirname, 'uploads');
if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR, { recursive: true });

const upload = multer({
    dest: UPLOAD_DIR,
    limits: { fileSize: 100 * 1024 * 1024 }  // 100 MB max
});

// ─── Local User DB ────────────────────────────────────────────────────────────
const DB_DIR  = 'C:\\Data\\AI_Models';
const DB_PATH = path.join(DB_DIR, 'users.json');

function hashPassword(password) {
    return crypto.createHash('sha256').update(password + 'authguard_salt').digest('hex');
}

function getUsers() {
    if (!fs.existsSync(DB_PATH)) return {};
    try { return JSON.parse(fs.readFileSync(DB_PATH, 'utf8')); }
    catch { return {}; }
}

function saveUsers(users) {
    if (!fs.existsSync(DB_DIR)) fs.mkdirSync(DB_DIR, { recursive: true });
    fs.writeFileSync(DB_PATH, JSON.stringify(users, null, 2));
}

// ─── Auth Middleware Helper ───────────────────────────────────────────────────
function getUserFromToken(token) {
    const users = getUsers();
    for (const [username, data] of Object.entries(users)) {
        if (data.token === token || data.developer_api_key === token) {
            return { username, ...data };
        }
    }
    return null;
}

// ─── Webhooks & Usage tracking helpers ────────────────────────────────────────
function trackUsage(username) {
    const USAGE_PATH = 'C:\\Data\\AI_Models\\usage.json';
    try {
        let usage = {};
        if (fs.existsSync(USAGE_PATH)) {
            usage = JSON.parse(fs.readFileSync(USAGE_PATH, 'utf8'));
        }
        if (!usage[username]) usage[username] = { total: 0, daily: {} };
        const date = new Date().toISOString().split('T')[0];
        usage[username].total += 1;
        usage[username].daily[date] = (usage[username].daily[date] || 0) + 1;
        fs.writeFileSync(USAGE_PATH, JSON.stringify(usage, null, 2));
    } catch (e) {
        console.error('Usage tracking error:', e.message);
    }
}

function fireWebhook(username, result) {
    const WEBHOOKS_PATH = 'C:\\Data\\AI_Models\\webhooks.json';
    try {
        if (!fs.existsSync(WEBHOOKS_PATH)) return;
        const webhooks = JSON.parse(fs.readFileSync(WEBHOOKS_PATH, 'utf8'));
        const url = webhooks[username];
        if (url) {
            const parsedUrl = new URL(url);
            const reqLib = parsedUrl.protocol === 'https:' ? require('https') : require('http');
            const data = JSON.stringify(result);
            const req = reqLib.request(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) }
            });
            req.on('error', () => {});
            req.write(data);
            req.end();
        }
    } catch(e) {}
}

function requireAuth(req, res, next) {
    // AuthGuard is now open-access. Assign all traffic to an anonymous global user.
    req.user = { username: 'anonymous' };
    trackUsage('anonymous');
    next();
}

// ─── 1. Health Check ─────────────────────────────────────────────────────────
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', version: '2.0', timestamp: Date.now() });
});

// ─── 1b. Tunnel URL Registry (solves the stale-URL / Failed-to-fetch bug) ─────
// The start-tunnel.cjs POSTs the new Cloudflare URL here on every startup.
// The frontend GETs it live, so it never uses a stale baked-in URL.
let currentTunnelUrl = '';

app.get('/api/tunnel-url', (req, res) => {
    res.json({ url: currentTunnelUrl });
});

app.post('/api/tunnel-url', (req, res) => {
    const { url } = req.body;
    if (url && url.startsWith('https://')) {
        currentTunnelUrl = url;
        console.log(`[TUNNEL] Registered tunnel URL: ${url}`);
    }
    res.json({ ok: true });
});

// ─── 2. Hardware Telemetry ────────────────────────────────────────────────────
app.get('/api/telemetry', (req, res) => {
    const memTotal = os.totalmem();
    const memUsed  = memTotal - os.freemem();
    const cpus     = os.cpus();
    res.json({
        cpu_cores:  cpus.length,
        cpu_model:  cpus[0]?.model || 'Unknown',
        mem_used:   memUsed,
        mem_total:  memTotal,
        mem_pct:    ((memUsed / memTotal) * 100).toFixed(1) + '%',
        platform:   os.platform(),
        uptime_hrs: (os.uptime() / 3600).toFixed(1)
    });
});

// ─── 3. Training History ──────────────────────────────────────────────────────
const HISTORY_PATH = 'C:\\voice-check\\ai_panel_history.json';

app.get('/api/history', (req, res) => {
    if (!fs.existsSync(HISTORY_PATH)) return res.json([]);
    try {
        res.json(JSON.parse(fs.readFileSync(HISTORY_PATH, 'utf8')));
    } catch {
        res.status(500).json({ error: 'Failed to read history file.' });
    }
});

// ─── 4. Start Training Job ────────────────────────────────────────────────────
let activeTrainingProcess = null;

app.post('/api/train', (req, res) => {
    if (activeTrainingProcess) {
        return res.status(400).json({ error: 'A training job is already running.' });
    }

    const epochs  = parseInt(req.body.epochs) || 5;
    const jobType = req.body.type || 'image';
    const pyScript = 'C:\\Server\\ai-training-panel\\python_engine\\train.py';

    activeTrainingProcess = spawn('python', [pyScript, '--type', jobType, '--epochs', String(epochs)]);

    activeTrainingProcess.stdout.on('data', d => process.stdout.write('[PY] ' + d));
    activeTrainingProcess.stderr.on('data', d => process.stderr.write('[PY ERR] ' + d));

    activeTrainingProcess.on('close', (code) => {
        console.log(`[TRAIN] Process exited with code ${code}`);
        activeTrainingProcess = null;

        // Log to history file
        try {
            const hist = fs.existsSync(HISTORY_PATH)
                ? JSON.parse(fs.readFileSync(HISTORY_PATH, 'utf8'))
                : [];
            hist.push({
                id:        Date.now(),
                job_type:  jobType,
                epochs:    epochs,
                exit_code: code,
                timestamp: new Date().toISOString(),
                trigger:   'external_website'
            });
            fs.writeFileSync(HISTORY_PATH, JSON.stringify(hist, null, 2));
        } catch (e) {
            console.error('[TRAIN] Failed to write history:', e.message);
        }
    });

    res.json({ message: 'Training job dispatched!', epochs, type: jobType });
});

// ─── 5. Real AI Inference ─────────────────────────────────────────────────────
app.post('/api/infer', requireAuth, upload.single('file'), (req, res) => {
    if (!req.file) return res.status(400).json({ error: 'No file uploaded.' });

    const modelType = req.body.type || 'image';
    const pyScript  = 'C:\\Server\\ai-training-panel\\python_engine\\inference.py';
    const filePath  = req.file.path;

    const inferProcess = spawn('python', [pyScript, '--file', filePath, '--type', modelType], {
        env: { ...process.env, TF_ENABLE_ONEDNN_OPTS: '0', TF_CPP_MIN_LOG_LEVEL: '3' }
    });

    let stdout = '';
    let stderr = '';

    inferProcess.stdout.on('data', d => { stdout += d.toString(); });
    inferProcess.stderr.on('data', d => { stderr += d.toString(); });

    // 5-minute timeout (TensorFlow needs time to load on first run)
    const timeout = setTimeout(() => {
        inferProcess.kill('SIGTERM');
        fs.unlink(filePath, () => {});
        if (!res.headersSent) {
            res.status(504).json({ error: 'Inference timed out after 5 minutes.' });
        }
    }, 300000);

    inferProcess.on('close', (code) => {
        clearTimeout(timeout);
        fs.unlink(filePath, () => {});  // Always clean up

        if (res.headersSent) return;

        if (code !== 0) {
            console.error('[INFER] Python exited with code', code, '| stderr:', stderr);
            return res.status(500).json({
                error:   'Inference engine failed.',
                details: stderr.slice(0, 500)  // Don't expose full stack trace
            });
        }

        try {
            // Extract the last valid JSON object from stdout (in case Python printed warnings)
            const lastBrace = stdout.lastIndexOf('}');
            const firstBrace = stdout.indexOf('{');
            if (firstBrace === -1 || lastBrace === -1) throw new Error('No JSON found in output');
            const result = JSON.parse(stdout.substring(firstBrace, lastBrace + 1));
            res.json(result);
            fireWebhook(req.user.username, result);
        } catch (e) {
            res.status(500).json({ error: 'Failed to parse inference result.', raw: stdout.slice(0, 300) });
        }
    });
});

// ─── 6. Watermark Engine ──────────────────────────────────────────────────────
app.post('/api/watermark', upload.single('file'), (req, res) => {
    if (!req.file) return res.status(400).json({ error: 'No file uploaded.' });

    const action   = req.body.action === 'encode' ? 'encode' : 'decode';
    const message  = (req.body.message || 'AuthGuard Human Signature').slice(0, 200);
    const pyScript = 'C:\\Server\\ai-training-panel\\python_engine\\watermark.py';
    const inFile   = req.file.path;
    const outFile  = path.join(UPLOAD_DIR, `wm_${Date.now()}.png`);

    const args = ['--action', action, '--file', inFile];
    if (action === 'encode') args.push('--message', message, '--out', outFile);

    const proc = spawn('python', [pyScript, ...args]);
    let stdout  = '';
    let stderr  = '';
    proc.stdout.on('data', d => stdout += d);
    proc.stderr.on('data', d => stderr += d);

    proc.on('close', () => {
        fs.unlink(inFile, () => {});
        try {
            const lastBrace  = stdout.lastIndexOf('}');
            const firstBrace = stdout.indexOf('{');
            const result     = JSON.parse(stdout.substring(firstBrace, lastBrace + 1));

            if (action === 'encode' && result.status === 'success' && fs.existsSync(outFile)) {
                res.download(outFile, 'protected_image.png', () => fs.unlink(outFile, () => {}));
            } else {
                res.json(result);
            }
        } catch {
            res.status(500).json({ error: 'Watermark engine failed.', details: stderr.slice(0, 300) });
        }
    });
});



// ─── 11. URL Scanner ──────────────────────────────────────────────────────────
app.post('/api/scan-url', requireAuth, (req, res) => {
    const { url, type } = req.body;
    if (!url) return res.status(400).json({ error: 'Missing url in body.' });

    let modelType = type || 'auto';
    if (modelType === 'auto') {
        const lowerUrl = url.toLowerCase();
        if (lowerUrl.endsWith('.mp3') || lowerUrl.endsWith('.wav')) modelType = 'voice';
        else if (lowerUrl.endsWith('.mp4')) modelType = 'video';
        else modelType = 'image';
    }

    let parsedUrl;
    try {
        parsedUrl = new URL(url);
    } catch (e) {
        return res.status(400).json({ error: 'Invalid URL.' });
    }
    const reqLib = parsedUrl.protocol === 'https:' ? require('https') : require('http');
    const tempFilePath = path.join(UPLOAD_DIR, `url_scan_${Date.now()}`);

    const fileStream = fs.createWriteStream(tempFilePath);
    const request = reqLib.get(url, (response) => {
        if (response.statusCode !== 200) {
            fs.unlink(tempFilePath, () => {});
            return res.status(400).json({ error: 'Download failed: ' + response.statusCode });
        }
        response.pipe(fileStream);
        fileStream.on('finish', () => {
            fileStream.close();
            
            const pyScript = 'C:\\Server\\ai-training-panel\\python_engine\\inference.py';
            const inferProcess = spawn('python', [pyScript, '--file', tempFilePath, '--type', modelType], {
                env: { ...process.env, TF_ENABLE_ONEDNN_OPTS: '0', TF_CPP_MIN_LOG_LEVEL: '3' }
            });
            
            let stdout = '';
            let stderr = '';
            inferProcess.stdout.on('data', d => { stdout += d.toString(); });
            inferProcess.stderr.on('data', d => { stderr += d.toString(); });

            const timeout = setTimeout(() => {
                inferProcess.kill('SIGTERM');
                fs.unlink(tempFilePath, () => {});
                if (!res.headersSent) res.status(504).json({ error: 'Inference timed out.' });
            }, 300000);

            inferProcess.on('close', (code) => {
                clearTimeout(timeout);
                fs.unlink(tempFilePath, () => {});
                
                if (res.headersSent) return;
                if (code !== 0) return res.status(500).json({ error: 'Inference engine failed.', details: stderr.slice(0, 500) });
                
                try {
                    const lastBrace = stdout.lastIndexOf('}');
                    const firstBrace = stdout.indexOf('{');
                    if (firstBrace === -1 || lastBrace === -1) throw new Error('No JSON found');
                    const result = JSON.parse(stdout.substring(firstBrace, lastBrace + 1));
                    res.json(result);
                    fireWebhook(req.user.username, result);
                } catch (e) {
                    res.status(500).json({ error: 'Failed to parse result.' });
                }
            });
        });
    }).on('error', (err) => {
        fs.unlink(tempFilePath, () => {});
        res.status(400).json({ error: 'Download error: ' + err.message });
    });
});

// ─── 12. Shareable Results ────────────────────────────────────────────────────
const SHARED_RESULTS_PATH = 'C:\\Data\\AI_Models\\shared_results.json';

app.post('/api/results/save', requireAuth, (req, res) => {
    const { result, filename, type } = req.body;
    if (!result) return res.status(400).json({ error: 'Missing result object.' });

    const id = crypto.randomBytes(8).toString('hex');
    let shared = {};
    if (fs.existsSync(SHARED_RESULTS_PATH)) {
        shared = JSON.parse(fs.readFileSync(SHARED_RESULTS_PATH, 'utf8'));
    }
    
    shared[id] = {
        result,
        filename: filename || 'unknown',
        type: type || 'image',
        timestamp: Date.now(),
        username: req.user.username
    };
    fs.writeFileSync(SHARED_RESULTS_PATH, JSON.stringify(shared, null, 2));
    res.json({ id });
});

app.get('/api/results/:id', (req, res) => {
    if (!fs.existsSync(SHARED_RESULTS_PATH)) return res.status(404).json({ error: 'Not found' });
    const shared = JSON.parse(fs.readFileSync(SHARED_RESULTS_PATH, 'utf8'));
    const item = shared[req.params.id];
    
    if (!item) return res.status(404).json({ error: 'Not found' });
    
    if (Date.now() - item.timestamp > 7 * 24 * 60 * 60 * 1000) {
        delete shared[req.params.id];
        fs.writeFileSync(SHARED_RESULTS_PATH, JSON.stringify(shared, null, 2));
        return res.status(404).json({ error: 'Result expired' });
    }
    
    res.json(item.result);
});

// ─── 13. Webhook Storage & Usage Tracking ─────────────────────────────────────
const WEBHOOKS_PATH = 'C:\\Data\\AI_Models\\webhooks.json';

app.post('/api/webhooks/register', requireAuth, (req, res) => {
    const { url } = req.body;
    if (!url) return res.status(400).json({ error: 'Missing url.' });
    
    let webhooks = {};
    if (fs.existsSync(WEBHOOKS_PATH)) {
        webhooks = JSON.parse(fs.readFileSync(WEBHOOKS_PATH, 'utf8'));
    }
    webhooks[req.user.username] = url;
    fs.writeFileSync(WEBHOOKS_PATH, JSON.stringify(webhooks, null, 2));
    res.json({ message: 'Webhook registered' });
});

app.get('/api/usage', requireAuth, (req, res) => {
    const USAGE_PATH = 'C:\\Data\\AI_Models\\usage.json';
    if (!fs.existsSync(USAGE_PATH)) return res.json({ total_calls: 0, daily: {} });
    
    const usage = JSON.parse(fs.readFileSync(USAGE_PATH, 'utf8'));
    const userUsage = usage[req.user.username] || { total: 0, daily: {} };
    res.json({ total_calls: userUsage.total, daily: userUsage.daily });
});

// ─── Start Server ─────────────────────────────────────────────────────────────
app.listen(PORT, () => {
    console.log(`\n AuthGuard Node API Server`);
    console.log(`  Listening on  : http://localhost:${PORT}`);
    console.log(`  Firebase Auth : ${firebaseReady ? 'enabled' : 'local fallback'}`);
    console.log(`  Upload dir    : ${UPLOAD_DIR}\n`);
});
