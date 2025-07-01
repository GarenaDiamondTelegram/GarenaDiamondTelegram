#!/usr/bin/env python3
"""
🤖 Telegram Bot для платежей в Garena Diamond Game

Этот бот обрабатывает платежи Telegram Stars для вашей игры.
Для запуска нужно:
1. Создать бота через @BotFather
2. Получить токен бота
3. Установить зависимости: pip install aiogram
4. Заменить BOT_TOKEN на ваш токен
"""

import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# 🔧 Настройки
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Замените на токен вашего бота
WEBHOOK_URL = "https://your-game-url.com/api/webhook"  # URL вашей игры для уведомлений

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 💎 Товары в игре
GAME_ITEMS = {
    'speed': {
        'name': '🚀 Ускорение тапов x2',
        'description': 'Увеличивает скорость тапов в 2 раза на 30 минут',
        'price': 100
    },
    'diamonds': {
        'name': '💎 Утроенные алмазы x3', 
        'description': 'Утраивает получение алмазов на 1 час',
        'price': 200
    },
    'energy': {
        'name': '⚡ Дополнительная энергия +50',
        'description': 'Мгновенно восстанавливает 50 единиц энергии',
        'price': 10  # В TON единицах, конвертируется в Stars
    },
    'mega': {
        'name': '🔥 Мега буст x5',
        'description': 'Увеличивает все бонусы в 5 раз на 2 часа',
        'price': 50  # В TON единицах
    },
    'vip': {
        'name': '👑 VIP Статус',
        'description': 'Премиум подписка на 30 дней с эксклюзивными бонусами',
        'price': 200  # В TON единицах
    }
}

