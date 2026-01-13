import sys
import asyncio

# Критическое исправление для Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Импорт наших модулей
from utils.database import create_tables, get_all_active_users, get_lesson, update_user_progress, get_user_progress
from handlers import user_commands, admin_panel
from curriculum_loader import load_curriculum_if_empty  # Модуль загрузки уроков

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# Инициализация бота
bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Функция рассылки уроков (Запускается планировщиком)
async def scheduled_lesson_delivery():
    logging.info("Запуск рассылки уроков...")
    users = await get_all_active_users()
    
    for user_tuple in users:
        user_id = user_tuple
        try:
            current_lesson = await get_user_progress(user_id)
            next_lesson_id = current_lesson + 1
            
            lesson_data = await get_lesson(next_lesson_id)
            
            if lesson_data:
                # Формирование сообщения
                text = (
                    f"📚 <b>Урок {lesson_data['id']}: {lesson_data['title']}</b>\n\n"
                    f"{lesson_data['content']}\n\n"
                    f"📝 <b>Задание:</b> {lesson_data['exercise_question']}\n"
                    f"<i>Ответ будет доступен в следующем уроке или по кнопке.</i>"
                )
                
                await bot.send_message(user_id, text)
                
                # Отправка аудио, если есть
                if lesson_data['audio_file_id']:
                    await bot.send_audio(user_id, lesson_data['audio_file_id'], caption="🎧 Прослушайте произношение")
                
                # Обновление прогресса
                await update_user_progress(user_id, next_lesson_id)
            else:
                # Если уроки закончились
                pass 
                
        except Exception as e:
            logging.error(f"Ошибка отправки пользователю {user_id}: {e}")

async def main():
    # 1. Создание таблиц БД
    await create_tables()
    
    # 2. Загрузка контента (102 урока), если БД пуста
    await load_curriculum_if_empty()
    
    # 3. Подключение роутеров (обработчиков)
    dp.include_router(user_commands.router)
    dp.include_router(admin_panel.router)
    
    # 4. Настройка планировщика
    scheduler = AsyncIOScheduler()
    # Запуск по понедельникам (mon) и четвергам (thu) в 10:00 утра
    scheduler.add_job(scheduled_lesson_delivery, 'cron', day_of_week='mon,thu', hour=10, minute=0)
    scheduler.start()
    
    # 5. Запуск опроса (Polling)
    logging.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")