from datetime import datetime
import re

'''
class User:
    def __init__(self, username, email, role) -> None:
        pass

    def _is_valid_email(self, email) -> bool:
        pass

    def update_info(self, username=None, email=None, role=None) -> None:
        pass

    def to_dict(self) -> dict:
        pass
'''

# models/user.py

class User:
    """Класс для представления пользователя в системе управления задачами."""

    def __init__(self, username, email, role) -> None:
        """
        Инициализация нового пользователя.

        Args:
            username (str): Имя пользователя
            email (str): Email пользователя
            role (str): Роль пользователя ('admin', 'manager', 'developer')

        Raises:
            ValueError: Если имя пользователя пустое, email некорректный или роль недопустима
        """
        # Валидация: имя пользователя не может быть пустым
        if not username or not str(username).strip():
            raise ValueError("Имя пользователя не может быть пустым")

        # Валидация: проверка формата email
        if not self._is_valid_email(email):
            raise ValueError("Некорректный формат email")

        # Валидация: роль должна быть допустимой
        valid_roles = {'admin', 'manager', 'developer'}
        role_lower = str(role).lower()
        if role_lower not in valid_roles:
            raise ValueError(f"Роль должна быть одной из: {valid_roles}")

        self.id = None
        self.username = str(username).strip()
        self.email = str(email).strip()
        self.role = role_lower
        self.registration_date = datetime.now()

    def update_info(self, username=None, email=None, role=None) -> bool:
        """
        Обновление информации о пользователе.

        Args:
            username (str, optional): Новое имя пользователя
            email (str, optional): Новый email
            role (str, optional): Новая роль ('admin', 'manager', 'developer')

        Returns:
            bool: True если хотя бы одно поле было обновлено, False если изменений нет

        Raises:
            ValueError: Если переданные данные некорректны
        """
        updated = False

        # Обновление имени пользователя
        if username is not None:
            if not str(username).strip():
                raise ValueError("Имя пользователя не может быть пустым")
            if str(username).strip() != self.username:
                self.username = str(username).strip()
                updated = True

        # Обновление email
        if email is not None:
            if not self._is_valid_email(email):
                raise ValueError("Некорректный формат email")
            if str(email).strip() != self.email:
                self.email = str(email).strip()
                updated = True

        # Обновление роли
        if role is not None:
            valid_roles = ['admin', 'manager', 'developer']
            role_lower = str(role).lower()
            if role_lower not in valid_roles:
                raise ValueError(f"Роль должна быть одной из: {valid_roles}")
            if role_lower != self.role:
                self.role = role_lower
                updated = True

        return updated

    def to_dict(self) -> dict:
        """
        Преобразование пользователя в словарь для сериализации.

        Returns:
            dict: Словарь с данными пользователя, где дата регистрации преобразована в ISO формат
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None
        }

    def _is_valid_email(self, email) -> bool:
        """
        Проверяет, является ли email корректным.

        Returns:
            bool: True если email корректный, False иначе
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, str(email))
