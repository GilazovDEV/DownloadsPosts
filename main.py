from telethon import TelegramClient, events
import asyncio
import re



# Инициализация клиента
client = TelegramClient("session_name", api_id, api_hash)


# Получаем ID группы по ссылке
async def get_group_id():
    group = await client.get_entity(group_link)
    return group.id

# Команда для остановки бота
@client.on(events.NewMessage(pattern='/stop'))
async def stop(event):
    # Проверка на разрешённого пользователя
    if event.sender_id in allowed_user_ids:
        await event.respond("Бот останавливается...")
        await client.disconnect()
    else:
        await event.respond("У вас нет прав для использования этой команды.")

# Команда для старта
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    # Получаем ID группы по ссылке
    group_id = await get_group_id()

    # Проверка на разрешённого пользователя или если сообщение из группы
    if event.sender_id in allowed_user_ids or event.chat_id == group_id:
        await event.respond("Привет! Отправь ссылку на канал и укажи, сколько постов нужно скачать в формате: \n<code>/txt ссылка количество</code>, <code>/img ссылка количество</code> или <code>/all ссылка количество</code>", parse_mode='html')
    else:
        await event.respond("У вас нет прав для использования этого бота.")

# Команда /img — для скачивания и отправки только изображений
@client.on(events.NewMessage(pattern='/img'))
async def handle_img(event):
    # Получаем ID группы по ссылке
    group_id = await get_group_id()

    # Проверка на разрешённого пользователя или если сообщение из группы
    if event.sender_id in allowed_user_ids or event.chat_id == group_id:
        if event.is_private or event.chat_id == group_id:
            try:
                # Парсим сообщение (с использованием split для получения ссылки и числа)
                message = event.message.text.split(maxsplit=2)
                if len(message) != 3:
                    raise ValueError("Формат должен быть: /img ссылка количество")

                channel_url = message[1]
                limit = int(message[2])

                # Подключаемся к каналу
                channel = await client.get_entity(channel_url)
                if not channel:
                    raise ValueError("Канал не найден!")

                # Скачиваем изображения из канала
                count = 0
                async for message in client.iter_messages(channel, limit=limit):
                    if message.photo:
                        # Отправляем фотографии в группу
                        await client.send_file(group_id, message.media, caption=message.text if message.text else None)
                        count += 1
                    if count >= limit:  # Прерываем после достижения лимита
                        break

                    # Задержка 3 секунды между отправками
                    await asyncio.sleep(1)

                await event.respond(f"Скачано {count} изображений из канала {channel_url} и отправлено в группу.")
            except Exception as e:
                await event.respond(f"Произошла ошибка: {str(e)}")
    else:
        await event.respond("У вас нет прав для использования этого бота.")

# Команда /txt — для скачивания и отправки только текста
@client.on(events.NewMessage(pattern='/txt'))
async def handle_txt(event):
    # Получаем ID группы по ссылке
    group_id = await get_group_id()

    # Проверка на разрешённого пользователя или если сообщение из группы
    if event.sender_id in allowed_user_ids or event.chat_id == group_id:
        if event.is_private or event.chat_id == group_id:
            try:
                # Парсим сообщение (с использованием split для получения ссылки и числа)
                message = event.message.text.split(maxsplit=2)
                if len(message) != 3:
                    raise ValueError("Формат должен быть: /txt ссылка количество")

                channel_url = message[1]
                limit = int(message[2])

                # Подключаемся к каналу
                channel = await client.get_entity(channel_url)
                if not channel:
                    raise ValueError("Канал не найден!")

                # Скачиваем текстовые сообщения из канала
                count = 0
                async for message in client.iter_messages(channel, limit=limit):
                    if message.text:
                        # Убираем ссылки из текста
                        cleaned_text = re.sub(r'http[s]?://\S+', '', message.text)
                        # Отправляем текстовые сообщения в группу, если после очистки есть текст
                        if cleaned_text:
                            await client.send_message(group_id, cleaned_text)
                        count += 1
                    if count >= limit:  # Прерываем после достижения лимита
                        break

                    # Задержка 3 секунды между отправками
                    await asyncio.sleep(1)

                await event.respond(f"Скачано {count} текстовых сообщений из канала {channel_url} и отправлено в группу.")
            except Exception as e:
                await event.respond(f"Произошла ошибка: {str(e)}")
    else:
        await event.respond("У вас нет прав для использования этого бота.")

