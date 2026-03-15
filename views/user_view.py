import tkinter as tk
from tkinter import ttk
import re

# views/user_view.py

class UserView(ttk.Frame):
    """Представление для управления пользователями."""

    def __init__(self, parent, user_controller) -> None:
        """
        Инициализация представления пользователей.

        Args:
            parent: Родительский виджет
            user_controller: Контроллер пользователей
        """
        super().__init__(parent)

        self.user_controller = user_controller
        self.main_window = self.get_main_window()

        # Переменные для формы
        self.user_id = None
        self.username_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.role_var = tk.StringVar(value="developer")

        # Создание интерфейса
        self.create_widgets()
        self.refresh_users()

    def get_main_window(self):
        """Получение ссылки на главное окно."""
        parent = self.master
        while parent and not hasattr(parent, 'show_error'):
            parent = parent.master
        return parent

    def create_widgets(self) -> None:
        """Создание виджетов."""
        # Основной контейнер
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель - форма
        self.create_form_panel(main_frame)

        # Правая панель - таблица и задачи
        self.create_table_panel(main_frame)

    def create_form_panel(self, parent):
        """Создание панели с формой."""
        form_frame = ttk.LabelFrame(parent, text="Добавление/редактирование пользователя", padding=10)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Поля формы
        row = 0

        # Имя пользователя
        ttk.Label(form_frame, text="Имя пользователя:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.username_var, width=30).grid(row=row, column=1, pady=5, padx=(5, 0))
        row += 1

        # Email
        ttk.Label(form_frame, text="Email:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.email_var, width=30).grid(row=row, column=1, pady=5, padx=(5, 0))
        row += 1

        # Роль
        ttk.Label(form_frame, text="Роль:").grid(row=row, column=0, sticky=tk.W, pady=5)
        role_frame = ttk.Frame(form_frame)
        role_frame.grid(row=row, column=1, pady=5, padx=(5, 0))

        roles = [("Администратор", "admin"), ("Менеджер", "manager"), ("Разработчик", "developer")]
        for i, (text, value) in enumerate(roles):
            ttk.Radiobutton(
                role_frame,
                text=text,
                variable=self.role_var,
                value=value
            ).pack(side=tk.LEFT, padx=2)
        row += 2

        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Добавить", command=self.add_user).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Обновить", command=self.update_user).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Очистить", command=self.clear_form).pack(side=tk.LEFT, padx=2)

    def create_table_panel(self, parent):
        """Создание панели с таблицей и задачами."""
        # Верхняя часть - таблица пользователей
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Таблица пользователей
        columns = ('ID', 'Имя пользователя', 'Email', 'Роль', 'Дата регистрации')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)

        # Настройка колонок
        self.tree.heading('ID', text='ID')
        self.tree.heading('Имя пользователя', text='Имя пользователя')
        self.tree.heading('Email', text='Email')
        self.tree.heading('Роль', text='Роль')
        self.tree.heading('Дата регистрации', text='Дата регистрации')

        self.tree.column('ID', width=50)
        self.tree.column('Имя пользователя', width=150)
        self.tree.column('Email', width=200)
        self.tree.column('Роль', width=100)
        self.tree.column('Дата регистрации', width=150)

        # Скроллбар выглядит некрасиво, да и не нужен
        ##scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        ##self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ##scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Привязка событий
        self.tree.bind('<<TreeviewSelect>>', self.on_user_select)

        # Кнопки действий
        action_frame = ttk.Frame(table_frame)
        action_frame.pack(fill=tk.X, pady=5)

        ttk.Button(action_frame, text="Удалить", command=self.delete_selected).pack(side=tk.TOP, padx=2, pady=2)
        ttk.Button(action_frame, text="Обновить список", command=self.refresh_users).pack(side=tk.TOP, padx=2, pady=2)

        # Нижняя часть - задачи пользователя
        tasks_frame = ttk.LabelFrame(parent, text="Задачи пользователя", padding=10)
        tasks_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Таблица задач
        columns = ('ID', 'Название', 'Статус', 'Приоритет', 'Срок', 'Проект')
        self.tasks_tree = ttk.Treeview(tasks_frame, columns=columns, show='headings', height=5)

        self.tasks_tree.heading('ID', text='ID')
        self.tasks_tree.heading('Название', text='Название')
        self.tasks_tree.heading('Статус', text='Статус')
        self.tasks_tree.heading('Приоритет', text='Приоритет')
        self.tasks_tree.heading('Срок', text='Срок')
        self.tasks_tree.heading('Проект', text='Проект')

        self.tasks_tree.column('ID', width=50)
        self.tasks_tree.column('Название', width=200)
        self.tasks_tree.column('Статус', width=100)
        self.tasks_tree.column('Приоритет', width=80)
        self.tasks_tree.column('Срок', width=100)
        self.tasks_tree.column('Проект', width=150)

        # Скроллбар для задач
        tasks_scrollbar = ttk.Scrollbar(tasks_frame, orient=tk.VERTICAL, command=self.tasks_tree.yview)
        self.tasks_tree.configure(yscrollcommand=tasks_scrollbar.set)

        self.tasks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tasks_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_users(self) -> None:
        """Обновление списка пользователей."""
        try:
            users = self.user_controller.get_all_users()
            self.display_users(users)

        except Exception as e:
            self.main_window.show_error(f"Ошибка загрузки пользователей: {str(e)}")

    def display_users(self, users):
        """Отображение пользователей в таблице."""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Очистка таблицы задач
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)

        # Заполнение таблицы
        role_map = {
            "admin": "Администратор",
            "manager": "Менеджер",
            "developer": "Разработчик"
        }

        for user in users:
            reg_date = user.registration_date.strftime("%Y-%m-%d %H:%M") if user.registration_date else ""

            self.tree.insert('', tk.END, values=(
                user.id,
                user.username,
                user.email,
                role_map.get(user.role, user.role),
                reg_date
            ))

    def add_user(self) -> None:
        """Добавление нового пользователя."""
        try:
            # Получение данных из формы
            username = self.username_var.get().strip()
            email = self.email_var.get().strip()
            role = self.role_var.get()

            if not username:
                self.main_window.show_error("Имя пользователя не может быть пустым")
                return

            if not email:
                self.main_window.show_error("Email не может быть пустым")
                return

            # Простая валидация email
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                self.main_window.show_error("Неверный формат email")
                return

            # Добавление пользователя
            user_id = self.user_controller.add_user(username, email, role)

            self.main_window.show_info(f"Пользователь добавлен с ID: {user_id}")
            self.clear_form()
            self.refresh_users()

        except Exception as e:
            self.main_window.show_error(f"Ошибка при добавлении пользователя: {str(e)}")

    def update_user(self):
        """Обновление существующего пользователя."""
        if not self.user_id:
            self.main_window.show_error("Выберите пользователя для обновления")
            return

        try:
            # Подготовка данных для обновления
            data = {}

            username = self.username_var.get().strip()
            if username:
                data['username'] = username

            email = self.email_var.get().strip()
            if email:
                # Валидация email
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, email):
                    self.main_window.show_error("Неверный формат email")
                    return
                data['email'] = email

            role = self.role_var.get()
            if role:
                data['role'] = role

            if not data:
                self.main_window.show_error("Нет данных для обновления")
                return

            # Обновление пользователя
            result = self.user_controller.update_user(self.user_id, **data)

            if result:
                self.main_window.show_info("Пользователь обновлен")
                self.clear_form()
                self.refresh_users()
            else:
                self.main_window.show_error("Пользователь не найден")

        except Exception as e:
            self.main_window.show_error(f"Ошибка при обновлении пользователя: {str(e)}")

    def delete_selected(self) -> None:
        """Удаление выбранного пользователя."""
        selected = self.tree.selection()
        if not selected:
            self.main_window.show_error("Выберите пользователя для удаления")
            return

        user_id = self.tree.item(selected[0])['values'][0]
        username = self.tree.item(selected[0])['values'][1]

        if self.main_window.confirm(f"Удалить пользователя {username}?"):
            try:
                result = self.user_controller.delete_user(user_id)
                if result:
                    self.main_window.show_info("Пользователь удален")
                    self.clear_form()
                    self.refresh_users()
                else:
                    self.main_window.show_error("Пользователь не найден")
            except Exception as e:
                self.main_window.show_error(f"Ошибка при удалении: {str(e)}")

    def on_user_select(self, event):
        """Обработка выбора пользователя в таблице."""
        selected = self.tree.selection()
        if not selected:
            return

        # Получение данных пользователя
        values = self.tree.item(selected[0])['values']
        self.user_id = values[0]

        # Загрузка полной информации о пользователе
        try:
            user = self.user_controller.get_user(self.user_id)
            if user:
                # Заполнение формы
                self.username_var.set(user.username)
                self.email_var.set(user.email)
                self.role_var.set(user.role)

                # Загрузка задач пользователя
                self.load_user_tasks(self.user_id)

        except Exception as e:
            self.main_window.show_error(f"Ошибка загрузки пользователя: {str(e)}")

    def load_user_tasks(self, user_id):
        """Загрузка задач пользователя."""
        try:
            # Получаем контроллер задач через главное окно
            tasks = self.main_window.task_controller.get_tasks_by_user(user_id)

            # Очистка таблицы
            for item in self.tasks_tree.get_children():
                self.tasks_tree.delete(item)

            # Заполнение таблицы
            priority_map = {1: "Высокий", 2: "Средний", 3: "Низкий"}
            status_map = {
                "pending": "Ожидание",
                "in_progress": "В работе",
                "completed": "Завершено"
            }

            # Получаем проекты для отображения названий
            projects = {}
            try:
                all_projects = self.main_window.project_controller.get_all_projects()
                projects = {p.id: p.name for p in all_projects}
            except:
                pass

            for task in tasks:
                due_date = task.due_date.strftime("%Y-%m-%d") if task.due_date else ""
                project_name = projects.get(task.project_id, f"ID:{task.project_id}")

                self.tasks_tree.insert('', tk.END, values=(
                    task.id,
                    task.title,
                    status_map.get(task.status, task.status),
                    priority_map.get(task.priority, task.priority),
                    due_date,
                    project_name
                ))

        except Exception as e:
            self.main_window.show_error(f"Ошибка загрузки задач: {str(e)}")

    def clear_form(self):
        """Очистка формы."""
        self.user_id = None
        self.username_var.set("")
        self.email_var.set("")
        self.role_var.set("developer")

        # Очистка таблицы задач
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)
