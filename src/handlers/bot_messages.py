from aiogram.types import Message
from aiogram import Router, F, Bot
from typing import Dict
from aiogram.fsm.context import FSMContext

from utils.states import UserData, UserState

from keyboards.reply import main_kb, ank_kb
from keyboards.inline import get_update_anket_keyboard, get_profile_keyboard

from database import db

import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token="8412234786:AAHY1c4maly_mlS0sf1thPNc7FZcUZFGdao")
router = Router()

user_data: Dict[int, UserData] = {}


def get_user_data(user_id: int) -> UserData:
    """Получает или создает данные пользователя"""
    if user_id not in user_data:
        user_data[user_id] = UserData()
    return user_data[user_id]


async def show_anket(user_id: int, anket: dict, state: FSMContext):
    """Показывает анкету пользователю (анкета как словарь)"""
    try:
        # Отправляем фото с подписью
        await bot.send_photo(
            chat_id=user_id,
            photo=anket['photo'],  # Обращаемся по ключу, а не по индексу
            caption=format_anket_text(anket),
            parse_mode='HTML',
            reply_markup=ank_kb
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке фото: {e}")
        # Если фото не грузится, отправляем только текст
        try:
            await bot.send_message(
                chat_id=user_id,
                text=format_anket_text(anket),
                parse_mode='HTML',
                reply_markup=ank_kb
            )
        except Exception as e2:
            logging.error(f"Ошибка при отправке текста: {e2}")
            await bot.send_message(
                chat_id=user_id,
                text="❌ Ошибка при загрузке анкеты",
                reply_markup=main_kb
            )


def format_anket_text(anket: dict) -> str:
    """Форматирует текст анкеты из словаря"""

    # Безопасно получаем значения с проверкой
    user_id = anket.get('id', 'Не указан')
    full_name = anket.get('full_name', 'Не указано')
    age = anket.get('age', 'Не указан')
    stack = anket.get('stack', 'Не указан')
    city = anket.get('city', 'Не указан')
    about_self = anket.get('about_self', 'Не указано')
    reg_date = anket.get('registration_date', 'Не указана')

    text = f"""
<b>ID:</b> {user_id}

<b>Имя:</b> {full_name}
<b>Возраст:</b> {age} лет
<b>Стек:</b> {stack}
<b>Город:</b> {city}
<b>О себе:</b> {about_self}
<b>Дата регистрации:</b> {reg_date}
"""
    return text


async def show_next_anket(user_id: int, state: FSMContext):
    """Показывает следующую анкету"""
    max_attempts = 10
    attempts = 0

    while attempts < max_attempts:
        # Получаем следующую анкету из БД
        anket = db.get_next_profile(user_id)

        if not anket:
            await bot.send_message(
                user_id,
                "🎉 Ты просмотрел все доступные анкеты! Возвращайся позже.",
                reply_markup=main_kb
            )
            await state.clear()
            return

        # Проверяем, не совпадает ли с предыдущей
        state_data = await state.get_data()
        prev_anket = state_data.get('current_anket')

        if prev_anket and anket['id'] == prev_anket['id']:
            attempts += 1
            continue

        # Нашли подходящую анкету
        break

    if attempts >= max_attempts:
        await bot.send_message(
            user_id,
            "😅 Что-то пошло не так. Попробуй позже.",
            reply_markup=main_kb
        )
        await state.clear()
        return

    # Сохраняем текущую анкету в состояние
    await state.update_data(current_anket=anket)

    # Показываем анкету
    await show_anket(user_id, anket, state)


# Обработчик ["Лайк 👍", "Дизлайк 👎"]
@router.message(UserState.viewing_ankets, F.text.in_(["Лайк 👍", "Дизлайк 👎"]))
async def handle_anket_action(message: Message, state: FSMContext):
    """Обрабатывает действия с анкетой"""
    user_id = message.from_user.id

    # Получаем текущую анкету из состояния
    state_data = await state.get_data()
    current_anket = state_data.get('current_anket')

    if not current_anket:
        await show_next_anket(user_id, state)
        return

    # Получаем данные текущего пользователя
    current_user = db.read_user(user_id)
    if not current_user:
        await message.answer("❌ Ошибка: пользователь не найден")
        return

    # Сообщение о действии
    action_msg = await message.answer("⏳ Обрабатываю...")

    # Обрабатываем разные действия
    if message.text == "Лайк 👍":
        # Сохраняем лайк в БД
        is_mutual, liked_user, current_user_data = db.like_user(
            user_id, current_anket['id']
        )

        await action_msg.edit_text(
            f"👍 Ты лайкнул(а) {current_anket['full_name']}!"
        )

        # 🔔 УВЕДОМЛЕНИЕ ПОЛЬЗОВАТЕЛЮ, КОТОРОГО ЛАЙКНУЛИ
        try:
            # Получаем username лайкнувшего
            liker_username = message.from_user.username
            if liker_username:
                contact_display = f"@{liker_username}"
            else:
                contact_display = current_user['full_name']

            # Формируем текст уведомления
            notification_text = (
                f"🔔 <b>Новый лайк!</b>\n\n"
                f"👤 <b>{current_user[
                    'full_name'
                ]}</b> лайкнул(а) твою анкету!\n"
                f"💬 Напиши ему(ей): {contact_display}\n\n"
                f"📊 Посмотреть все лайки: «Кто лайкнул меня»"
            )

            # Отправляем уведомление
            keyboard = get_profile_keyboard(
                message.from_user.username,
                user_id=user_id
            )
            await bot.send_message(
                chat_id=current_anket['id'],
                text=notification_text,
                parse_mode='HTML',
                reply_markup=keyboard
            )

            logging.info(
                f"Уведомление о лайке отправлено пользователю {current_anket[
                    'id'
                ]}")

        except Exception as e:
            logging.error(f"Не удалось отправить уведомление о лайке: {e}")

        # Если лайк взаимный - отправляем специальное уведомление обоим
        if is_mutual and liked_user:
            # Подготавливаем контакты
            user1_contact = f"@{
                message.from_user.username
            }" if message.from_user.username else current_user[
                'full_name'
            ]
            user2_contact = f"@{
                current_anket.get('username')
            }" if current_anket.get(
                'username') else current_anket['full_name']

            # Уведомление текущему пользователю
            await message.answer(
                f"❤️ {current_anket['full_name']} тоже лайкнул(а) тебя!\n"
                f"👤 Контакт: {user2_contact}\n\n"
                f"💬 Напишите друг другу!"
            )

            # Уведомление второму пользователю
            try:
                await bot.send_message(
                    chat_id=current_anket['id'],
                    text=(
                        f"❤️ {current_user[
                            'full_name'
                        ]} тоже лайкнул(а) тебя!\n"
                        f"👤 Контакт: {user1_contact}\n\n"
                        f"💬 Напишите друг другу!"
                    ),
                    parse_mode='HTML'
                )
            except Exception as e:
                logging.error(
                    f"Не удалось отправить уведомление о взаимной симпатии: {
                        e
                    }"
                )

    elif message.text == "Дизлайк 👎":
        # Сохраняем дизлайк в БД
        db.dislike_user(user_id, current_anket['id'])

        await action_msg.edit_text(
            f"👎 Ты пропустил(а) {current_anket['full_name']}..."
        )

    # Очищаем текущую анкету из состояния
    await state.update_data(current_anket=None)

    # Переходим к следующей анкете
    await show_next_anket(user_id, state)


