from aiogram.types import Message
from aiogram import Router, F, Bot
from typing import Dict, Set, Optional
from aiogram.fsm.context import FSMContext

from utils.states import Form_anket, UserData, UserState

from keyboards.reply import rm_kb, main_kb, ank_kb
from keyboards.inline import get_update_anket_keyboard

from database import db

import os


bot = Bot(token="8412234786:AAHY1c4maly_mlS0sf1thPNc7FZcUZFGdao")
router = Router()  # Инифциализация роутера


user_data: Dict[int, UserData] = {}


def get_user_data(user_id: int) -> UserData:
    """Получает или создает данные пользователя"""
    if user_id not in user_data:
        user_data[user_id] = UserData()
    return user_data[user_id]


async def show_anket(user_id: int, anket: tuple, state: FSMContext):
    """Показывает анкету пользователю"""
    try:
        # Отправляем фото с подписью
        await bot.send_photo(
            chat_id=user_id,
            photo=anket[3],
            caption=format_anket_text(anket),
            parse_mode='HTML',
            reply_markup=ank_kb
        )
    except Exception as e:
        # Если фото не грузится, отправляем только текст
        await bot.send_message(
            chat_id=user_id,
            text=format_anket_text(anket),
            parse_mode='HTML',
            reply_markup=ank_kb
        )


def format_anket_text(anket: tuple) -> str:
    """Форматирует текст анкеты"""
    
    text = f"""
<b>ID:</b>    {int(anket[0])}\n
<b>Name:</b>  {anket[1]}
<b>Age:</b>   {anket[2]} years\n
<b>Stack:</b> {anket[4]}\n
<b>City:</b>  {anket[5]}\n
<b>About:</b> {anket[7]}\n
<b>Registartion date:</b>\n{anket[6]}UTC(+3)
"""

    return text


async def show_next_anket(user_id: int, state: FSMContext):
    """Показывает следующую анкету"""
    data = get_user_data(user_id)
    ankets = db.create_pool_ankets(user_id)
    
    if not ankets:
        await bot.send_message(
            user_id,
            "🎉 Ты просмотрел все анкеты! Возвращайся позже.",
            reply_markup=main_kb
        )
        await state.clear()
        return
    
    # Если анкета последняя 
    if data.current_index >= len(ankets):
        await bot.send_message(
            user_id,
            "🎉 Ты просмотрел все анкеты! Возвращайся позже.",
            reply_markup=main_kb
        )
        await state.clear()
        return
    

    anket = ankets[data.current_index]
    
    # Отмечаем как просмотренную
    data.viewed_ankets.add(anket[0])
    
    # Сохраняем текущую анкету в состояние
    await state.update_data(current_anket=anket)
    
    # Показываем анкету
    await show_anket(user_id, anket, state)


# Обработчик ["Лайк 👍", "Дизлайк 👎"] 
@router.message(UserState.viewing_ankets, F.text.in_(["Лайк 👍", "Дизлайк 👎"]))
async def handle_anket_action(message: Message, state: FSMContext):
    """Обрабатывает действия с анкетой"""
    user_id = message.from_user.id
    data = get_user_data(user_id)
    user = db.read_user(user_id)
    
    # Получаем текущую анкету из состояния
    state_data = await state.get_data()
    current_anket = state_data.get('current_anket')
    
    if not current_anket:
        await show_next_anket(user_id, state)
        return
    
    # Обрабатываем разные действия
    if message.text == "Лайк 👍":
        data.liked_ankets.add(current_anket[0])
        await message.answer(
            f"👍 Лайк для {current_anket[1]} отправлен!"
        )
        await bot.send_message(chat_id=current_anket[0], text=f'Ты понравился {user[0][1]}')
        

    
    elif message.text == "Дизлайк 👎":
        await message.answer(
            f"👎 Пропускаем {current_anket[1]}..."
        )
    
    # Переходим к следующей анкете
    data.current_index += 1
    await show_next_anket(user_id, state)


@router.message(UserState.viewing_ankets, F.text == "Прекратить просмотр 💤")
async def exit_search(message: Message, state: FSMContext):
    """Выход из режима просмотра"""
    await message.answer(
        "👋 Ты вышел из режима поиска. Возвращайся скорее!",
        reply_markup=main_kb
    )
    await state.clear()


@router.message(F.text == 'Смотреть анкеты 🔍')  # Обработчик текста
async def handler_text(message: Message, state: FSMContext):
    """Начинает просмотр анкет"""
    user_id = message.from_user.id
    data = get_user_data(user_id)
    
    # Сбрасываем индекс
    data.current_index = 0
    
    # Проверяем, есть ли анкеты
    filtered_ankets = db.create_pool_ankets(user_id)
    
    if not filtered_ankets:
        await message.answer(
            "😔 Анкеты закончились! Попробуй зайти позже.",
            reply_markup=main_kb
            )
        return
    
    # Устанавливаем состояние просмотра
    await state.set_state(UserState.viewing_ankets)
    
    # Показываем первую анкету
    await show_next_anket(user_id, state)


@router.message(F.text == 'Заполнить анкету заново 🔄')
async def handler_text(message: Message):
    if not db.check_user(message.from_user.id):
        await message.answer(
        "❌ У вас нет анкеты для обновления!\n\n"
        "Создайте анкету: /registr")
        return

    await message.answer(
        "⚠️ <b>Вы точно хотите обновить свою анкету?</b>\n\n"
        "Это действие нельзя будет отменить!",
        reply_markup=get_update_anket_keyboard(),
        parse_mode='html')


@router.message(F.text == "Статистика 📊")
async def show_stats(message: Message):
    """Показывает статистику"""
    user_id = message.from_user.id
    data = get_user_data(user_id)

    ankets = db.create_pool_ankets(user_id)
    
    total_ankets = len(ankets)
    viewed = len(data.viewed_ankets)
    liked = len(data.liked_ankets)
    
    stats_text = f"""
📊 <b>Твоя статистика:</b>

👀 Просмотрено: {viewed}/{total_ankets}
❤️ Лайков поставлено: {liked}

📈 Прогресс: {int(viewed/total_ankets*100) if total_ankets > 0 else 0}%
    """
    
    await message.answer(stats_text, parse_mode='HTML')



@router.message()
async def handle_all_messages(message: Message, state: FSMContext):
    """Обработчик всех остальных сообщений"""
    current_state = await state.get_state()
    
    if current_state == UserState.viewing_ankets:
        await message.answer(
            "Используй кнопки под фото для действий с анкетой! 👆",
            reply_markup=ank_kb
        )
    elif current_state:
        await message.answer(
            "Пожалуйста, следуй инструкциям или отправь /cancel для отмены"
        )
    else:
        await message.answer(
            "Используй кнопки меню для навигации 👇",
            reply_markup=main_kb
        )