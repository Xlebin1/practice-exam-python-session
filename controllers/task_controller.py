from models.task import Task

# controllers/task_controller.py

class TaskController:
    """Контроллер для управления задачами."""

    def __init__(self, db_manager):
        """
        Инициализация контроллера задач.

        Args:
            db_manager: Менеджер базы данных
        """
        self.db_manager = db_manager

    def add_task(self, title, description, priority, due_date, project_id, assignee_id):
        """
        Добавление новой задачи.

        Args:
            title (str): Название задачи
            description (str): Описание задачи
            priority (int): Приоритет (1-высокий, 2-средний, 3-низкий)
            due_date (datetime): Срок выполнения
            project_id (int): ID проекта
            assignee_id (int): ID исполнителя

        Returns:
            int: ID созданной задачи

        Raises:
            ValueError: Если данные не проходят валидацию
        """
        # Создание объекта задачи (валидация произойдет в конструкторе Task)
        task = Task(title, description, priority, due_date, project_id, assignee_id)

        # Сохранение в базу данных
        task_id = self.db_manager.add_task(task)

        return task_id

    def get_task(self, task_id):
        """
        Получение задачи по ID.

        Args:
            task_id (int): ID задачи

        Returns:
            Task: Объект задачи или None, если задача не найдена
        """
        return self.db_manager.get_task_by_id(task_id)

    def get_all_tasks(self):
        """
        Получение всех задач.

        Returns:
            list: Список всех задач
        """
        return self.db_manager.get_all_tasks()

    def update_task(self, task_id, **kwargs):
        """
        Обновление задачи.

        Args:
            task_id (int): ID задачи
            **kwargs: Поля для обновления (title, description, priority,
                     due_date, project_id, assignee_id, status)

        Returns:
            bool: True если задача обновлена, False если задача не найдена

        Raises:
            ValueError: Если данные не проходят валидацию
        """
        # Получаем текущую задачу для проверки
        task = self.get_task(task_id)
        if not task:
            return False

        # Валидация полей (без проверки типов)
        if 'title' in kwargs:
            if not kwargs['title'] or not str(kwargs['title']).strip():
                raise ValueError("Название задачи не может быть пустым")
            kwargs['title'] = str(kwargs['title']).strip()

        if 'priority' in kwargs:
            if kwargs['priority'] not in [1, 2, 3]:
                raise ValueError("Приоритет должен быть 1 (высокий), 2 (средний) или 3 (низкий)")

        if 'project_id' in kwargs:
            if kwargs['project_id'] <= 0:
                raise ValueError("ID проекта должен быть положительным числом")

        if 'assignee_id' in kwargs:
            if kwargs['assignee_id'] <= 0:
                raise ValueError("ID исполнителя должен быть положительным числом")

        if 'status' in kwargs:
            # Проверка допустимости статуса
            valid_statuses = ['pending', 'in_progress', 'completed']
            new_status = str(kwargs['status']).lower()
            if new_status not in valid_statuses:
                raise ValueError(f"Статус должен быть одним из: {valid_statuses}")

            # Проверка логики перехода
            if task.status == 'completed' and new_status != 'completed':
                raise ValueError("Нельзя изменить статус с 'completed' на другой")

            kwargs['status'] = new_status

        # Преобразование даты в строку для БД
        if 'due_date' in kwargs and kwargs['due_date']:
            kwargs['due_date'] = kwargs['due_date'].isoformat()

        # Обновление в базе данных
        return self.db_manager.update_task(task_id, **kwargs)

    def delete_task(self, task_id):
        """
        Удаление задачи.

        Args:
            task_id (int): ID задачи

        Returns:
            bool: True если задача удалена, False если задача не найдена
        """
        return self.db_manager.delete_task(task_id)

    def search_tasks(self, query):
        """
        Поиск задач по названию или описанию.

        Args:
            query (str): Поисковый запрос

        Returns:
            list: Список задач, соответствующих запросу
        """
        return self.db_manager.search_tasks(query)

    def update_task_status(self, task_id, new_status):
        """
        Обновление статуса задачи.

        Args:
            task_id (int): ID задачи
            new_status (str): Новый статус ('pending', 'in_progress', 'completed')

        Returns:
            bool: True если статус обновлен, False если задача не найдена

        Raises:
            ValueError: Если статус недопустим
        """
        # Используем update_task для обновления статуса
        return self.update_task(task_id, status=new_status)

    def get_overdue_tasks(self):
        """
        Получение всех просроченных задач.

        Returns:
            list: Список просроченных задач
        """
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks if task.is_overdue()]

    def get_tasks_by_project(self, project_id):
        """
        Получение всех задач проекта.

        Args:
            project_id (int): ID проекта

        Returns:
            list: Список задач проекта
        """
        return self.db_manager.get_tasks_by_project(project_id)

    def get_tasks_by_user(self, user_id):
        """
        Получение всех задач пользователя.

        Args:
            user_id (int): ID пользователя

        Returns:
            list: Список задач пользователя
        """
        return self.db_manager.get_tasks_by_user(user_id)
