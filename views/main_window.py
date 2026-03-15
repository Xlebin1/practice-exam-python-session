# Главное окно приложения согласно README.md

import tkinter as tk
from tkinter import ttk, messagebox
from views.project_view import ProjectView
from views.task_view import TaskView
from views.user_view import UserView

# views/main_window.py

class MainWindow(tk.Tk):
    """Главное окно приложения."""

    def __init__(self, task_controller, project_controller, user_controller) -> None:
        """
        Инициализация главного окна.

        Args:
            project_controller: Контроллер проектов
            task_controller: Контроллер задач
            user_controller: Контроллер пользователей
        """
        super().__init__()

        self.title("Система управления задачами")
        self.geometry("1600x600")

        # Сохранение контроллеров
        self.project_controller = project_controller
        self.task_controller = task_controller
        self.user_controller = user_controller

        # Создание меню
        self.create_menu()

        # Создание основного контейнера с вкладками
        self.create_notebook()

        # Создание строки статуса
        self.create_status_bar()

        # Обработка закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_menu(self):
        """Создание главного меню."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Обновить все", command=self.refresh_all)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.on_closing)

        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
        help_menu.add_command(label="Помощь", command=self.show_help)

    def create_notebook(self):
        """Создание вкладок для управления разделами."""
        # Основной контейнер
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Создание Notebook (вкладки)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка задач
        self.tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tasks_frame, text="Задачи")
        self.task_view = TaskView(self.tasks_frame,
                                  self.task_controller, self.project_controller, self.user_controller)
        self.task_view.pack(fill="both", expand=True)

        # Вкладка проектов
        self.projects_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.projects_frame, text="Проекты")
        self.project_view = ProjectView(self.projects_frame, self.project_controller)
        self.project_view.pack(fill="both", expand=True)

        # Вкладка пользователей
        self.users_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.users_frame, text="Пользователи")
        self.user_view = UserView(self.users_frame, self.user_controller)
        self.user_view.pack(fill="both", expand=True)

        # Привязка события смены вкладки
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

    def create_status_bar(self):
        """Создание строки статуса."""
        self.status_frame = ttk.Frame(self, relief=tk.SUNKEN, padding=(5, 2))
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = ttk.Label(
            self.status_frame,
            text="Готов к работе"
        )
        self.status_label.pack(side=tk.LEFT)

        # Информация о количестве элементов
        self.stats_label = ttk.Label(
            self.status_frame,
            text=""
        )
        self.stats_label.pack(side=tk.RIGHT)

        self.update_stats()

    def update_status(self, message):
        """Обновление сообщения в строке статуса."""
        self.status_label.config(text=message)
        self.update_idletasks()

    def update_stats(self):
        """Обновление статистики в строке статуса."""
        try:
            tasks = self.task_controller.get_all_tasks()
            projects = self.project_controller.get_all_projects()
            users = self.user_controller.get_all_users()

            stats_text = f"Задач: {len(tasks)} | Проектов: {len(projects)} | Пользователей: {len(users)}"
            self.stats_label.config(text=stats_text)
        except Exception:
            self.stats_label.config(text="Ошибка загрузки статистики")

    def on_tab_changed(self, event):
        """Обработчик смены вкладки."""
        current_tab = self.notebook.index(self.notebook.select())
        tab_names = ["задачам", "проектам", "пользователям"]

        if current_tab < len(tab_names):
            self.update_status(f"Работа с {tab_names[current_tab]}")

            # Обновление соответствующего представления
            if current_tab == 0:
                self.task_view.refresh()
            elif current_tab == 1:
                self.project_view.refresh()
            elif current_tab == 2:
                self.user_view.refresh_users()

    def refresh_all(self):
        """Обновление всех представлений."""
        self.update_status("Обновление данных...")
        self.task_view.refresh()
        self.project_view.refresh()
        self.user_view.refresh_users()
        self.update_stats()
        self.update_status("Данные обновлены")

    def show_about(self):
        """Показ информации о программе."""
        about_text = """
        Система управления задачами

        Версия: 1.0
        Разработано с использованием:
        - Python 3.12
        - Tkinter
        - SQLite

        Архитектура: MVC
        """
        messagebox.showinfo("О программе", about_text)

    def show_help(self):
        """Показ справки."""
        help_text = """
        Справка по использованию:

        Задачи:
        - Добавление: заполните поля и нажмите "Добавить"
        - Редактирование: выберите задачу и нажмите "Изменить"
        - Удаление: выберите задачу и нажмите "Удалить"

        Проекты:
        - Управление проектами во вкладке "Проекты"

        Пользователи:
        - Управление пользователями во вкладке "Пользователи"

        Статусы задач:
        - pending: ожидание
        - in_progress: в работе
        - completed: завершено
        """
        messagebox.showinfo("Помощь", help_text)

    def show_error(self, message):
        """Показ сообщения об ошибке."""
        messagebox.showerror("Ошибка", message)
        self.update_status("Ошибка: " + message[:50] + "...")

    def show_info(self, message):
        """Показ информационного сообщения."""
        messagebox.showinfo("Информация", message)
        self.update_status(message)

    def confirm(self, message):
        """Запрос подтверждения."""
        return messagebox.askyesno("Подтверждение", message)

    def on_closing(self):
        """Обработка закрытия окна."""
        if self.confirm("Вы действительно хотите выйти?"):
            self.destroy()
