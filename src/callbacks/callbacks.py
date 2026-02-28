from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import db

from utils.states import Form_anket
from aiogram.fsm.context import FSMContext

router = Router() # Инициализация роутера


@router.callback_query(F.data == "confirm_delete")
async def confirm_delete(callback: CallbackQuery):
    """Подтверждение удаления анкеты"""

    # Удаляем анкету
    db.delete_user(callback.from_user.id)

    await callback.message.edit_text(
        "✅ <b>Ваша анкета успешно удалена!</b>\n\n"
        "Если захотите вернуться, создайте новую анкету:\n"
        "/registr",
        parse_mode='html'
    )

    await callback.answer("Анкета удалена")


@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery):
    """Отмена удаления анкеты"""

    await callback.message.edit_text(
        "✅ <b>Удаление отменено!</b>\n\n"
        "Ваша анкета сохранена.",
        parse_mode='html'
    )

    await callback.answer("Удаление отменено")


@router.callback_query(F.data == 'confirm_update')
async def confirm_update(callback: CallbackQuery, state: FSMContext):
	"""Подтверждение обновления анкеты"""

	await callback.message.edit_text(
			"✅ <b>Начинаем обновление:</b>\n\n"
            "<b>Введите имя фамилию:</b>",
            parse_mode='html')
	await callback.answer("✅ Начинаем обновление")
	await state.set_state(Form_anket.full_name)


@router.callback_query(F.data == 'cancel_update')
async def cancel_update(callback: CallbackQuery):
	"""Отмена обновления анкеты"""
	await callback.message.edit_text(
	 		"✅ <b>Обновление отменено!</b>\n\n",
	 		parse_mode='html'
	 	)
	await callback.answer("✅ Обновление отменено!\n\n")