from utils.database import aiosqlite, DB_NAME

async def load_curriculum_if_empty():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT count(*) FROM lessons")
        count = await cursor.fetchone()
        if count[0] > 0:
            return

        lessons = [
            (1, "Казахский алфавит", "Текст урока 1...", None, "Прочитайте: Ана", "Ана"),
            (2, "Специфический звук Ә", "Текст урока 2...", None, "Переведите: Папа", "Әке"),
            #... Здесь должны быть прописаны все 102 урока по структуре выше
            # Для краткости отчета полный список 102 кортежей опущен, но в реальном коде они должны быть здесь.
        ]
        
        await db.executemany(
            "INSERT INTO lessons (id, title, content, audio_file_id, exercise_question, exercise_answer) VALUES (?,?,?,?,?,?)",
            lessons
        )

        await db.commit()
