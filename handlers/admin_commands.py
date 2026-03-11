import asyncio
from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import db, constants
import io
import csv
from datetime import datetime

from database.models import Base, init_db
from .decorators import admin_only

router = Router()


class BroadcastStates(StatesGroup):
    waiting_for_text = State()


class ClearDBStates(StatesGroup):
    waiting_for_confirmation = State()


@router.message(F.text == "/admin")
@admin_only
async def admin_panel(message: Message):
    text = """
🔐 <b>Админ панель</b>

Доступные команды:
/stats - статистика бота
/users - список пользователей
/broadcast - рассылка
/export - экспорт данных
/clear_db - очистить БД
"""
    await message.answer(text, parse_mode='HTML')


@router.message(F.text == "/stats")
@admin_only
async def admin_stats(message: Message):
    stats = db.get_stats()
    text = f"""
📊 <b>Статистика бота:</b>

👥 Всего пользователей: {stats['total_users']}
❤️ Всего лайков: {stats['total_likes']}
💕 Взаимных лайков: {stats['mutual_likes']}
👎 Всего дизлайков: {stats['total_dislikes']}
"""
    await message.answer(text, parse_mode='HTML')


@router.message(F.text == "/users")
@admin_only
async def list_users(message: Message):
    users = db.get_all_users()
    text = "👥 <b>Список пользователей:</b>\n\n"
    for user in users[:10]:  # Первые 10
        text += f"• ID: {user['id']} | {user['full_name']} | {user[
            'age'
        ]} лет\n"
    text += f"\nВсего: {len(users)} пользователей"
    await message.answer(text, parse_mode='HTML')


@router.message(F.text == "/broadcast")
@admin_only
async def broadcast_start(message: Message, state: FSMContext):
    await message.answer(
        "📢 Введите текст для рассылки:\n"
        "(или отправьте /cancel для отмены)"
    )
    # 👈 Используем класс
    await state.set_state(BroadcastStates.waiting_for_text)


@router.message(BroadcastStates.waiting_for_text)
@admin_only
async def broadcast_send(message: Message, state: FSMContext):
    # Проверка на отмену
    if message.text == "/cancel":
        await message.answer("❌ Рассылка отменена")
        await state.clear()
        return

    text = message.text
    users = db.get_all_users()

    if not users:
        await message.answer("📭 Нет пользователей для рассылки")
        await state.clear()
        return

    # Отправляем статусное сообщение
    status_msg = await message.answer(
        f"⏳ Начинаю рассылку {len(users)} пользователям...\n"
        f"0/{len(users)}"
    )

    success = 0
    failed = 0

    for i, user in enumerate(users, 1):
        try:
            await message.bot.send_message(
                chat_id=user['id'],
                text=f"📢 <b>Рассылка от администрации:</b>\n\n{text}",
                parse_mode='HTML'
            )
            success += 1
        except Exception as e:
            failed += 1
            print(f"Ошибка отправки пользователю {user['id']}: {e}")

        # Обновляем статус каждые 10 сообщений
        if i % 10 == 0 or i == len(users):
            await status_msg.edit_text(
                f"⏳ Рассылка... {i}/{len(users)}\n"
                f"✓ Успешно: {success}\n"
                f"✗ Ошибок: {failed}"
            )

        await asyncio.sleep(0.05)  # Anti-flood

    await status_msg.edit_text(
        f"✅ Рассылка завершена!\n"
        f"✓ Успешно: {success}\n"
        f"✗ Не удалось: {failed}\n"
        f"Всего: {len(users)}"
    )
    await state.clear()


@router.message(F.text == "/clear_db")
@admin_only
async def clear_db_start(message: Message, state: FSMContext):
    """
    Начинает процесс очистки базы данных с подтверждением
    """
    # Получаем текущую статистику
    stats = db.get_stats()

    # Отправляем предупреждение
    warning_text = f"""

📊 <b>Текущая статистика:</b>
• Пользователей: {stats['total_users']}
• Лайков: {stats['total_likes']}
• Дизлайков: {stats['total_dislikes']}
• Взаимных лайков: {stats['mutual_likes']}

<b>Для подтверждения отправьте:</b> <code>SECRET_KEY</code>
<b>Для отмены отправьте:</b> /cancel

⏱ У вас есть 30 секунд на подтверждение.
"""

    await message.answer(warning_text, parse_mode='HTML')

    # Устанавливаем состояние ожидания подтверждения
    await state.set_state(ClearDBStates.waiting_for_confirmation)

    # Запускаем таймер на 30 секунд
    await asyncio.sleep(30)

    # Проверяем, не подтвердил ли пользователь
    current_state = await state.get_state()
    if current_state == ClearDBStates.waiting_for_confirmation:
        await message.answer(
            "⏱ Время подтверждения истекло. Операция отменена."
        )
        await state.clear()