@dp.message(Command('start'))
async def start_handler(message: types.Message):
    """Обработка команды /start с параметрами оплаты"""
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if not args:
        # Обычный старт без параметров
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Открыть игру", url="https://your-game-url.com")],
            [InlineKeyboardButton(text="💰 Тест платежей", callback_data="test_payments")]
        ])
        
        await message.answer(
            "🎮 <b>Добро пожаловать в Garena Diamond Game!</b>\n\n"
            "Этот бот обрабатывает платежи для игры.\n"
            "Для покупок используйте кнопки в игре.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return
    
    # Парсим параметры: currency_category_itemtype_price_userid
    if len(args[0].split('_')) >= 5:
        params = args[0].split('_')
        currency, category, item_type, price, user_id = params[:5]
        
        if currency == 'stars' and item_type in GAME_ITEMS:
            await send_stars_invoice(message, item_type, category, user_id)
        elif currency == 'ton' and item_type in GAME_ITEMS:
            await send_ton_invoice(message, item_type, category, user_id)
        else:
            await message.answer("❌ Неизвестный товар или валюта")
    else:
        await message.answer("❌ Неверные параметры платежа")

async def send_stars_invoice(message: types.Message, item_type: str, category: str, user_id: str):
    """Отправка инвойса для оплаты Telegram Stars"""
    item = GAME_ITEMS[item_type]
    
    prices = [LabeledPrice(label=item['name'], amount=item['price'])]
    
    try:
        await bot.send_invoice(
            chat_id=message.chat.id,
            title=f"⭐ {item['name']}",
            description=item['description'],
            payload=f"stars_{category}_{item_type}_{user_id}_{message.date.timestamp()}",
            provider_token="",  # Пустой для Telegram Stars
            currency="XTR",
            prices=prices,
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            send_phone_number_to_provider=False,
            send_email_to_provider=False,
            is_flexible=False,
            start_parameter=f"stars_{category}_{item_type}_{item['price']}"
        )
        
        await message.answer(
            f"💫 <b>Инвойс создан!</b>\n\n"
            f"Товар: {item['name']}\n"
            f"Цена: {item['price']} ⭐ Stars\n\n"
            f"Нажмите кнопку 'Pay' для оплаты",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        await message.answer(f"❌ Ошибка создания инвойса: {e}")

async def send_ton_invoice(message: types.Message, item_type: str, category: str, user_id: str):
    """Отправка инвойса для TON (через Stars для демо)"""
    item = GAME_ITEMS[item_type]
    
    # Конвертируем TON в Stars для демо (1 TON = 100 Stars)
    stars_price = item['price'] * 100
    prices = [LabeledPrice(label=item['name'], amount=stars_price)]
    
    try:
        await bot.send_invoice(
            chat_id=message.chat.id,
            title=f"💎 {item['name']} (TON)",
            description=f"{item['description']}\n\n💡 Демо: оплата через Stars вместо TON",
            payload=f"ton_{category}_{item_type}_{user_id}_{message.date.timestamp()}",
            provider_token="",  # Пустой для Telegram Stars
            currency="XTR",
            prices=prices,
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            send_phone_number_to_provider=False,
            send_email_to_provider=False,
            is_flexible=False,
            start_parameter=f"ton_{category}_{item_type}_{item['price']}"
        )
        
        await message.answer(
            f"💎 <b>TON Инвойс создан!</b>\n\n"
            f"Товар: {item['name']}\n"
            f"Цена: {item['price']} TON (= {stars_price} ⭐ в демо)\n\n"
            f"🔧 В продакшене здесь будет реальный TON платеж",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error creating TON invoice: {e}")
        await message.answer(f"❌ Ошибка создания TON инвойса: {e}")

@dp.callback_query(lambda c: c.data == "test_payments")
async def test_payments_handler(callback: types.CallbackQuery):
    """Показать тестовые платежи"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Тест 100 ⭐", callback_data="test_stars_speed")],
        [InlineKeyboardButton(text="💎 Тест 200 ⭐", callback_data="test_stars_diamonds")],
        [InlineKeyboardButton(text="🔥 Тест TON", callback_data="test_ton_mega")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")]
    ])
    
    await callback.message.edit_text(
        "🧪 <b>Тестовые платежи</b>\n\n"
        "Выберите товар для тестирования платежной системы:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.callback_query(lambda c: c.data.startswith("test_"))
async def handle_test_payment(callback: types.CallbackQuery):
    """Обработка тестовых платежей"""
    test_type = callback.data.replace("test_", "")
    
    if test_type == "stars_speed":
        await send_stars_invoice(callback.message, "speed", "booster", "test_user")
    elif test_type == "stars_diamonds":
        await send_stars_invoice(callback.message, "diamonds", "booster", "test_user")
    elif test_type == "ton_mega":
        await send_ton_invoice(callback.message, "mega", "booster", "test_user")

@dp.pre_checkout_query()
async def pre_checkout_handler(query: PreCheckoutQuery):
    """Проверка перед оплатой"""
    # Здесь можно добавить дополнительные проверки
    await bot.answer_pre_checkout_query(query.id, ok=True)
    logger.info(f"Pre-checkout approved for: {query.invoice_payload}")

@dp.message(lambda message: message.content_type == types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment_handler(message: types.Message):
    """Обработка успешного платежа"""
    payment = message.successful_payment
    payload_data = payment.invoice_payload.split('_')
    
    if len(payload_data) >= 4:
        currency, category, item_type, user_id = payload_data[:4]
        
        # Уведомляем пользователя
        item = GAME_ITEMS.get(item_type, {})
        await message.answer(
            f"✅ <b>Платеж успешен!</b>\n\n"
            f"Товар: {item.get('name', item_type)}\n"
            f"Сумма: {payment.total_amount} {payment.currency}\n"
            f"ID транзакции: {payment.telegram_payment_charge_id}\n\n"
            f"🎮 Товар будет активирован в игре в течение нескольких секунд",
            parse_mode="HTML"
        )
        
        # Отправляем webhook в игру
        await notify_game_webhook(user_id, item_type, category, payment)
        
        logger.info(f"Payment successful: {payment.invoice_payload}")
    else:
        logger.error(f"Invalid payload format: {payment.invoice_payload}")

async def notify_game_webhook(user_id: str, item_type: str, category: str, payment):
    """Отправка уведомления в игру о успешном платеже"""
    # Здесь бы был реальный HTTP запрос к вашему серверу игры
    webhook_data = {
        "user_id": user_id,
        "item_type": item_type,
        "category": category,
        "amount": payment.total_amount,
        "currency": payment.currency,
        "transaction_id": payment.telegram_payment_charge_id,
        "timestamp": payment.invoice_payload.split('_')[-1] if '_' in payment.invoice_payload else None
    }
    
    logger.info(f"Would send webhook to game: {webhook_data}")
    # import aiohttp
    # async with aiohttp.ClientSession() as session:
    #     async with session.post(WEBHOOK_URL, json=webhook_data) as response:
    #         logger.info(f"Webhook response: {response.status}")

async def main():
    """Запуск бота"""
    logger.info("🚀 Garena Diamond Bot starting...")
    
    # Удаляем старые апдейты
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")