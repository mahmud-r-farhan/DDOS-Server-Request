const http = require('http');

let requestCount = 0;

const server = http.createServer((req, res) => {
    requestCount++;
    console.log(` Request #${requestCount} received: ${req.method} ${req.url}`);

    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end(`Hello! You are visitor #${requestCount}\n`);
});

const PORT = 3000;

server.listen(PORT, () => {
    console.log(` Server running at http://localhost:${PORT}`);
});
