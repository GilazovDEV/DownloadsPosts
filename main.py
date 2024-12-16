from telethon import TelegramClient, events
import os
import asyncio

# Замените эти значения на ваши
api_id = "1"
api_hash = "1"
phone_number = "+1"
group_link = '1'  # t.me/username или https://t.me/...
allowed_user_ids = [1]  # Список ID разрешённых пользователей

# Инициализация клиента
client = TelegramClient('session_name', api_id, api_hash)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    # Проверка на разрешённого пользователя
    if event.sender_id in allowed_user_ids or event.chat_id == group_link:
        await event.respond("Привет! Отправь ссылку на канал и укажи, сколько постов нужно скачать в формате: \n<code>ссылка количество</code>", parse_mode='html')
    else:
        await event.respond("У вас нет прав для использования этого бота.")

@client.on(events.NewMessage)
async def handle_message(event):
    # Проверка на разрешённого пользователя
    if event.sender_id in allowed_user_ids or event.chat_id == group_link:
        if event.is_private or event.chat_id == group_link:
            try:
                # Парсим сообщение
                message = event.message.text.split()
                if len(message) != 2:
                    raise ValueError("Формат должен быть: ссылка количество")

                channel_url = message[0]
                limit = int(message[1])

                # Подключаемся к каналу
                channel = await client.get_entity(channel_url)
                if not channel:
                    raise ValueError("Канал не найден!")

                # Скачиваем сообщения из канала
                count = 0
                async for message in client.iter_messages(channel, limit=limit):
                    if message.text:
                        # Отправляем текстовые сообщения в группу
                        await client.send_message(group_link, message.text)
                    if message.photo:
                        # Отправляем фотографии в группу
                        await client.send_file(group_link, message.media, caption=message.text if message.text else None)
                    count += 1

                await event.respond(f"Скачано {count} постов из канала {channel_url} и отправлено в группу.")
            except Exception as e:
                await event.respond(f"Произошла ошибка: {str(e)}")
    else:
        await event.respond("У вас нет прав для использования этого бота.")

async def main():
    await client.start(phone=phone_number)
    print("Бот запущен!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())