from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.states import Form_anket
from database import test

import datetime


router = Router()

@router.message(Command('registr'))
async def registration_command(message: Message, state: FSMContext):
    if test.check_user(message.from_user.id):
        await message.answer(f"Ты уже зарегестрирован, {message.from_user.first_name}!")
        print(test.read_user(message.from_user.id))
    else:
        await message.answer("Введите ваше имя и фамилию:")
        await state.set_state(Form_anket.full_name)


@router.message(Form_anket.full_name)
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(Form_anket.age)
    await message.answer("Введите свой возраст:")


@router.message(Form_anket.age)
async def get_age(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(age=message.text)
        await state.set_state(Form_anket.photo)
        await message.answer("Теперь скинь фото:")
    else:
        await message.answer("Введите свой возраст:")


@router.message(Form_anket.photo, F.photo)
async def get_photo(message: Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo=photo_file_id)
    await state.set_state(Form_anket.stack)
    await message.answer("Введите свой stack-разработки:")


@router.message(Form_anket.stack)
async def get_stack(message: Message, state: FSMContext):
    await state.update_data(stack=message.text)
    await state.set_state(Form_anket.city)
    await message.answer("Теперь введите свой город:")


@router.message(Form_anket.city)
async def get_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(Form_anket.about_self)
    await message.answer("Теперь расскажите о себе:")


@router.message(Form_anket.about_self)
async def get_about_self(message: Message, state: FSMContext):
    await state.update_data(about_self=message.text)
    data = await state.get_data()
    await state.clear()
    test.create_user(id=message.from_user.id, full_name=data["full_name"], age=data["age"], photo=str(data["photo"]), stack=data["stack"], city=data["city"],
                              registration_date=datetime.datetime.now().strftime("%Y-%m-%d    %H:%M:%S"), about_self=data["about_self"], like=None)
