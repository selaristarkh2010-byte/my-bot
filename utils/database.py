import aiosqlite
import logging

DB_NAME = "database/kazakh_bot.db"

async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        # Таблица пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                current_lesson_id INTEGER DEFAULT 0,
                active BOOLEAN DEFAULT 1,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Таблица уроков
        await db.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY,
                title TEXT,
                content TEXT,
                audio_file_id TEXT,
                exercise_question TEXT,
                exercise_answer TEXT
            )
        """)
        await db.commit()
        logging.info("База данных инициализирована.")

async def add_user(user_id: int, username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?,?)",
            (user_id, username)
        )
        await db.commit()

async def get_user_progress(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT current_lesson_id FROM users WHERE user_id =?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row if row else 0

async def update_user_progress(user_id: int, new_lesson_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET current_lesson_id =? WHERE user_id =?", (new_lesson_id, user_id))
        await db.commit()

async def get_lesson(lesson_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        # Используем Row Factory для доступа по именам полей
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM lessons WHERE id =?", (lesson_id,)) as cursor:
            return await cursor.fetchone()

async def update_lesson_audio(lesson_id: int, file_id: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE lessons SET audio_file_id =? WHERE id =?", (file_id, lesson_id))
        await db.commit()

async def get_all_active_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users WHERE active = 1") as cursor:
            return await cursor.fetchall()