@router.message(UserState.viewing_ankets, F.text == "Прекратить просмотр 💤")
async def exit_search(message: Message, state: FSMContext):
    """Выход из режима просмотра"""
    await message.answer(
        "👋 Ты вышел из режима поиска. Возвращайся скорее!",
        reply_markup=main_kb
    )
    await state.clear()


@router.message(F.text == 'Смотреть анкеты 🔍')
async def start_search(message: Message, state: FSMContext):
    """Начинает просмотр анкет"""
    user_id = message.from_user.id

    # Проверяем, есть ли пользователь в БД
    if not db.check_user(user_id):
        await message.answer(
            "❌ Сначала нужно создать анкету!\n"
            "Используй /registr для регистрации",
            reply_markup=main_kb
        )
        return

    # Проверяем, есть ли анкеты для просмотра
    first_anket = db.get_next_profile(user_id)

    if not first_anket:
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
async def update_profile(message: Message):
    user_id = message.from_user.id

    if not db.check_user(user_id):
        await message.answer(
            "❌ У вас нет анкеты для обновления!\n\n"
            "Создайте анкету: /registr"
        )
        return

    await message.answer(
        "⚠️ <b>Вы точно хотите обновить свою анкету?</b>\n\n"
        "Это действие нельзя будет отменить!",
        reply_markup=get_update_anket_keyboard(),
        parse_mode='html'
    )


