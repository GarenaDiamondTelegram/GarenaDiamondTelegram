# Sait WebSocket Server

## Описание
Простой WebSocket сервер для чата и мультиплеера сайта Sait.

## Запуск локально

1. Установите Node.js (16+)
2. Установите зависимости:
   ```
   npm install
   ```
3. Запустите сервер:
   ```
   npm start
   ```

Сервер будет доступен по адресу: ws://localhost:10000

## Развёртывание на render.com

1. Залейте этот проект на GitHub.
2. Создайте новый Web Service на render.com, выберите этот репозиторий.
3. Build Command: `npm install`
4. Start Command: `npm start`
5. После запуска используйте адрес вида:
   ```
   wss://your-app-name.onrender.com
   ```
   для подключения с сайта. 