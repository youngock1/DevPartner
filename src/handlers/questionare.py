from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.states import Form_anket
from database import db

import datetime
import asyncio


router = Router()


@router.message(Command('registr'))
async def registration_command(message: Message, state: FSMContext):
    # ИСПРАВЛЕНО: test -> db
    if db.check_user(message.from_user.id):
        await message.answer(
            f"Ты уже зарегестрирован, {message.from_user.first_name}!"
        )
        print(db.read_user(message.from_user.id))
    else:
        await message.answer(
            "<b>Введите ваше имя и фамилию:</b>", parse_mode='html'
        )
        await state.set_state(Form_anket.full_name)


@router.message(Form_anket.full_name)
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(Form_anket.age)
    await message.answer("<b>Введите свой возраст:</b>", parse_mode='html')


@router.message(Form_anket.age)
async def get_age(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(age=message.text)
        await state.set_state(Form_anket.photo)
        await message.answer("<b>Теперь скинь фото:</b>", parse_mode='html')
    else:
        await message.answer(
            "<b>❌ Возраст должен быть числом.</b>\n\n"
            "<b>Пожалуйста, введите ваш возраст цифрами:</b>",
            parse_mode='html'
        )


@router.message(Form_anket.photo, F.photo)
async def get_photo(message: Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo=photo_file_id)
    await state.set_state(Form_anket.stack)
    await message.answer(
        "<b>Введите свой stack-разработки:</b>", parse_mode='html'
    )


@router.message(Form_anket.photo)
async def wrong_photo(message: Message, state: FSMContext):
    await message.answer(
        "<b>❌ Пожалуйста, отправьте фотографию,"
        " а не текст или другой файл!</b>\n\n",
        parse_mode='html'
    )


@router.message(Form_anket.stack)
async def get_stack(message: Message, state: FSMContext):
    await state.update_data(stack=message.text)
    await state.set_state(Form_anket.city)
    await message.answer(
        "<b>Теперь введите свой город:</b>", parse_mode='html'
    )


@router.message(Form_anket.city)
async def get_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(Form_anket.about_self)
    await message.answer("<b>Теперь расскажите о себе:</b>", parse_mode='html')


@router.message(Form_anket.about_self)
async def get_about_self(message: Message, state: FSMContext):
    # ИСПРАВЛЕНО: test -> db
    if db.check_user(message.from_user.id):
        await state.update_data(about_self=message.text)
        data = await state.get_data()
        await state.clear()
        # ИСПРАВЛЕНО: test -> db
        db.update_user(
            message.from_user.id,
            full_name=data["full_name"],
            age=data["age"],
            photo=str(data["photo"]),
            stack=data["stack"],
            city=data["city"],
            about_self=data["about_self"]
        )
        await asyncio.sleep(0.1)
        data = db.read_user(message.from_user.id)
        if data:
            await message.answer_photo(
                photo=data[0][3],
                caption=f'<b>ID:</b>    {int(data[0][0])}\n'
                f'<b>Name:</b>  {data[0][1]}\n'
                f'<b>Age:</b>   {data[0][2]} years\n\n'
                f'<b>Stack:</b> {data[0][4]}\n'
                f'<b>City:</b>  {data[0][5]}\n\n'
                f'<b>About:</b> {data[0][7]}\n\n'
                f'<b>Registration date:</b>\n{data[0][6]}UTC(+3)',
                parse_mode='html'
            )
    else:
        await state.update_data(about_self=message.text)
        data = await state.get_data()
        await state.clear()
        # ИСПРАВЛЕНО: test -> db
        db.create_user(
            id=message.from_user.id,
            full_name=data["full_name"],
            age=data["age"],
            photo=str(data["photo"]),
            stack=data["stack"],
            city=data["city"],
            registration_date=(
                datetime.datetime.now().strftime("%Y-%m-%d    %H:%M:%S")
            ),
            about_self=data["about_self"],
            like=None
        )
        await asyncio.sleep(0.1)
        data = db.read_user(message.from_user.id)
        if data:
            await message.answer_photo(
                photo=data[0][3],
                caption=f'<b>ID:</b>    {int(data[0][0])}\n'
                f'<b>Name:</b>  {data[0][1]}\n'
                f'<b>Age:</b>   {data[0][2]} years\n\n'
                f'<b>Stack:</b> {data[0][4]}\n'
                f'<b>City:</b>  {data[0][5]}\n\n'
                f'<b>About:</b> {data[0][7]}\n\n'
                f'<b>Registration date:</b>\n{data[0][6]}UTC(+3)',
                parse_mode='html'
            )
