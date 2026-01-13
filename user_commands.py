from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from utils.database import add_user

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await add_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "Сәлем! (Привет!)\n\n"
        "Я ваш автоматический репетитор казахского языка. "
        "Моя задача — помочь вам освоить язык с нуля до уверенного разговорного уровня.\n\n"
        "📅 <b>Как это работает?</b>\n"
        "Я буду присылать вам новый урок два раза в неделю: в понедельник и четверг.\n"
        "Курс состоит из 102 уроков.\n\n"
        "Ничего нажимать не нужно, просто ждите первого занятия!"
    )