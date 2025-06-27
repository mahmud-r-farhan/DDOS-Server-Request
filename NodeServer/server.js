const http = require('http');
const fs = require('fs');
const path = require('path');

let requestCount = 0;
const logFile = path.join(__dirname, 'logs.json');
let logs = [];

if (fs.existsSync(logFile)) {
    try {
        logs = JSON.parse(fs.readFileSync(logFile, 'utf-8'));
    } catch (err) {
        console.error("❌ Failed to parse existing logs. Starting fresh.");
        logs = [];
    }
}

const server = http.createServer((req, res) => {
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

    // Response
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end(`Hello! You are visitor #${requestCount}\n`);
});

const PORT = 3000;
server.listen(PORT, () => {
    console.log(`🚀 Server running at http://localhost:${PORT}`);
});
