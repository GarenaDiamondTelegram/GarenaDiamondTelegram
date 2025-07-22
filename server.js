// server.js
const WebSocket = require('ws');
const PORT = process.env.PORT || 10000;
const server = new WebSocket.Server({ port: PORT });

let clients = [];

server.on('connection', ws => {
    clients.push(ws);
    ws.on('message', msg => {
        // Рассылаем сообщение всем клиентам
        clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(msg);
            }
        });
    });
    ws.on('close', () => {
        clients = clients.filter(c => c !== ws);
    });
});

console.log('WebSocket сервер запущен на порту', PORT); 