@router.message(ClearDBStates.waiting_for_confirmation)
@admin_only
async def clear_db_confirm(message: Message, state: FSMContext):
    """
    Обрабатывает подтверждение очистки БД
    """
    # Проверка на отмену
    if message.text == "/cancel":
        await message.answer("❌ Очистка БД отменена")
        await state.clear()
        return

    # Проверка подтверждения
    if message.text != constants.SECRET_KEY:
        await message.answer(
            "❌ Неверный код подтверждения. Операция отменена.\n",
            parse_mode='HTML'
        )
        await state.clear()
        return

    # Получаем статистику ДО очистки
    stats_before = db.get_stats()

    # Отправляем сообщение о начале очистки
    status_msg = await message.answer("⏳ Очистка базы данных...")

    try:
        # Очищаем все таблицы
        db.drop_table()  # Удаляем все таблицы
        engine = init_db(constants.SQLALCHEMY_DATABASE_URI)
        Base.metadata.create_all(engine)

        # Обновляем статус
        await status_msg.edit_text(
            f"✅ <b>База данных успешно очищена!</b>\n\n"
            f"📊 <b>Было удалено:</b>\n"
            f"• Пользователей: {stats_before['total_users']}\n"
            f"• Лайков: {stats_before['total_likes']}\n"
            f"• Дизлайков: {stats_before['total_dislikes']}\n"
            f"• Взаимных лайков: {stats_before['mutual_likes']}",
            parse_mode='HTML'
        )

        # Логируем действие
        print(f"⚠️ АДМИН: {message.from_user.id} очистил базу данных")

    except Exception as e:
        await status_msg.edit_text(
            f"❌ <b>Ошибка при очистке БД:</b>\n<code>{e}</code>",
            parse_mode='HTML'
        )

    finally:
        await state.clear()


@router.message(F.text == "/export")
@admin_only
async def export_data(message: Message):
    """
    Экспорт данных из БД
    """
    users = db.get_all_users()

    if not users:
        await message.answer("📭 Нет данных для экспорта")
        return

    # Создаем CSV в памяти
    output = io.StringIO()
    writer = csv.writer(output)

    # Заголовки
    writer.writerow(['ID', 'Имя', 'Возраст', 'Город',
                    'Стек', 'О себе', 'Дата регистрации'])

    # Данные
    for user in users:
        writer.writerow([
            user['id'],
            user['full_name'],
            user['age'],
            user.get('city', ''),
            user.get('stack', ''),
            user.get('about_self', '')[:100] +
            ('...' if user.get('about_self') else ''),
            user.get('registration_date', '')
        ])

    # Получаем статистику
    stats = db.get_stats()

    # Добавляем статистику в конец файла
    writer.writerow([])
    writer.writerow(['СТАТИСТИКА'])
    writer.writerow(['Всего пользователей', stats['total_users']])
    writer.writerow(['Всего лайков', stats['total_likes']])
    writer.writerow(['Всего дизлайков', stats['total_dislikes']])
    writer.writerow(['Взаимных лайков', stats['mutual_likes']])
    writer.writerow(
        ['Дата экспорта', datetime.now().strftime(constants.DATETIME_FORM)])

    csv_bytes = output.getvalue().encode('utf-8-sig')
    input_file = BufferedInputFile(
        file=csv_bytes,
        filename=f"users_export_{datetime.now().strftime(
            constants.DATETIME_FORM
        )}.csv"
    )

    # Отправляем файл
    await message.answer_document(
        document=input_file,
        caption=f"📊 Экспорт данных ({len(users)} пользователей)"
    )
