import sqlite3
import time


conn = sqlite3.connect(database='test.db') # Подключаемся к файлу БД
cursor = conn.cursor() # Инициализиурем курсор

    
def create_table(): # Функция создания структурной таблицы
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


def create_user(id, full_name, age, photo, stack, city, registration_date, about_self, like): # Функция создания юзера в таблице
    cursor.execute("INSERT INTO users_ankets (id, full_name, age, photo, stack, city, registration_date, about_self, like) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, full_name, age, photo, stack, city, registration_date, about_self, like))
    conn.commit()


def read_user(id): # Функция получения всех данных юзера по его id
    data = cursor.execute("SELECT id, full_name, age, photo, stack, city, registration_date, about_self, like FROM users_ankets WHERE id=?", (id,)).fetchall()
    return data

def update_user(id, full_name:str, age:int, photo, stack:str, city:str, about_self:str): # Функция обновления некоторых параметров юзера
    cursor.execute("UPDATE users_ankets SET full_name=? WHERE id = ?", (full_name, id))
    cursor.execute("UPDATE users_ankets SET age=? WHERE id = ?", (age, id))
    cursor.execute("UPDATE users_ankets SET photo=? WHERE id = ?", (photo, id))
    cursor.execute("UPDATE users_ankets SET stack=? WHERE id = ?", (stack, id))
    cursor.execute("UPDATE users_ankets SET city=? WHERE id = ?", (city, id))
    cursor.execute("UPDATE users_ankets SET about_self=? WHERE id = ?", (about_self, id))
    conn.commit()


def delete_user(id): # Функция удаления юзера из таблицы
    cursor.execute("DELETE FROM users_ankets WHERE id=?", (id,))


def check_user(id): # Функция проверки наличия юзера в БД
    create_table()
    user = cursor.execute("SELECT id FROM users_ankets WHERE id=?", (id,)).fetchone()
    if user == None:
        return False
    else:
        return True
    

def create_pool_ankets(id: int) -> list: # Функция создания пула анкет пользователей
    data = cursor.execute("SELECT * FROM users_ankets").fetchall()
    user_anket = cursor.execute("SELECT id, full_name, age, photo, stack, city, registration_date, about_self, like FROM users_ankets WHERE id=?", (id,)).fetchall()[0]

    data.remove(user_anket)

    return data


def drop_table(): # Функция удаления всей таблицы(структуры)
    cursor.execute("DROP TABLE IF EXISTS users_ankets")
    conn.commit()




def test_create_users() -> None: # Тестовая функция создания 100 анкет
    for id in range(100):
        cursor.execute("INSERT INTO users_ankets (id, full_name, age, photo, stack, city, registration_date, about_self, like) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, "full_name", 18, "photo", "stack", "city", "registration_date", "about_self", None))
        conn.commit()
        time.sleep(1)
        print("+1 User")