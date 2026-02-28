import sqlite3
import time
from datetime import datetime, timedelta

from .constants import USER_FIELDS

conn = sqlite3.connect(database='test.db')  # Подключаемся к файлу БД
cursor = conn.cursor()  # Инициализиурем курсор
FIELDS_STRING = ', '.join(USER_FIELDS)
PLACEHOLDERS = ', '.join(['?'] * len(USER_FIELDS))


def create_table():  # Функция создания структурной таблицы
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_ankets (
                id INTEGER PRIMARY KEY,
                full_name TEXT,
                age INTEGER,
                photo TEXT,
                stack TEXT,
                city TEXT,
                registration_date TEXT,
                about_self TEXT,
                like TEXT)""")
    conn.commit()


# Функция создания юзера в таблице
def create_user(**kwargs):
    """Создание нового пользователя"""
    values = [kwargs.get(field) for field in USER_FIELDS]
    cursor.execute(
        f"INSERT INTO users_ankets ({FIELDS_STRING}) VALUES ({PLACEHOLDERS})",
        values
    )
    conn.commit()


def read_user(id):
    """Получение всех данных пользователя по его id"""
    data = cursor.execute(
        f"SELECT {FIELDS_STRING} FROM users_ankets WHERE id=?",
        (id,)
    ).fetchall()
    return data


def update_user(id, full_name: str, age: int,
                photo, stack: str, city: str,
                about_self: str):
    """Обновление данных пользователя"""
    update_fields = {
        'full_name': full_name,
        'age': age,
        'photo': photo,
        'stack': stack,
        'city': city,
        'about_self': about_self
    }

    for field, value in update_fields.items():
        if field in USER_FIELDS:  # Проверяем, что поле существует
            cursor.execute(
                f"UPDATE users_ankets SET {field}=? WHERE id=?",
                (value, id)
            )
    conn.commit()


def delete_user(id):
    """Удаление пользователя из таблицы"""
    cursor.execute("DELETE FROM users_ankets WHERE id=?", (id,))


def check_user(id):
    """Проверка наличия пользователя в БД"""
    create_table()
    user = cursor.execute(
        "SELECT id FROM users_ankets WHERE id=?", (id,)
    ).fetchone()
    return user is not None


def create_pool_ankets(id: int) -> list:
    """Создание пула анкет (все анкеты кроме указанной)"""
    all_users = cursor.execute(
        f"SELECT {FIELDS_STRING} FROM users_ankets").fetchall()
    current_user = cursor.execute(
        f"SELECT {FIELDS_STRING} FROM users_ankets WHERE id=?",
        (id,)
    ).fetchone()

    if current_user and current_user in all_users:
        all_users.remove(current_user)

    return all_users


def drop_table():
    """Удаление всей таблицы"""
    cursor.execute("DROP TABLE IF EXISTS users_ankets")
    conn.commit()


def test_create_users() -> None:
    """Тестовая функция создания 100 анкет"""
    start_time = time.time()

    # Опционально: очищаем таблицу перед тестом
    # drop_table()
    create_table()

    for user_id in range(100):
        user_data = (
            user_id,
            f"User_{user_id}",
            18 + (user_id % 50),
            f"photo_id_{user_id}",
            f"Stack_{user_id % 10}",
            f"City_{user_id % 20}",
            (
                datetime.now() - timedelta(days=user_id)).strftime(
                    "%Y-%m-%d %H:%M:%S"
            ),
            f"About_self_{user_id}",
            None
        )

        cursor.execute(
            f"INSERT INTO users_ankets ({FIELDS_STRING}) VALUES ({PLACEHOLDERS})",
            user_data)
        conn.commit()

        print(f"✓ Создана анкета #{user_id+1}: User_{user_id}")
        time.sleep(0.1)

    elapsed_time = time.time() - start_time
    print(f"\n Создано 100 анкет за {elapsed_time:.2f} секунд")
    print(f" Средняя скорость: {100/elapsed_time:.1f} анкет/сек")
