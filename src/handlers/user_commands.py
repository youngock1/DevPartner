from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards import reply
from aiogram.types import Message
from aiogram import Router, F
from database import test
import datetime

router = Router()  # Инициализация роутера

class Form_anket(StatesGroup):
    full_name = State()
    age = State()
    photo = State()
    stack = State()
    city = State()
    about_self = State()


@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(f"Добро пожаловать в бота, {message.from_user.full_name}!", reply_markup=reply.main_kb)


@router.message(Command('help'))
async def help_command(message: Message):
    await message.answer(f"<b>Руководство бота:</b>\n\n"
                         f"<b>/start</b> - перезапустить бота.\n"
                         f"<b>/help</b> - команда справки.\n"
                         f"<b>/registr</b> - команда регистрации анкеты.\n\n"
                         f"Этот бот для поиска товарищей по коду, здесь ты сможешь найти их для общения, создания пет-проектов, а может быть даже и своего startup`a", 
                         parse_mode='html')
    

@router.message(Command("profile"))
async def profile_command(message: Message):
    data = test.read_user(message.from_user.id)
    if data:
        await message.answer_photo(photo=data[0][3], caption=f'ID:    {data[0][0]}\n'
                                                          f'Name:  {data[0][1]}\n'
                                                          f'Age:   {data[0][2]}\n'
                                                          f'Stack: {data[0][4]}\n'
                                                          f'City:  {data[0][5]}\n'
                                                          f'About: {data[0][7]}\n'
                                                          f'Registartion date:\n{data[0][6]}'
                                   )
    else:
        await message.answer("Для отображения профиля, необходимо пройти регистрацию в боте.\n/registr")


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
