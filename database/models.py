"""----------IMPORT MODULES----------"""
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

from . import constants


# Initilization class='declarativa_base'
Base = declarative_base() 



# Initilization class table 'User' in bot
class User(Base):
    # Parametres
    __tablename__ = 'users_ankets'

    # Structure table
    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    photo = Column(String(255))
    stack = Column(Text)
    city = Column(String(100))
    registration_date = Column(
        String(20), default=lambda: datetime.now().strftime(
            constants.DATETIME_FORM)
        )
    about_self = Column(Text)
    like = Column(String(10), nullable=True)


    # Relationships
    likes_given = relationship(
        'Like',
        foreign_keys='Like.user_id',
        back_populates='user',
        cascade='all, delete-orphan'
    )
    likes_received = relationship(
        'Like',
        foreign_keys='Like.liked_user_id',
        back_populates='liked_user',
        cascade='all, delete-orphan'
    )
    dislikes_given = relationship(
        'Dislike',
        foreign_keys='Dislike.user_id',
        back_populates='user',
        cascade='all, delete-orphan'
    )
    dislikes_received = relationship(
        'Dislike',
        foreign_keys='Dislike.disliked_user_id',
        back_populates='disliked_user',
        cascade='all, delete-orphan'
    )


    def __repr__(self):
        return f"<User(id={self.id}, name={self.full_name}, age={self.age})>"


    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'age': self.age,
            'photo': self.photo,
            'stack': self.stack,
            'city': self.city,
            'registration_date': self.registration_date,
            'about_self': self.about_self,
            'like': self.like
        }



# Initilization class 'Like' in bot
class Like(Base):
    # Parametres
    __tablename__ = 'likes'
    __table_args__ = (
        UniqueConstraint('user_id', 'liked_user_id', name='unique_like'),
    )

    # Structure table
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(
        'users_ankets.id', ondelete='CASCADE'), nullable=False)
    liked_user_id = Column(Integer, ForeignKey(
        'users_ankets.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(
        String(20), default=lambda: datetime.now().strftime(
            constants.DATETIME_FORM
        ))
    is_mutual = Column(Integer, default=0)


    # Relationships
    user = relationship('User', foreign_keys=[
                        user_id], back_populates='likes_given')
    liked_user = relationship('User', foreign_keys=[
                              liked_user_id], back_populates='likes_received')


    def __repr__(self):
        return (f"<Like(id={self.id}, user={self.user_id} -> "
                f"{self.liked_user_id}, mutual={self.is_mutual})>")


    def to_dict(self):
        """Convert like object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'liked_user_id': self.liked_user_id,
            'created_at': self.created_at,
            'is_mutual': self.is_mutual
        }


# Initilization class 'Dislike' in bot
class Dislike(Base):
    __tablename__ = 'dislikes'
    __table_args__ = (
        UniqueConstraint('user_id', 'disliked_user_id', name='unique_dislike'),
    )

    # Structure table
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(
        'users_ankets.id', ondelete='CASCADE'), nullable=False)
    disliked_user_id = Column(Integer, ForeignKey(
        'users_ankets.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(
        String(20), default=lambda: datetime.now().strftime(
            constants.DATETIME_FORM
        ))


    # Relationships
    user = relationship('User', foreign_keys=[
                        user_id], back_populates='dislikes_given')
    disliked_user = relationship(
        'User',
        foreign_keys=[disliked_user_id],
        back_populates='dislikes_received'
    )


    def __repr__(self):
        return (f"<Dislike(id={self.id}, user={self.user_id} -> "
                f"{self.disliked_user_id})>")


    def to_dict(self):
        """Convert dislike object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'disliked_user_id': self.disliked_user_id,
            'created_at': self.created_at
        }


# Function initilize DB
def init_db(db_path=None):
    """Initialize database and create tables"""
    if db_path is None:
        db_path = 'sqlite:///users.db'  # Запасной вариант

    # Убедимся, что db_path - строка
    if not isinstance(db_path, str):
        db_path = 'sqlite:///users.db'

    engine = create_engine(db_path, echo=False, connect_args={
                           'check_same_thread': False})
    Base.metadata.create_all(engine)
    return engine


# Function creating session
def get_session(engine):
    """Create a new session"""
    Session = sessionmaker(bind=engine)
    return Session()
