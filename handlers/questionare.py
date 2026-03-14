"""----------IMPORT MODULES----------"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.states import Form_anket
from database.crud import DatabaseManager

import datetime

from keyboards.inline import get_update_anket_keyboard
from keyboards.reply import main_kb


# Initialize 'Router'
router = Router()

# Initialize 'DatabaseManager'
db = DatabaseManager()


# Handler command 'registr'(registration anket in bot)
@router.message(Command('registr'))
async def registration_command(message: Message, state: FSMContext):
    if db.check_user(message.from_user.id):
        await message.answer(
            "⚠️ <b>Вы точно хотите обновить свою анкету?</b>\n\n"
            "Это действие нельзя будет отменить!",
            reply_markup=get_update_anket_keyboard(),
            parse_mode='html')
    else:
        await message.answer(
            "✅ <b>Начинаем регистрацию...</b>\n\n"
            "<b>Введите ваше имя и фамилию:</b>", parse_mode='html'
        )
        await state.set_state(Form_anket.full_name)


# Handler state get name user
@router.message(Form_anket.full_name)
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(Form_anket.age)
    await message.answer("<b>Я получил ваше имя</b> ✅\n\n"
                         "<b>Теперь введите свой возраст:</b>",
                         parse_mode='html')


# Handler state get age user
@router.message(Form_anket.age)
async def get_age(message: Message, state: FSMContext):
    if message.text and message.text.isdigit():
        await state.update_data(age=message.text)
        await state.set_state(Form_anket.photo)
        await message.answer("<b>Я получил ваш возраст</b> ✅\n\n"
                             "<b>Теперь отправьте фото профиля:</b>",
                             parse_mode='html')
    else:
        await message.answer(
            "<b>❌ Возраст должен быть числом.</b>\n\n"
            "<b>Пожалуйста, введите ваш возраст цифрами:</b>",
            parse_mode='html'
        )


# Handler state get photo user
@router.message(Form_anket.photo, F.photo)
async def get_photo(message: Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo=photo_file_id)
    await state.set_state(Form_anket.stack)
    await message.answer("<b>Я получил ваше фото профиля</b> ✅\n\n"
                         "<b>Теперь введите свой stack-разработки:</b>",
                         parse_mode='html'
                         )


# Handler state get else photo in this state
@router.message(Form_anket.photo)
async def wrong_photo(message: Message, state: FSMContext):
    await message.answer(
        "<b>❌ Пожалуйста, отправьте фотографию,"
        " а не текст или другой файл!</b>\n\n",
        parse_mode='html'
    )


# Handler state get stack user
@router.message(Form_anket.stack)
async def get_stack(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(stack=message.text)
        await state.set_state(Form_anket.city)
        await message.answer("<b>Я получил ваш stack-разработки</b> ✅\n\n"
                            "<b>Теперь введите свой город:</b>",
                            parse_mode='html'
                            )
    else:
        await message.answer(f"<b>❌ Введите пожалуйста свой stack(ЯП) или None.</b>",
                            parse_mode='html')


# Handler state get city user
@router.message(Form_anket.city)
async def get_city(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(city=message.text)
        await state.set_state(Form_anket.about_self)
        await message.answer("<b>Я получил ваш город</b> ✅\n\n"
                            "<b>Теперь расскажите о себе:</b>",
                            parse_mode='html')
    else:
        await message.answer(f"<b>❌ Введите пожалуйста свой город или None.</b>",
                            parse_mode='html')


# Function format data of user
def format_user_data(user_data):
    """Форматирует данные пользователя для отображения"""
    if not user_data:
        return None

    # Если user_data - это список кортежей/списков
    if isinstance(user_data, list) and len(user_data) > 0:
        user = user_data[0]
        if isinstance(user, (list, tuple)):
            return {
                'id': user[0],
                'full_name': user[1],
                'age': user[2],
                'photo': user[3],
                'stack': user[4],
                'city': user[5],
                'registration_date': user[6],
                'about_self': user[7]
            }
    # Если user_data - это словарь
    elif isinstance(user_data, dict):
        return user_data

    return None


# Handler state get about user
@router.message(Form_anket.about_self)
async def get_about_self(message: Message, state: FSMContext):
    about_self = message.text
    user_id = message.from_user.id
    username = message.from_user.username

    # Проверяем, существует ли пользователь
    if db.check_user(user_id):
        # Обновляем существующего пользователя
        await state.update_data(about_self=about_self)
        data = await state.get_data()
        await state.clear()

        db.update_user(
            user_id,
            full_name=data["full_name"],
            age=int(data["age"]),
            photo=str(data["photo"]),
            stack=data["stack"],
            city=data["city"],
            about_self=data["about_self"]
        )

        # Получаем обновленные данные
        user_data = db.read_user(user_id)
        formatted_data = format_user_data(user_data)

        if formatted_data:
            caption = (
                f"<b>ID:</b> {formatted_data['id']}\n"
                f"<b>Имя:</b> {formatted_data['full_name']}\n"
                f"<b>Возраст:</b> {formatted_data['age']} лет\n\n"
                f"<b>Стек:</b> {formatted_data['stack']}\n"
                f"<b>Город:</b> {formatted_data['city']}\n\n"
                f"<b>О себе:</b> {formatted_data['about_self']}\n\n"
                f"<b>Дата регистрации:</b>\n{formatted_data['registration_date']} UTC(+3)"
            )

            await message.answer_photo(
                photo=formatted_data['photo'],
                caption=caption,
                parse_mode='html',
                reply_markup=main_kb
            )
        else:
            await message.answer("✅ Анкета обновлена!")

    else:
        # Создаем нового пользователя
        await state.update_data(about_self=about_self)
        data = await state.get_data()
        await state.clear()

        db.create_user(
            id=user_id,
            full_name=data["full_name"],
            age=int(data["age"]),
            photo=str(data["photo"]),
            stack=data["stack"],
            city=data["city"],
            registration_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            about_self=data["about_self"]
        )

        # Получаем созданные данные
        user_data = db.read_user(user_id)
        formatted_data = format_user_data(user_data)

        if formatted_data:
            caption = (
                f"<b>ID:</b> {formatted_data['id']}\n"
                f"<b>Имя:</b> {formatted_data['full_name']}\n"
                f"<b>Возраст:</b> {formatted_data['age']} лет\n\n"
                f"<b>Стек:</b> {formatted_data['stack']}\n"
                f"<b>Город:</b> {formatted_data['city']}\n\n"
                f"<b>О себе:</b> {formatted_data['about_self']}\n\n"
                f"<b>Дата регистрации:</b>\n{formatted_data['registration_date']} UTC(+3)"
            )

            await message.answer_photo(
                photo=formatted_data['photo'],
                caption=caption,
                parse_mode='html',
                reply_markup=main_kb
            )
        else:
            await message.answer("✅ Анкета создана!")
