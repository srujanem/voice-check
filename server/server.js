const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const port = 5001;

app.use(cors());
app.use(bodyParser.json());

const dbPath = path.resolve(__dirname, 'database.sqlite');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Error opening database', err.message);
    } else {
        console.log('Connected to the SQLite database.');
        db.serialize(() => {
            db.run(`CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                name TEXT
            )`);
            db.run(`CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                type TEXT,
                fileName TEXT,
                isAi INTEGER,
                confidence REAL,
                date TEXT
            )`);
        });
    }
});

app.post('/api/users', (req, res) => {
    const { email, name } = req.body;
    if (!email) {
        return res.status(400).json({ error: 'Email is required' });
    }
    
    db.run(`INSERT OR IGNORE INTO users (email, name) VALUES (?, ?)`, [email, name], function(err) {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json({ message: 'User processed', email, name });
    });
});

app.post('/api/history', (req, res) => {
    const { email, type, fileName, isAi, confidence, date } = req.body;
    
    if (!email) {
        return res.status(400).json({ error: 'Email is required' });
    }

    const stmt = db.prepare(`INSERT INTO history (email, type, fileName, isAi, confidence, date) VALUES (?, ?, ?, ?, ?, ?)`);
    stmt.run([email, type, fileName, isAi ? 1 : 0, confidence, date], function(err) {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json({ id: this.lastID, email, type, fileName, isAi, confidence, date });
    });
    stmt.finalize();
});

app.get('/api/history', (req, res) => {
    const email = req.query.email;
    if (!email) {
        return res.status(400).json({ error: 'Email is required' });
    }

    db.all(`SELECT * FROM history WHERE email = ? ORDER BY id DESC`, [email], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});

process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});
