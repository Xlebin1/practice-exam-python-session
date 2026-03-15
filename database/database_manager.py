import sqlite3
from models.task import Task
from models.project import Project
from models.user import User
from datetime import datetime

# database/database_manager.py

class DatabaseManager:
    """Класс для управления базой данных SQLite."""

    def __init__(self, db_name='tasks.db'):
        """
        Инициализация менеджера базы данных.

        Args:
            db_name (str): Имя файла базы данных
        """
        self.db_name = db_name
        self.connection = None
        self._create_connection()
        self.create_task_table()
        self.create_project_table()
        self.create_user_table()

    def _create_connection(self):
        """Создание соединения с базой данных."""
        self.connection = sqlite3.connect(self.db_name)
        self.connection.row_factory = sqlite3.Row  # Для доступа к колонкам по имени

    def _execute_query(self, query, params=()):
        """
        Выполнение SQL запроса.

        Args:
            query (str): SQL запрос
            params (tuple): Параметры запроса

        Returns:
            cursor: Курсор после выполнения запроса
        """
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor

    # ========== МЕТОДЫ ДЛЯ РАБОТЫ С ЗАДАЧАМИ ==========

    def create_task_table(self):
        """Создание таблицы задач, если она не существует."""
        query = '''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                due_date TEXT,
                project_id INTEGER,
                assignee_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
                FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL
            )
        '''
        self._execute_query(query)

    def add_task(self, task):
        """
        Добавление новой задачи.

        Args:
            task (Task): Объект задачи

        Returns:
            int: ID добавленной задачи

        Raises:
            ValueError: Если задача не является объектом Task
        """
        if not isinstance(task, Task):
            raise ValueError("Ожидается объект Task")

        query = '''
            INSERT INTO tasks (title, description, priority, status, due_date, project_id, assignee_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            task.title,
            task.description,
            task.priority,
            task.status,
            task.due_date.isoformat() if task.due_date else None,
            task.project_id,
            task.assignee_id
        )

        cursor = self._execute_query(query, params)
        task_id = cursor.lastrowid
        task.id = task_id
        return task_id

    def get_task_by_id(self, task_id):
        """
        Получение задачи по ID.

        Args:
            task_id (int): ID задачи

        Returns:
            Task: Объект задачи или None, если задача не найдена
        """
        query = 'SELECT * FROM tasks WHERE id = ?'
        cursor = self._execute_query(query, (task_id,))
        row = cursor.fetchone()

        if row:
            # Преобразование строки даты в объект datetime
            due_date = None
            if row['due_date']:
                due_date = datetime.fromisoformat(row['due_date'])

            task = Task(
                title=row['title'],
                description=row['description'] or '',
                priority=row['priority'],
                due_date=due_date,
                project_id=row['project_id'],
                assignee_id=row['assignee_id']
            )
            task.id = row['id']
            task.status = row['status']
            return task

        return None

    def get_all_tasks(self):
        """
        Получение всех задач.

        Returns:
            list: Список объектов Task
        """
        query = 'SELECT * FROM tasks ORDER BY due_date'
        cursor = self._execute_query(query)
        rows = cursor.fetchall()

        tasks = []
        for row in rows:
            due_date = None
            if row['due_date']:
                due_date = datetime.fromisoformat(row['due_date'])

            task = Task(
                title=row['title'],
                description=row['description'] or '',
                priority=row['priority'],
                due_date=due_date,
                project_id=row['project_id'],
                assignee_id=row['assignee_id']
            )
            task.id = row['id']
            task.status = row['status']
            tasks.append(task)

        return tasks

    def update_task(self, task_id, **kwargs):
        """
        Обновление задачи.

        Args:
            task_id (int): ID задачи
            **kwargs: Поля для обновления (title, description, priority, status, due_date, project_id, assignee_id)

        Returns:
            bool: True если задача обновлена, False если задача не найдена
        """
        if not kwargs:
            return False

        # Формирование запроса динамически
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        set_clause += ", updated_at = CURRENT_TIMESTAMP"

        query = f'UPDATE tasks SET {set_clause} WHERE id = ?'
        params = list(kwargs.values()) + [task_id]

        cursor = self._execute_query(query, params)
        return cursor.rowcount > 0

    def delete_task(self, task_id):
        """
        Удаление задачи.

        Args:
            task_id (int): ID задачи

        Returns:
            bool: True если задача удалена, False если задача не найдена
        """
        query = 'DELETE FROM tasks WHERE id = ?'
        cursor = self._execute_query(query, (task_id,))
        return cursor.rowcount > 0

    def search_tasks(self, query_text):
        """
        Поиск задач по названию или описанию.

        Args:
            query_text (str): Текст для поиска

        Returns:
            list: Список объектов Task, соответствующих запросу
        """
        search_pattern = f'%{query_text}%'
        query = '''
            SELECT * FROM tasks
            WHERE title LIKE ? OR description LIKE ?
            ORDER BY due_date
        '''
        cursor = self._execute_query(query, (search_pattern, search_pattern))
        rows = cursor.fetchall()

        tasks = []
        for row in rows:
            due_date = None
            if row['due_date']:
                due_date = datetime.fromisoformat(row['due_date'])

            task = Task(
                title=row['title'],
                description=row['description'] or '',
                priority=row['priority'],
                due_date=due_date,
                project_id=row['project_id'],
                assignee_id=row['assignee_id']
            )
            task.id = row['id']
            task.status = row['status']
            tasks.append(task)

        return tasks

    def get_tasks_by_project(self, project_id):
        """
        Получение всех задач проекта.

        Args:
            project_id (int): ID проекта

        Returns:
            list: Список объектов Task
        """
        query = 'SELECT * FROM tasks WHERE project_id = ? ORDER BY due_date'
        cursor = self._execute_query(query, (project_id,))
        rows = cursor.fetchall()

        tasks = []
        for row in rows:
            due_date = None
            if row['due_date']:
                due_date = datetime.fromisoformat(row['due_date'])

            task = Task(
                title=row['title'],
                description=row['description'] or '',
                priority=row['priority'],
                due_date=due_date,
                project_id=row['project_id'],
                assignee_id=row['assignee_id']
            )
            task.id = row['id']
            task.status = row['status']
            tasks.append(task)

        return tasks

    def get_tasks_by_user(self, user_id):
        """
        Получение всех задач пользователя.

        Args:
            user_id (int): ID пользователя

        Returns:
            list: Список объектов Task
        """
        query = 'SELECT * FROM tasks WHERE assignee_id = ? ORDER BY due_date'
        cursor = self._execute_query(query, (user_id,))
        rows = cursor.fetchall()

        tasks = []
        for row in rows:
            due_date = None
            if row['due_date']:
                due_date = datetime.fromisoformat(row['due_date'])

            task = Task(
                title=row['title'],
                description=row['description'] or '',
                priority=row['priority'],
                due_date=due_date,
                project_id=row['project_id'],
                assignee_id=row['assignee_id']
            )
            task.id = row['id']
            task.status = row['status']
            tasks.append(task)

        return tasks

    # ========== МЕТОДЫ ДЛЯ РАБОТЫ С ПРОЕКТАМИ ==========

    def create_project_table(self):
        """Создание таблицы проектов, если она не существует."""
        query = '''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        '''
        self._execute_query(query)

    def add_project(self, project):
        """
        Добавление нового проекта.

        Args:
            project (Project): Объект проекта

        Returns:
            int: ID добавленного проекта

        Raises:
            ValueError: Если проект не является объектом Project
        """
        if not isinstance(project, Project):
            raise ValueError("Ожидается объект Project")

        query = '''
            INSERT INTO projects (name, description, start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?)
        '''
        params = (
            project.name,
            project.description,
            project.start_date.isoformat(),
            project.end_date.isoformat(),
            project.status
        )

        cursor = self._execute_query(query, params)
        project_id = cursor.lastrowid
        project.id = project_id
        return project_id

    def get_project_by_id(self, project_id):
        """
        Получение проекта по ID.

        Args:
            project_id (int): ID проекта

        Returns:
            Project: Объект проекта или None, если проект не найден
        """
        query = 'SELECT * FROM projects WHERE id = ?'
        cursor = self._execute_query(query, (project_id,))
        row = cursor.fetchone()

        if row:
            project = Project(
                name=row['name'],
                description=row['description'] or '',
                start_date=datetime.fromisoformat(row['start_date']),
                end_date=datetime.fromisoformat(row['end_date'])
            )
            project.id = row['id']
            project.status = row['status']
            return project

        return None

    def get_all_projects(self):
        """
        Получение всех проектов.

        Returns:
            list: Список объектов Project
        """
        query = 'SELECT * FROM projects ORDER BY start_date'
        cursor = self._execute_query(query)
        rows = cursor.fetchall()

        projects = []
        for row in rows:
            project = Project(
                name=row['name'],
                description=row['description'] or '',
                start_date=datetime.fromisoformat(row['start_date']),
                end_date=datetime.fromisoformat(row['end_date'])
            )
            project.id = row['id']
            project.status = row['status']
            projects.append(project)

        return projects

    def update_project(self, project_id, **kwargs):
        """
        Обновление проекта.

        Args:
            project_id (int): ID проекта
            **kwargs: Поля для обновления (name, description, start_date, end_date, status)

        Returns:
            bool: True если проект обновлен, False если проект не найден
        """
        if not kwargs:
            return False

        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        set_clause += ", updated_at = CURRENT_TIMESTAMP"

        query = f'UPDATE projects SET {set_clause} WHERE id = ?'
        params = list(kwargs.values()) + [project_id]

        cursor = self._execute_query(query, params)
        return cursor.rowcount > 0

    def delete_project(self, project_id):
        """
        Удаление проекта.

        Args:
            project_id (int): ID проекта

        Returns:
            bool: True если проект удален, False если проект не найден
        """
        query = 'DELETE FROM projects WHERE id = ?'
        cursor = self._execute_query(query, (project_id,))
        return cursor.rowcount > 0

    # ========== МЕТОДЫ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ==========

    def create_user_table(self):
        """Создание таблицы пользователей, если она не существует."""
        query = '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL,
                registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        '''
        self._execute_query(query)

    def add_user(self, user):
        """
        Добавление нового пользователя.

        Args:
            user (User): Объект пользователя

        Returns:
            int: ID добавленного пользователя

        Raises:
            ValueError: Если пользователь не является объектом User
        """
        if not isinstance(user, User):
            raise ValueError("Ожидается объект User")

        query = '''
            INSERT INTO users (username, email, role)
            VALUES (?, ?, ?)
        '''
        params = (user.username, user.email, user.role)

        cursor = self._execute_query(query, params)
        user_id = cursor.lastrowid
        user.id = user_id
        return user_id

    def get_user_by_id(self, user_id):
        """
        Получение пользователя по ID.

        Args:
            user_id (int): ID пользователя

        Returns:
            User: Объект пользователя или None, если пользователь не найден
        """
        query = 'SELECT * FROM users WHERE id = ?'
        cursor = self._execute_query(query, (user_id,))
        row = cursor.fetchone()

        if row:
            user = User(
                username=row['username'],
                email=row['email'],
                role=row['role']
            )
            user.id = row['id']
            if row['registration_date']:
                user.registration_date = datetime.fromisoformat(row['registration_date'])
            return user

        return None

    def get_all_users(self):
        """
        Получение всех пользователей.

        Returns:
            list: Список объектов User
        """
        query = 'SELECT * FROM users ORDER BY username'
        cursor = self._execute_query(query)
        rows = cursor.fetchall()

        users = []
        for row in rows:
            user = User(
                username=row['username'],
                email=row['email'],
                role=row['role']
            )
            user.id = row['id']
            if row['registration_date']:
                user.registration_date = datetime.fromisoformat(row['registration_date'])
            users.append(user)

        return users

    def update_user(self, user_id, **kwargs):
        """
        Обновление пользователя.

        Args:
            user_id (int): ID пользователя
            **kwargs: Поля для обновления (username, email, role)

        Returns:
            bool: True если пользователь обновлен, False если пользователь не найден
        """
        if not kwargs:
            return False

        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        set_clause += ", updated_at = CURRENT_TIMESTAMP"

        query = f'UPDATE users SET {set_clause} WHERE id = ?'
        params = list(kwargs.values()) + [user_id]

        cursor = self._execute_query(query, params)
        return cursor.rowcount > 0

    def delete_user(self, user_id):
        """
        Удаление пользователя.

        Args:
            user_id (int): ID пользователя

        Returns:
            bool: True если пользователь удален, False если пользователь не найден
        """
        query = 'DELETE FROM users WHERE id = ?'
        cursor = self._execute_query(query, (user_id,))
        return cursor.rowcount > 0

    def close(self):
        """Закрытие соединения с базой данных."""
        if self.connection:
            self.connection.close()

    def __enter__(self):
        """Поддержка контекстного менеджера."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое закрытие соединения при выходе из контекста."""
        self.close()
