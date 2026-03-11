import sqlite3
import time
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

from .constants import (USER_FIELDS,
                        LIKE_FIELDS,
                        DISLIKE_FIELDS)


FIELDS_STRING = ', '.join(USER_FIELDS)
PLACEHOLDERS = ', '.join(['?'] * len(USER_FIELDS))
DISLIKE_FIELDS_STRING = ', '.join(DISLIKE_FIELDS)
DISLIKE_PLACEHOLDERS = ', '.join(['?'] * len(DISLIKE_FIELDS))
LIKE_FIELDS_STRING = ', '.join(LIKE_FIELDS)
LIKE_PLACEHOLDERS = ', '.join(['?'] * len(LIKE_FIELDS))

conn = sqlite3.connect(database='test.db', check_same_thread=False)
conn.row_factory = sqlite3.Row  # Для доступа по именам полей
cursor = conn.cursor()


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
    # Таблица лайков
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            liked_user_id INTEGER,
            created_at TEXT,
            is_mutual INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users_ankets(id),
            FOREIGN KEY (liked_user_id) REFERENCES users_ankets(id),
            UNIQUE(user_id, liked_user_id)
        )
    """)

    # Таблица дизлайков
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dislikes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            disliked_user_id INTEGER,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users_ankets(id),
            FOREIGN KEY (disliked_user_id) REFERENCES users_ankets(id),
            UNIQUE(user_id, disliked_user_id)
        )
    """)
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


def read_user(user_id: int) -> Optional[dict]:
    """Получение данных пользователя по его id"""
    cursor.execute(
        f"SELECT {FIELDS_STRING} FROM users_ankets WHERE id=?",
        (user_id,)
    )
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None


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
        if field in USER_FIELDS:
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


def get_next_profile(current_user_id: int) -> Optional[dict]:
    """
    Получение следующей анкеты для просмотра
    Исключает: самого пользователя, уже лайкнутых, уже дизлайкнутых
    """
    # Получаем ID уже просмотренных пользователей (лайки и дизлайки)
    cursor.execute("""
        SELECT liked_user_id FROM likes WHERE user_id=?
        UNION
        SELECT disliked_user_id FROM dislikes WHERE user_id=?
    """, (current_user_id, current_user_id))

    viewed_users = [row[0] for row in cursor.fetchall()]

    # Добавляем текущего пользователя в исключения
    excluded_users = [current_user_id] + viewed_users

    # Если нет исключений, используем другой подход
    if not excluded_users:
        cursor.execute(f"""
            SELECT {FIELDS_STRING} FROM users_ankets
            WHERE id != ?
            ORDER BY RANDOM()
            LIMIT 1
        """, (current_user_id,))
    else:
        placeholders = ','.join(['?'] * len(excluded_users))

        cursor.execute(f"""
            SELECT {FIELDS_STRING} FROM users_ankets
            WHERE id NOT IN ({placeholders})
            ORDER BY RANDOM()
            LIMIT 1
        """, excluded_users)

    row = cursor.fetchone()
    return dict(row) if row else None


def like_user(
        user_id: int, liked_user_id: int
) -> Tuple[bool, Optional[dict], Optional[dict]]:
    """
    Лайкнуть пользователя
    Возвращает (is_mutual, liked_user_data, current_user_data)
    """
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Проверяем, есть ли встречный лайк
    cursor.execute("""
        SELECT * FROM likes
        WHERE user_id=? AND liked_user_id=?
    """, (liked_user_id, user_id))

    mutual_like = cursor.fetchone()
    is_mutual = mutual_like is not None

    # Добавляем лайк
    cursor.execute(f"""
        INSERT OR IGNORE INTO likes ({LIKE_FIELDS_STRING})
        VALUES ({LIKE_PLACEHOLDERS})
    """, (user_id, liked_user_id, created_at, 1 if is_mutual else 0))

    # Если есть встречный лайк, обновляем его статус
    if is_mutual:
        cursor.execute("""
            UPDATE likes SET is_mutual=1
            WHERE user_id=? AND liked_user_id=?
        """, (liked_user_id, user_id))

    conn.commit()

    # Получаем данные обоих пользователей
    liked_user = read_user(liked_user_id)
    current_user = read_user(user_id)

    return is_mutual, liked_user, current_user


def dislike_user(user_id: int, disliked_user_id: int):
    """Дизлайкнуть пользователя"""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(f"""
        INSERT OR IGNORE INTO dislikes ({DISLIKE_FIELDS_STRING})
        VALUES ({DISLIKE_PLACEHOLDERS})
    """, (user_id, disliked_user_id, created_at))

    conn.commit()


