from datetime import datetime

'''
class Task:
    def __init__(self, title, description, priority, due_date, project_id, assignee_id) -> None:
        pass

    def update_status(self, new_status) -> bool:
        pass

    def is_overdue(self) -> bool:
        pass

    def to_dict(self) -> dict:
        pass
'''

# models/task.py

class Task:
    """Класс для представления задачи в системе управления задачами."""

    def __init__(self, title, description, priority, due_date, project_id, assignee_id) -> None:
        """
        Инициализация новой задачи.

        Args:
            title (str): Название задачи
            description (str): Описание задачи
            priority (int): Приоритет задачи (1 - высокий, 2 - средний, 3 - низкий)
            due_date (datetime): Срок выполнения задачи
            project_id (int): ID проекта, к которому относится задача
            assignee_id (int): ID исполнителя задачи

        Raises:
            ValueError: Если название пустое, приоритет не 1-3 или project_id/assignee_id <= 0
        """
        # Валидация: название не может быть пустым
        if not title or not str(title).strip():
            raise ValueError("Название задачи должно быть непустой строкой")

        # Валидация: приоритет должен быть 1, 2 или 3
        if priority not in [1, 2, 3]:
            raise ValueError("Приоритет должен быть 1 (высокий), 2 (средний) или 3 (низкий)")

        # Валидация: ID проекта должен быть положительным числом
        if project_id <= 0:
            raise ValueError("ID проекта должен быть положительным числом")

        # Валидация: ID исполнителя должен быть положительным числом
        if assignee_id <= 0:
            raise ValueError("ID исполнителя должен быть положительным числом")

        self.id = None
        self.title = str(title).strip()
        self.description = str(description).strip() if description else ""
        self.priority = priority
        self.due_date = due_date
        self.project_id = project_id
        self.assignee_id = assignee_id
        self.status = 'pending'

    def update_status(self, new_status) -> bool:
        """
        Обновление статуса задачи.

        Args:
            new_status (str): Новый статус ('pending', 'in_progress', 'completed')

        Returns:
            bool: True если статус был изменен, False если статус не изменился

        Raises:
            ValueError: Если указан недопустимый статус или попытка изменить статус
                       завершенной задачи
        """
        valid_statuses = ['pending', 'in_progress', 'completed']

        # Приводим к нижнему регистру для сравнения
        new_status = str(new_status).lower()

        if new_status not in valid_statuses:
            raise ValueError(f"Статус должен быть одним из: {valid_statuses}")

        # Проверка, изменился ли статус
        if self.status == new_status:
            return False

        # Проверка корректности перехода (нельзя из completed в другое)
        if self.status == 'completed' and new_status != 'completed':
            raise ValueError("Нельзя изменить статус с 'completed' на другой")

        self.status = new_status
        return True

    def is_overdue(self) -> bool:
        """
        Проверка, просрочена ли задача.

        Returns:
            bool: True если текущая дата больше срока выполнения и задача не завершена,
                  False в противном случае
        """
        # Завершенные задачи не считаются просроченными
        if self.status == 'completed':
            return False
        return datetime.now() > self.due_date

    def to_dict(self) -> dict:
        """
        Преобразование задачи в словарь для сериализации.

        Returns:
            dict: Словарь с данными задачи, где дата преобразована в ISO формат
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'project_id': self.project_id,
            'assignee_id': self.assignee_id,
            'status': self.status
        }