@router.message(F.text == "Мои симпатии")
async def show_mutual_likes(message: Message):
    """Показывает взаимные симпатии"""
    user_id = message.from_user.id

    mutual_likes = db.get_mutual_likes(user_id)

    if not mutual_likes:
        await message.answer(
            "😕 У тебя пока нет взаимных симпатий",
            reply_markup=main_kb
        )
        return

    text = "<b>Твои взаимные симпатии:</b>\n\n"
    for user in mutual_likes:
        text += f"👤 {user['full_name']}, {user['age']} лет\n"
        text += f"📱 @{user.get('username', 'не указан')}\n"
        text += f"🏙 {user['city']}\n\n"

    await message.answer(text, parse_mode='HTML')


@router.message(F.text == "Статистика 📊")
async def show_stats(message: Message):
    """Показывает статистику"""
    user_id = message.from_user.id

    # Получаем статистику из БД
    stats = db.get_user_stats(user_id)

    # Получаем общее количество анкет
    all_users = db.get_all_users()
    total_users = len(all_users)

    stats_text = f"""
📊 <b>Твоя статистика:</b>

Ты лайкнул(а): {stats.get('likes_given', 0)} человек
Тебя лайкнули: {stats.get('likes_received', 0)} человек
Взаимных лайков: {stats.get('mutual_likes', 0)}

👥 Всего анкет в базе: {total_users}
    """

    await message.answer(stats_text, parse_mode='HTML')


@router.message(F.text == "Мои лайки 👍")
async def show_my_likes(message: Message):
    """Показывает кого лайкнул пользователь"""
    user_id = message.from_user.id

    likes_given = db.get_likes_given(user_id)

    if not likes_given:
        await message.answer("Ты ещё никого не лайкнул(а)")
        return

    text = "👤 <b>Кого ты лайкнул(а):</b>\n\n"
    for user in likes_given:
        text += f"• {user['full_name']}, {user['age']} лет - @{user.get(
            'username',
            'нет'
        )}\n"

    await message.answer(text, parse_mode='HTML')


@router.message(F.text == "Кто лайкнул меня")
async def show_who_liked_me(message: Message):
    """Показывает кто лайкнул пользователя"""
    user_id = message.from_user.id

    likes_received = db.get_likes_received(user_id)

    if not likes_received:
        await message.answer("Тебя пока никто не лайкнул(а)")
        return

    text = "<b>Кто тебя лайкнул(а):</b>\n\n"
    for user in likes_received:
        text += f"• {user['full_name']}, {user['age']} лет - @{user.get(
            'username',
            ' у пользователя нет username')}\n"

    await message.answer(text, parse_mode='HTML')


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
        text = "Используй кнопки меню для навигации 👇"
        await message.answer(
            text,
            reply_markup=main_kb
        )
