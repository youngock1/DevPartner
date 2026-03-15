"""----------IMPORT MODULES----------"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import crud

from keyboards.reply import rm_kb

from utils.states import Form_anket
from aiogram.fsm.context import FSMContext
import logging


# Инициализация роутера
router = Router()

# Initilization DB
db = crud.DatabaseManager()



# Handler callback data = "confirm_delete"
@router.callback_query(F.data == "confirm_delete")
async def confirm_delete(callback: CallbackQuery):
    """Подтверждение удаления анкеты"""

    # Удаляем анкету
    db.delete_user(callback.from_user.id)

    await callback.message.edit_text(
        "✅ <b>Ваша анкета успешно удалена!</b>\n\n"
        "Если захотите вернуться, создайте новую анкету:\n"
        "/registr",
        parse_mode='html')

    await callback.answer("Анкета удалена")



# Handler callback data = "cancel_delete"
@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery):
    """Отмена удаления анкеты"""

    await callback.message.edit_text(
        "✅ <b>Удаление отменено!</b>\n\n"
        "Ваша анкета сохранена.",
        parse_mode='html'
    )

    await callback.answer("Удаление отменено")



# Handler callback data = "confirm_update"
@router.callback_query(F.data == 'confirm_update')
async def confirm_update(callback: CallbackQuery, state: FSMContext):
    """Подтверждение обновления анкеты"""

    await callback.message.edit_text(
        "✅ <b>Начинаем обновление:</b>\n\n"
        "<b>Введите имя фамилию:</b>",
        parse_mode='html')
    await callback.answer("✅ Начинаем обновление")
    await state.set_state(Form_anket.full_name)



# Handler callback data = "cancel_update"
@router.callback_query(F.data == 'cancel_update')
async def cancel_update(callback: CallbackQuery):
    """Отмена обновления анкеты"""
    await callback.message.edit_text(
        "✅ <b>Обновление отменено!</b>\n\n",
        parse_mode='html'
    )
    await callback.answer("✅ Обновление отменено!\n\n")



# Handler callback data = "view_profile"
@router.callback_query(F.data.startswith("view_profile:"))
async def view_profile_callback(callback: CallbackQuery):
    """Показывает анкету пользователя"""
    try:
        # Получаем ID из callback data
        user_id = int(callback.data.split(":")[1])

        # Получаем данные пользователя
        user = db.read_user(user_id)

        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        # Форматируем текст анкеты
        profile_text = (
            f"👤 <b>{user.get('full_name', 'Не указано')}</b>\n"
            f"  • Возраст: {user.get('age', '?')}\n"
            f"  • Город: {user.get('city', 'Не указан')}\n"
            f"  • Стек: {user.get('stack', 'Не указан')}\n"
            f"📝 О себе: {user.get('about_self', 'Не указано')}"
        )

        # Отправляем фото, если есть
        if user.get('photo'):
            await callback.message.answer_photo(
                photo=user['photo'],
                caption=profile_text,
                parse_mode='HTML'
            )
        else:
            await callback.message.answer(
                profile_text,
                parse_mode='HTML'
            )

        await callback.answer()

    except Exception as e:
        logging.error(f"Ошибка в view_profile_callback: {e}")
        await callback.answer("Ошибка загрузки анкеты", show_alert=True)
