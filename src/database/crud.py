from sqlalchemy import func
from typing import List, Tuple, Optional, Dict
import time
from functools import lru_cache

from . import constants
from .models import User, Like, Dislike, init_db, get_session


class DatabaseManager:
    def __init__(self, db_path=constants.SQLALCHEMY_DATABASE_URI):
        self.engine = init_db(db_path)  # Инициализация "движка"
        self.session = get_session(self.engine)

    def __enter__(self):  # Стандартный
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def create_user(self, **kwargs) -> User:
        """Create a new user"""
        user = User(**kwargs)
        self.session.add(user)
        self.session.commit()
        return user

    def read_user(self, user_id: int) -> Optional[Dict]:
        """Получение данных пользователя по его id"""
        user = self.session.query(User).filter(User.id == user_id).first()
        return user.to_dict() if user else None

    def update_user(self, id: int, **kwargs) -> Optional[User]:
        """Update user data"""
        user = self.session.query(User).filter(User.id == id).first()
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)
            self.session.commit()
        return user

    def delete_user(self, id: int) -> bool:
        """Delete user by id"""
        user = self.session.query(User).filter(User.id == id).first()
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False

    def check_user(self, id: int) -> bool:
        """Есть пользователб в БД"""
        return self.session.query(
            User
        ).filter(User.id == id).first() is not None

    def get_next_profile(self, current_user_id: int) -> Optional[Dict]:
        viewed_users = self.session.query(Like.liked_user_id).filter(
            Like.user_id == current_user_id
        ).union(
            self.session.query(Dislike.disliked_user_id).filter(
                Dislike.user_id == current_user_id
            )
        ).all()

        viewed_ids = [user[0] for user in viewed_users]
        viewed_ids.append(current_user_id)

        user = self.session.query(User).filter(
            ~User.id.in_(viewed_ids)
        ).order_by(func.random()).first()

        return user.to_dict() if user else None

    def like_user(self, user_id: int, liked_user_id: int) -> Tuple[
        bool, Optional[Dict], Optional[Dict]
    ]:
        """
        Лайкнуть пользователя
        Возвращает (is_mutual, liked_user_data, current_user_data)
        """

        # Проверяем есть ли встречный лайк
        mutual_like = self.session.query(Like).filter(
            Like.user_id == liked_user_id,
            Like.liked_user_id == user_id
        ).first()

        is_mutual = mutual_like is not None

        # Добавляем лайк
        like = Like(
            user_id=user_id,
            liked_user_id=liked_user_id,
            is_mutual=1 if is_mutual else 0
        )
        self.session.add(like)

        # Если есть встречный лайк, обновляем его статус
        if is_mutual:
            mutual_like.is_mutual = 1

        self.session.commit()

        liked_user = self.read_user(liked_user_id)
        current_user = self.read_user(user_id)

        return is_mutual, liked_user, current_user

    def dislike_user(self, user_id: int, disliked_user_id: int) -> Dislike:
        """Дизлайкнуть пользователя"""
        dislike = Dislike(
            user_id=user_id,
            disliked_user_id=disliked_user_id
        )
        self.session.add(dislike)
        self.session.commit()
        return dislike

    def get_mutual_likes(self, user_id: int) -> List[Dict]:
        """Получение всех взаимных лайков пользователя"""

        users = self.session.query(User).join(
            Like, User.id == Like.user_id
        ).filter(
            Like.liked_user_id == user_id,
            Like.is_mutual == 1
        ).all()

        return [user.to_dict() for user in users]

    def has_user_liked(self, user_id: int, target_user_id: int) -> bool:
        """Проверка, лайкал ли пользователь target"""

        return self.session.query(Like).filter(
            Like.user_id == user_id,
            Like.liked_user_id == target_user_id
        ).first() is not None

    def get_likes_received(self, user_id: int) -> List[Dict]:
        """Получение всех пользователей, которые лайкнули данного"""

        users = self.session.query(User).join(
            Like, User.id == Like.user_id
        ).filter(
            Like.liked_user_id == user_id
        ).all()

        return [user.to_dict() for user in users]

    def get_likes_given(self, user_id: int) -> List[Dict]:
        """Получение всех пользователей, которых лайкнул данный"""

        users = self.session.query(User).join(
            Like, User.id == Like.liked_user_id
        ).filter(
            Like.user_id == user_id
        ).all()

        return [user.to_dict() for user in users]

    def is_profile_viewed(self, user_id: int, profile_id: int) -> bool:
        """Проверяет, просматривал ли пользователь эту анкету"""

        like_viewed = self.session.query(Like).filter(
            Like.user_id == user_id,
            Like.liked_user_id == profile_id
        ).first()

        dislike_viewed = self.session.query(Dislike).filter(
            Dislike.user_id == user_id,
            Dislike.disliked_user_id == profile_id
        ).first()

        return like_viewed is not None or dislike_viewed is not None

    def drop_table(self, table_name: str = None):
        """Удаление таблицы (по умолчанию всех)"""

        if table_name == 'users_ankets':
            User.__table__.drop(self.engine)
        elif table_name == 'likes':
            Like.__table__.drop(self.engine)
        elif table_name == 'dislikes':
            Dislike.__table__.drop(self.engine)
        else:
            # Drop all tables
            User.__table__.drop(self.engine, checkfirst=True)
            Like.__table__.drop(self.engine, checkfirst=True)
            Dislike.__table__.drop(self.engine, checkfirst=True)

    def get_all_users(self) -> List[Dict]:
        """Получение всех пользователей"""

        users = self.session.query(User).all()
        return [user.to_dict() for user in users]

    def get_stats(self) -> Dict:
        """Получение статистики по БД"""

        stats = {}

        # Количество пользователей
        stats['total_users'] = self.session.query(func.count(User.id)).scalar()

        # Количество лайков
        stats['total_likes'] = self.session.query(func.count(Like.id)).scalar()

        # Количество взаимных лайков
        stats['mutual_likes'] = self.session.query(func.count(Like.id)).filter(
            Like.is_mutual == 1
        ).scalar()

        # Количество дизлайков
        stats['total_dislikes'] = self.session.query(
            func.count(Dislike.id)).scalar()

        return stats

    @lru_cache(maxsize=128)
    def get_user_stats(self, user_id: int) -> Dict:
        """Получение статистики по конкретному пользователю"""

        stats = {}

        # Количество лайков, которые поставил пользователь
        stats['likes_given'] = self.session.query(func.count(Like.id)).filter(
            Like.user_id == user_id
        ).scalar()

        # Количество полученных лайков
        stats[
            'likes_received'
        ] = self.session.query(func.count(Like.id)).filter(
            Like.liked_user_id == user_id
        ).scalar()

        # Количество взаимных лайков
        stats['mutual_likes'] = self.session.query(func.count(Like.id)).filter(
            Like.liked_user_id == user_id,
            Like.is_mutual == 1
        ).scalar()

        return stats

    def create_pool_ankets(self, user_id: int) -> List[Dict]:
        """Создание пула анкет (все анкеты кроме указанной)"""

        users = self.session.query(User).filter(User.id != user_id).all()
        return [user.to_dict() for user in users]


def test_create_users(db_manager: DatabaseManager, count: int = 100) -> None:
    """Тестовая функция создания 100 анкет"""

    start_time = time.time()

    for i in range(count):
        user_data = {
            'id': i,
            'full_name': f"User_{i}",
            'age': 18 + (i % 50),
            'photo': f"photo_id_{i}",
            'stack': f"Stack_{i % 10}",
            'city': f"City_{i % 20}",
            'about_self': f"About_self_{i}"
        }

        db_manager.create_user(**user_data)
        print(f"✓ Created anketa #{i+1}: User_{i}")
        time.sleep(0.1)

    elapsed_time = time.time() - start_time
    print(f"\n Created {count} ankets in {elapsed_time:.2f} seconds")
    print(f" Average speed: {count/elapsed_time:.1f} ankets/sec")