# Команда /all — для скачивания и отправки текстовых сообщений, фотографий и видео
@client.on(events.NewMessage(pattern='/all'))
async def handle_all(event):
    # Получаем ID группы по ссылке
    group_id = await get_group_id()

    # Проверка на разрешённого пользователя или если сообщение из группы
    if event.sender_id in allowed_user_ids or event.chat_id == group_id:
        if event.is_private or event.chat_id == group_id:
            try:
                # Парсим сообщение (с использованием split для получения ссылки и числа)
                message = event.message.text.split(maxsplit=2)
                if len(message) != 3:
                    raise ValueError("Формат должен быть: /all ссылка количество")

                channel_url = message[1]
                limit = int(message[2])

                # Подключаемся к каналу
                channel = await client.get_entity(channel_url)
                if not channel:
                    raise ValueError("Канал не найден!")

                # Скачиваем сообщения из канала (текст, фото и видео)
                count = 0
                async for message in client.iter_messages(channel, limit=limit):
                    if message.text:
                        # Убираем ссылки из текста
                        cleaned_text = re.sub(r'http[s]?://\S+', '', message.text)
                        # Отправляем текстовые сообщения в группу
                        if cleaned_text:
                            await client.send_message(group_id, cleaned_text)
                        count += 1
                    if message.photo or message.video:
                        # Отправляем фотографии и видео в группу с подписью (если есть текст)
                        await client.send_file(group_id, message.media, caption=message.text if message.text else None)
                        count += 1

                    if count >= limit:  # Прерываем после достижения лимита
                        break

                    # Задержка 3 секунды между отправками
                    await asyncio.sleep(3)

                await event.respond(f"Скачано {count} сообщений (текст, фото и видео) из канала {channel_url} и отправлено в группу.")
            except Exception as e:
                await event.respond(f"Произошла ошибка: {str(e)}")
    else:
        await event.respond("У вас нет прав для использования этого бота.")


# Команда /no_all — для скачивания и отправки только фотографий и видео
@client.on(events.NewMessage(pattern='/no_all'))
async def handle_no_all(event):
    # Получаем ID группы по ссылке
    group_id = await get_group_id()

    # Проверка на разрешённого пользователя или если сообщение из группы
    if event.sender_id in allowed_user_ids or event.chat_id == group_id:
        if event.is_private or event.chat_id == group_id:
            try:
                # Парсим сообщение (с использованием split для получения ссылки и числа)
                message = event.message.text.split(maxsplit=2)
                if len(message) != 3:
                    raise ValueError("Формат должен быть: /no_all ссылка количество")

                channel_url = message[1]
                limit = int(message[2])

                # Подключаемся к каналу
                channel = await client.get_entity(channel_url)
                if not channel:
                    raise ValueError("Канал не найден!")

                # Скачиваем сообщения из канала (только фотографии и видео)
                count = 0
                async for message in client.iter_messages(channel, limit=limit):
                    if message.photo or message.video:
                        # Отправляем фотографии и видео в группу
                        await client.send_file(group_id, message.media, caption=None)  # Без текста
                        count += 1

                    if count >= limit:  # Прерываем после достижения лимита
                        break

                    # Задержка 3 секунды между отправками
                    await asyncio.sleep(3)

                await event.respond(f"Скачано {count} медиафайлов (фото и видео) из канала {channel_url} и отправлено в группу.")
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