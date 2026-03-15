from models.project import Project

# controllers/project_controller.py

class ProjectController:
    """Контроллер для управления проектами."""

    def __init__(self, db_manager):
        """
        Инициализация контроллера проектов.

        Args:
            db_manager: Менеджер базы данных
        """
        self.db_manager = db_manager

    def add_project(self, name, description, start_date, end_date):
        """
        Добавление нового проекта.

        Args:
            name (str): Название проекта
            description (str): Описание проекта
            start_date (datetime): Дата начала
            end_date (datetime): Дата окончания

        Returns:
            int: ID созданного проекта

        Raises:
            ValueError: Если данные не проходят валидацию
        """
        # Создание объекта проекта (валидация произойдет в конструкторе Project)
        project = Project(name, description, start_date, end_date)

        # Сохранение в базу данных
        project_id = self.db_manager.add_project(project)

        return project_id

    def get_project(self, project_id):
        """
        Получение проекта по ID.

        Args:
            project_id (int): ID проекта

        Returns:
            Project: Объект проекта или None, если проект не найден
        """
        return self.db_manager.get_project_by_id(project_id)

    def get_all_projects(self):
        """
        Получение всех проектов.

        Returns:
            list: Список всех проектов
        """
        return self.db_manager.get_all_projects()

    def update_project(self, project_id, **kwargs):
        """
        Обновление проекта.

        Args:
            project_id (int): ID проекта
            **kwargs: Поля для обновления (name, description, start_date, end_date, status)

        Returns:
            bool: True если проект обновлен, False если проект не найден

        Raises:
            ValueError: Если данные не проходят валидацию
        """
        # Получаем текущий проект для проверки
        project = self.get_project(project_id)
        if not project:
            return False

        # Валидация полей (без проверки типов)
        if 'name' in kwargs:
            if not kwargs['name'] or not str(kwargs['name']).strip():
                raise ValueError("Название проекта не может быть пустым")
            kwargs['name'] = str(kwargs['name']).strip()

        if 'status' in kwargs:
            valid_statuses = ['active', 'completed', 'on_hold']
            new_status = str(kwargs['status']).lower()
            if new_status not in valid_statuses:
                raise ValueError(f"Статус должен быть одним из: {valid_statuses}")

            # Проверка логики перехода
            if project.status == 'completed' and new_status != 'completed':
                raise ValueError("Нельзя изменить статус с 'completed' на другой")

            kwargs['status'] = new_status

        # Проверка дат, если обе обновляются
        if 'start_date' in kwargs and 'end_date' in kwargs:
            if kwargs['start_date'] > kwargs['end_date']:
                raise ValueError("Дата начала не может быть позже даты окончания")
        elif 'start_date' in kwargs:
            # Сравниваем с существующей датой окончания
            if kwargs['start_date'] > project.end_date:
                raise ValueError("Дата начала не может быть позже даты окончания")
        elif 'end_date' in kwargs:
            # Сравниваем с существующей датой начала
            if project.start_date > kwargs['end_date']:
                raise ValueError("Дата начала не может быть позже даты окончания")

        # Преобразование дат в строки для БД
        if 'start_date' in kwargs and kwargs['start_date']:
            kwargs['start_date'] = kwargs['start_date'].isoformat()

        if 'end_date' in kwargs and kwargs['end_date']:
            kwargs['end_date'] = kwargs['end_date'].isoformat()

        # Обновление в базе данных
        return self.db_manager.update_project(project_id, **kwargs)

    def delete_project(self, project_id):
        """
        Удаление проекта.

        Args:
            project_id (int): ID проекта

        Returns:
            bool: True если проект удален, False если проект не найден
        """
        return self.db_manager.delete_project(project_id)

    def update_project_status(self, project_id, new_status):
        """
        Обновление статуса проекта.

        Args:
            project_id (int): ID проекта
            new_status (str): Новый статус ('active', 'completed', 'on_hold')

        Returns:
            bool: True если статус обновлен, False если проект не найден

        Raises:
            ValueError: Если статус недопустим
        """
        # Используем update_project для обновления статуса
        return self.update_project(project_id, status=new_status)

    def get_project_progress(self, project_id):
        """
        Получение прогресса проекта.

        Args:
            project_id (int): ID проекта

        Returns:
            float: Прогресс проекта в процентах (0-100)

        Raises:
            ValueError: Если проект не найден
        """
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Проект с ID {project_id} не найден")

        return project.get_progress()
