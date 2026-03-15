from models.user import User

# controllers/user_controller.py

class UserController:
    """Контроллер для управления пользователями."""

    def __init__(self, db_manager):
        """
        Инициализация контроллера пользователей.

        Args:
            db_manager: Менеджер базы данных
        """
        self.db_manager = db_manager

    def add_user(self, username, email, role):
        """
        Добавление нового пользователя.

        Args:
            username (str): Имя пользователя
            email (str): Email пользователя
            role (str): Роль ('admin', 'manager', 'developer')

        Returns:
            int: ID созданного пользователя

        Raises:
            ValueError: Если данные не проходят валидацию
        """
        # Создание объекта пользователя (валидация произойдет в конструкторе User)
        user = User(username, email, role)

        # Сохранение в базу данных
        user_id = self.db_manager.add_user(user)

        return user_id

    def get_user(self, user_id):
        """
        Получение пользователя по ID.

        Args:
            user_id (int): ID пользователя

        Returns:
            User: Объект пользователя или None, если пользователь не найден
        """
        return self.db_manager.get_user_by_id(user_id)

    def get_all_users(self):
        """
        Получение всех пользователей.

        Returns:
            list: Список всех пользователей
        """
        return self.db_manager.get_all_users()

    def update_user(self, user_id, **kwargs):
        """
        Обновление пользователя.

        Args:
            user_id (int): ID пользователя
            **kwargs: Поля для обновления (username, email, role)

        Returns:
            bool: True если пользователь обновлен, False если пользователь не найден

        Raises:
            ValueError: Если данные не проходят валидацию
        """
        # Получаем текущего пользователя
        user = self.get_user(user_id)
        if not user:
            return False

        # Используем метод update_info модели для валидации
        user.update_info(**kwargs)

        # Обновление в базе данных
        return self.db_manager.update_user(user_id, **kwargs)

    def delete_user(self, user_id):
        """
        Удаление пользователя.

        Args:
            user_id (int): ID пользователя

        Returns:
            bool: True если пользователь удален, False если пользователь не найден
        """
        return self.db_manager.delete_user(user_id)

    def get_user_tasks(self, user_id):
        """
        Получение всех задач пользователя.

        Args:
            user_id (int): ID пользователя

        Returns:
            list: Список задач пользователя

        Raises:
            ValueError: Если пользователь не найден
        """
        # Проверяем существование пользователя
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"Пользователь с ID {user_id} не найден")

        return self.db_manager.get_tasks_by_user(user_id)
