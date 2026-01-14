import os
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.database import update_lesson_audio

router = Router()

# Получаем ID админов из.env
ADMIN_IDS =

class AudioUpload(StatesGroup):
    waiting_for_lesson_id = State()
    waiting_for_file = State()

# Проверка на админа
def is_admin(user_id):
    return user_id in ADMIN_IDS

@router.message(Command("add_audio"))
async def start_audio_upload(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Введите номер урока (ID), к которому нужно прикрепить аудио:")
    await state.set_state(AudioUpload.waiting_for_lesson_id)

@router.message(AudioUpload.waiting_for_lesson_id)
async def process_lesson_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return
    
    await state.update_data(lesson_id=int(message.text))
    await message.answer("Теперь отправьте мне аудиофайл или голосовое сообщение.")
    await state.set_state(AudioUpload.waiting_for_file)

@router.message(AudioUpload.waiting_for_file, F.audio | F.voice)
async def process_audio_file(message: Message, state: FSMContext):
    data = await state.get_data()
    lesson_id = data['lesson_id']
    
    # Получаем file_id от Telegram (уникальная строка)
    if message.audio:
        file_id = message.audio.file_id
    else:
        file_id = message.voice.file_id
        
    # Сохраняем в БД
    await update_lesson_audio(lesson_id, file_id)
    
    await message.answer(f"✅ Аудио успешно прикреплено к уроку {lesson_id}!")
    await state.clear()