def get_mutual_likes(user_id: int) -> List[dict]:
    """Получение всех взаимных лайков пользователя"""
    cursor.execute("""
        SELECT u.* FROM users_ankets u
        JOIN likes l ON u.id = l.user_id
        WHERE l.liked_user_id = ? AND l.is_mutual = 1
    """, (user_id,))

    return [dict(row) for row in cursor.fetchall()]


def has_user_liked(user_id: int, target_user_id: int) -> bool:
    """Проверка, лайкал ли пользователь target"""
    cursor.execute("""
        SELECT * FROM likes WHERE user_id=? AND liked_user_id=?
    """, (user_id, target_user_id))

    return cursor.fetchone() is not None


def get_likes_received(user_id: int) -> List[dict]:
    """Получение всех пользователей, которые лайкнули данного"""
    cursor.execute("""
        SELECT u.* FROM users_ankets u
        JOIN likes l ON u.id = l.user_id
        WHERE l.liked_user_id = ?
    """, (user_id,))

    return [dict(row) for row in cursor.fetchall()]


def get_likes_given(user_id: int) -> List[dict]:
    """Получение всех пользователей, которых лайкнул данный"""
    cursor.execute("""
        SELECT u.* FROM users_ankets u
        JOIN likes l ON u.id = l.liked_user_id
        WHERE l.user_id = ?
    """, (user_id,))

    return [dict(row) for row in cursor.fetchall()]


def is_profile_viewed(user_id: int, profile_id: int) -> bool:
    """Проверяет, просматривал ли пользователь эту анкету"""
    cursor.execute("""
        SELECT 1 FROM likes WHERE user_id=? AND liked_user_id=?
        UNION
        SELECT 1 FROM dislikes WHERE user_id=? AND disliked_user_id=?
    """, (user_id, profile_id, user_id, profile_id))

    return cursor.fetchone() is not None


def drop_table(table_name: str = None):
    """Удаление таблицы (по умолчанию всех)"""
    if table_name:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    else:
        cursor.execute("DROP TABLE IF EXISTS users_ankets")
        cursor.execute("DROP TABLE IF EXISTS likes")
        cursor.execute("DROP TABLE IF EXISTS dislikes")
    conn.commit()


def get_all_users() -> List[dict]:
    """Получение всех пользователей"""
    cursor.execute(f"SELECT {FIELDS_STRING} FROM users_ankets")
    return [dict(row) for row in cursor.fetchall()]


def get_stats() -> dict:
    """Получение статистики по БД"""
    stats = {}

    # Количество пользователей
    cursor.execute("SELECT COUNT(*) FROM users_ankets")
    stats['total_users'] = cursor.fetchone()[0]

    # Количество лайков
    cursor.execute("SELECT COUNT(*) FROM likes")
    stats['total_likes'] = cursor.fetchone()[0]

    # Количество взаимных лайков
    cursor.execute("SELECT COUNT(*) FROM likes WHERE is_mutual=1")
    stats['mutual_likes'] = cursor.fetchone()[0]

    # Количество дизлайков
    cursor.execute("SELECT COUNT(*) FROM dislikes")
    stats['total_dislikes'] = cursor.fetchone()[0]

    return stats


def get_user_stats(user_id: int) -> dict:
    """Получение статистики по конкретному пользователю"""
    stats = {}

    # Количество лайков, которые поставил пользователь
    cursor.execute("SELECT COUNT(*) FROM likes WHERE user_id=?", (user_id,))
    stats['likes_given'] = cursor.fetchone()[0]

    # Количество полученных лайков
    cursor.execute(
        "SELECT COUNT(*) FROM likes WHERE liked_user_id=?", (user_id,))
    stats['likes_received'] = cursor.fetchone()[0]

    # Количество взаимных лайков
    cursor.execute("""
        SELECT COUNT(*) FROM likes
        WHERE liked_user_id=? AND is_mutual=1
    """, (user_id,))
    stats['mutual_likes'] = cursor.fetchone()[0]

    return stats


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
            (f"INSERT INTO users_ankets ({FIELDS_STRING}) "
             f"VALUES ({PLACEHOLDERS})"),
            user_data
        )
        conn.commit()

        print(f"✓ Создана анкета #{user_id+1}: User_{user_id}")
        time.sleep(0.1)

    elapsed_time = time.time() - start_time
    print(f"\n Создано 100 анкет за {elapsed_time:.2f} секунд")
    print(f" Средняя скорость: {100/elapsed_time:.1f} анкет/сек")
