USER_FIELDS = ('id', 'full_name', 'age', 'photo', 'stack',
               'city', 'registration_date', 'about_self', 'like')

LIKE_FIELDS = ['user_id', 'liked_user_id', 'created_at', 'is_mutual']
DISLIKE_FIELDS = ['user_id', 'disliked_user_id', 'created_at']

GREETING_PART_OF_MESSAGE = "<b>Добро пожаловать в бота, {full_name}!</b>\n\n"

DEFAULT_MESSAGE = (
    "Этот бот для людей, которые хотят создать свои IT-startups и проекты. "
    "С помощью этого бота ты сможешь найти себе товарища для кодинга, "
    "с которым сможешь разработать pet-project или startup, "
    "который в будущем станет популярным 👨‍💻\n\n"
)
