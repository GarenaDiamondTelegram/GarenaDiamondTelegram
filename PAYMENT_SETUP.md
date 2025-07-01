# 💸 Настройка платежной системы

## 🚀 Быстрый старт

Для работы платежей нужно настроить Telegram бота с платежными функциями.

## 📋 Шаги настройки

### 1. Создание бота
```bash
# Создайте бота через @BotFather
/newbot
# Введите имя: YourGameBot
# Введите username: your_game_bot
```

### 2. Настройка платежей
```bash
# В @BotFather выберите вашего бота
/mybots -> YourGameBot -> Bot Settings -> Payments

# Подключите провайдера:
# - Для тестирования: Test Provider
# - Для продакшена: YooKassa, Stripe, или другие
```

### 3. Получение токенов

#### Для Telegram Stars (XTR):
- Токен провайдера: `""` (пустая строка)
- Валюта: `"XTR"`
- Минимальная сумма: 1 звезда

#### Для TON:
- Нужен специальный провайдер TON
- Или используйте TON Connect SDK

### 4. Обновление кода

В файле `index.html` замените:

```javascript
// Строка 123: замените на имя вашего бота
return `https://t.me/your_game_bot?${params.toString()}`;

// Строка 156: замените URL бота
const botUrl = `https://t.me/your_game_bot?start=ton_${category}_${itemType}_${price}_${currentUserId}`;

// Строка 201: замените URL бота  
const botUrl = `https://t.me/your_game_bot?start=stars_${category}_${itemType}_${price}_${currentUserId}`;
```

## 🤖 Код бота (Python)

```python
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import LabeledPrice, PreCheckoutQuery

API_TOKEN = 'YOUR_BOT_TOKEN'
PROVIDER_TOKEN = 'YOUR_PROVIDER_TOKEN'  # Пустой для Stars

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    args = message.get_args().split('_')
    
    if len(args) >= 5:
        currency, category, item_type, price, user_id = args[:5]
        
        if currency == 'stars':
            await send_stars_invoice(message, item_type, int(price), user_id)
        elif currency == 'ton':
            await send_ton_invoice(message, item_type, float(price), user_id)

async def send_stars_invoice(message, item_type, price, user_id):
    prices = [LabeledPrice(label=f"Бустер {item_type}", amount=price)]
    
    await bot.send_invoice(
        chat_id=message.chat.id,
        title=f"⭐ Бустер {item_type}",
        description=f"Покупка бустера за {price} Telegram Stars",
        payload=f"stars_{item_type}_{user_id}",
        provider_token="",  # Пустой для Stars
        currency="XTR",
        prices=prices,
        need_name=False,
        need_phone_number=False,
        need_email=False
    )

@dp.pre_checkout_query_handler()
async def pre_checkout_handler(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment_handler(message: types.Message):
    payment = message.successful_payment
    # Здесь обработайте успешный платеж
    # Отправьте webhook в ваше приложение
    
if __name__ == '__main__':
    asyncio.run(dp.start_polling())
```

## 🔗 Webhook настройка

Для интеграции с веб-приложением:

```python
# Отправляйте POST запрос в ваше приложение
import requests

async def notify_webapp(user_id, item_type, category):
    webhook_url = "https://your-app.com/api/payment-success"
    data = {
        "user_id": user_id,
        "item_type": item_type,
        "category": category,
        "timestamp": time.time()
    }
    requests.post(webhook_url, json=data)
```

## 📱 Тестирование

1. **Локальное тестирование:**
   - Используйте кнопку "Демо покупка" 
   - Все бустеры активируются без оплаты

2. **Тестовые платежи:**
   - В @BotFather включите Test Mode
   - Используйте тестовые карты провайдера

3. **Продакшен:**
   - Получите реальные токены провайдера
   - Обновите PROVIDER_TOKEN в боте

## 🚨 Важные моменты

- **Безопасность:** Никогда не храните токены в клиентском коде
- **Валидация:** Всегда проверяйте платежи на сервере
- **Логирование:** Ведите логи всех транзакций
- **Fallback:** Предусмотрите альтернативные способы оплаты

## 🔧 Быстрая настройка для демо

Если нужно быстро протестировать:

1. Замените в коде все функции оплаты на `simulatePayment()`
2. Все покупки будут бесплатными
3. Пользователи смогут тестировать функционал

```javascript
function buyBooster(type, price, currency) {
    // Быстрое демо - все бесплатно
    simulatePayment(type, 'booster');
}
```

## 📞 Поддержка

- Документация Telegram Bot API: https://core.telegram.org/bots/api#payments
- TON Connect: https://docs.ton.org/develop/dapps/ton-connect
- Telegram Stars: https://core.telegram.org/bots/payments#stars