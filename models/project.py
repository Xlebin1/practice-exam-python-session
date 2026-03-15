from datetime import datetime

'''
class Project:
    def __init__(self, name, description, start_date, end_date) -> None:
        pass

    def update_status(self, new_status) -> bool:
        pass

    def get_progress(self) -> float:
        pass

    def to_dict(self) -> dict:
        pass
'''

# models/project.py

class Project:
    """Класс для представления проекта в системе управления задачами."""

    def __init__(self, name, description, start_date, end_date) -> None:
        """
        Инициализация нового проекта.

        Args:
            name (str): Название проекта
            description (str): Описание проекта
            start_date (datetime): Дата начала проекта
            end_date (datetime): Дата окончания проекта

        Raises:
            ValueError: Если название пустое или дата начала позже даты окончания
        """
        # Валидация: название не может быть пустым
        if not name or not str(name).strip():
            raise ValueError("Название проекта не может быть пустым")

        # Валидация: дата начала не позже даты окончания
        if start_date > end_date:
            raise ValueError("Дата начала не может быть позже даты окончания")

        self.id = None
        self.name = str(name).strip()
        self.description = str(description).strip() if description else ""
        self.start_date = start_date
        self.end_date = end_date
        self.status = 'active'

    def update_status(self, new_status) -> bool:
        """
        Обновление статуса проекта.

        Args:
            new_status (str): Новый статус ('active', 'completed', 'on_hold')

        Returns:
            bool: True если статус был изменен, False если статус не изменился

        Raises:
            ValueError: Если указан недопустимый статус или попытка изменить статус
                       завершенного проекта
        """
        valid_statuses = ['active', 'completed', 'on_hold']

        # Приводим к нижнему регистру для сравнения
        new_status = str(new_status).lower()

        if new_status not in valid_statuses:
            raise ValueError(f"Статус должен быть одним из: {valid_statuses}")

        if self.status == new_status:
            return False

        # Нельзя изменить статус с completed на другой
        if self.status == 'completed' and new_status != 'completed':
            raise ValueError("Нельзя изменить статус с 'completed' на другой")

        self.status = new_status
        return True

    def get_progress(self) -> float:
        """
        Расчет прогресса выполнения проекта на основе временных параметров.

        Returns:
            float: Прогресс в процентах (0-100):
                - 0%: проект еще не начался
                - 1-98%: проект в процессе выполнения
                - 99%: проект просрочен, но не завершен
                - 100%: проект завершен
        """
        now = datetime.now()

        if self.status == 'completed':
            return 100.0

        if now < self.start_date:
            return 0.0

        if now > self.end_date:
            return 99.0

        total_duration = (self.end_date - self.start_date).total_seconds()
        if total_duration <= 0:
            return 100.0

        elapsed = (now - self.start_date).total_seconds()
        progress = (elapsed / total_duration) * 100
        return min(round(progress, 2), 99.0)

    def to_dict(self) -> dict:
        """
        Преобразование проекта в словарь для сериализации.

        Returns:
            dict: Словарь с данными проекта, где даты преобразованы в ISO формат
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status
        }
