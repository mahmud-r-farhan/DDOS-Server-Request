const http = require('http');
const fs = require('fs');
const path = require('path');

let requestCount = 0;
const logFile = path.join(__dirname, 'logs.json');
let logs = [];

if (fs.existsSync(logFile)) {
    try {
        logs = JSON.parse(fs.readFileSync(logFile, 'utf-8'));
        requestCount = logs.length; // Set requestCount based on existing logs
    } catch (err) {
        console.error("❌ Failed to parse existing logs. Starting fresh.");
        logs = [];
    }
}

const server = http.createServer((req, res) => {
    // Handle API endpoint for fetching logs
    if (req.method === 'GET' && req.url === '/api/logs') {
        try {
            // Read logs.json file
            const logsData = fs.readFileSync(logFile, 'utf-8');
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(logsData);
            console.log('📤 Served logs.json via /api/logs');
            return;
        } catch (err) {
            console.error('❌ Error reading logs.json:', err);
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Failed to fetch logs' }));
            return;
        }
    }

    // Handle other requests (existing functionality)
    requestCount++;

    const forwardedFor = req.headers['x-forwarded-for'];
    const clientIp = forwardedFor
        ? forwardedFor.split(',')[0].trim()
        : req.socket.remoteAddress || 'Unknown';

    const isProxy = !!forwardedFor;

    // Prepare log entry
    const logEntry = {
        id: requestCount,
        method: req.method,
        url: req.url,
        ip: clientIp,
        proxyDetected: isProxy,
        userAgent: req.headers['user-agent'],
        timestamp: new Date().toISOString()
    };

    // Console output
    console.log(`📥 Request #${logEntry.id}: ${logEntry.method} ${logEntry.url}`);
    console.log(`   From IP: ${logEntry.ip}${isProxy ? ' (via proxy)' : ''}`);
    if (logEntry.userAgent) {
        console.log(`   User-Agent: ${logEntry.userAgent}`);
    }

    // Save log
    logs.push(logEntry);
    fs.writeFile(logFile, JSON.stringify(logs, null, 2), err => {
        if (err) console.error('❌ Error writing to log file:', err);
    });

    // Response for non-API requests
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end(`Hello! You are visitor #${requestCount}\n`);
});

const PORT = 5000;
server.listen(PORT, () => {
    console.log(`🚀 Server running at http://localhost:${PORT}`);
});