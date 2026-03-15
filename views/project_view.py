import tkinter as tk
from tkinter import ttk
from datetime import datetime

# views/project_view.py

class ProjectView(ttk.Frame):
    """Представление для управления проектами."""

    def __init__(self, parent, project_controller) -> None:
        """
        Инициализация представления проектов.

        Args:
            parent: Родительский виджет
            project_controller: Контроллер проектов
        """
        super().__init__(parent)

        self.project_controller = project_controller
        self.main_window = self.get_main_window()

        # Переменные для формы
        self.project_id = None
        self.name_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        self.status_var = tk.StringVar(value="active")

        # Создание интерфейса
        self.create_widgets()
        self.refresh()

    def get_main_window(self):
        """Получение ссылки на главное окно."""
        parent = self.master
        while parent and not hasattr(parent, 'show_error'):
            parent = parent.master
        return parent

    def create_widgets(self):
        """Создание виджетов."""
        # Основной контейнер
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель - форма
        self.create_form_panel(main_frame)

        # Правая панель - таблица и информация
        self.create_table_panel(main_frame)

    def create_form_panel(self, parent):
        """Создание панели с формой."""
        form_frame = ttk.LabelFrame(parent, text="Добавление/редактирование проекта", padding=10)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Поля формы
        row = 0

        # Название
        ttk.Label(form_frame, text="Название:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.name_var, width=30).grid(row=row, column=1, pady=5, padx=(5, 0))
        row += 1

        # Описание
        ttk.Label(form_frame, text="Описание:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.description_var, width=30).grid(row=row, column=1, pady=5, padx=(5, 0))
        row += 1

        # Дата начала
        ttk.Label(form_frame, text="Дата начала:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.start_date_var, width=30).grid(row=row, column=1, pady=5, padx=(5, 0))
        ttk.Label(form_frame, text="ГГГГ-ММ-ДД", font=('Arial', 8)).grid(row=row+1, column=1, sticky=tk.W)
        row += 2

        # Дата окончания
        ttk.Label(form_frame, text="Дата окончания:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.end_date_var, width=30).grid(row=row, column=1, pady=5, padx=(5, 0))
        ttk.Label(form_frame, text="ГГГГ-ММ-ДД", font=('Arial', 8)).grid(row=row+1, column=1, sticky=tk.W)
        row += 2

        # Статус
        ttk.Label(form_frame, text="Статус:").grid(row=row, column=0, sticky=tk.W, pady=5)
        status_frame = ttk.Frame(form_frame)
        status_frame.grid(row=row, column=1, pady=5, padx=(5, 0))

        statuses = [("Активный", "active"), ("Завершен", "completed"), ("Приостановлен", "on_hold")]
        for i, (text, value) in enumerate(statuses):
            ttk.Radiobutton(
                status_frame,
                text=text,
                variable=self.status_var,
                value=value
            ).pack(side=tk.LEFT, padx=2)
        row += 1

        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Добавить", command=self.add_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Обновить", command=self.update_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Очистить", command=self.clear_form).pack(side=tk.LEFT, padx=2)

    def create_table_panel(self, parent):
        """Создание панели с таблицей и информацией."""
        # Верхняя часть - таблица
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Таблица проектов
        columns = ('ID', 'Название', 'Статус', 'Дата начала', 'Дата окончания', 'Прогресс')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)

        # Настройка колонок
        self.tree.heading('ID', text='ID')
        self.tree.heading('Название', text='Название')
        self.tree.heading('Статус', text='Статус')
        self.tree.heading('Дата начала', text='Дата начала')
        self.tree.heading('Дата окончания', text='Дата окончания')
        self.tree.heading('Прогресс', text='Прогресс')

        self.tree.column('ID', width=50)
        self.tree.column('Название', width=200)
        self.tree.column('Статус', width=100)
        self.tree.column('Дата начала', width=100)
        self.tree.column('Дата окончания', width=100)
        self.tree.column('Прогресс', width=80)

        # Скроллбар
        ##scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        ##self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ##scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Привязка событий
        self.tree.bind('<<TreeviewSelect>>', self.on_project_select)

        # Кнопки действий для проектов
        action_frame = ttk.Frame(table_frame)
        action_frame.pack(fill=tk.X, pady=5)

        ttk.Button(action_frame, text="Удалить", command=self.delete_project).pack(side=tk.TOP, padx=2, pady=2)
        ttk.Button(action_frame, text="Завершить", command=self.complete_project).pack(side=tk.TOP, padx=2, pady=2)
        ttk.Button(action_frame, text="Активировать", command=self.activate_project).pack(side=tk.TOP, padx=2, pady=2)
        ttk.Button(action_frame, text="Приостановить", command=self.hold_project).pack(side=tk.TOP, padx=2, pady=2)
        ttk.Button(action_frame, text="Обновить", command=self.refresh).pack(side=tk.TOP, padx=2, pady=2)

        # Нижняя часть - информация о проекте и задачи
        info_frame = ttk.LabelFrame(parent, text="Информация о проекте", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Информация о прогрессе
        self.progress_frame = ttk.Frame(info_frame)
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(self.progress_frame, text="Прогресс выполнения:").pack(side=tk.LEFT)
        self.progress_bar = ttk.Progressbar(self.progress_frame, length=200, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, padx=10)
        self.progress_label = ttk.Label(self.progress_frame, text="0%")
        self.progress_label.pack(side=tk.LEFT)

        # Таблица задач проекта
        tasks_label = ttk.Label(info_frame, text="Задачи проекта:", font=('Arial', 10, 'bold'))
        tasks_label.pack(anchor=tk.W, pady=(0, 5))

        # Таблица задач
        columns = ('ID', 'Название', 'Статус', 'Приоритет', 'Срок', 'Исполнитель')
        self.tasks_tree = ttk.Treeview(info_frame, columns=columns, show='headings', height=5)

        self.tasks_tree.heading('ID', text='ID')
        self.tasks_tree.heading('Название', text='Название')
        self.tasks_tree.heading('Статус', text='Статус')
        self.tasks_tree.heading('Приоритет', text='Приоритет')
        self.tasks_tree.heading('Срок', text='Срок')
        self.tasks_tree.heading('Исполнитель', text='Исполнитель')

        self.tasks_tree.column('ID', width=50)
        self.tasks_tree.column('Название', width=150)
        self.tasks_tree.column('Статус', width=80)
        self.tasks_tree.column('Приоритет', width=70)
        self.tasks_tree.column('Срок', width=90)
        self.tasks_tree.column('Исполнитель', width=100)

        # Скроллбар для задач
        tasks_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.tasks_tree.yview)
        self.tasks_tree.configure(yscrollcommand=tasks_scrollbar.set)

        self.tasks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tasks_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def add_project(self):
        """Добавление нового проекта."""
        try:
            # Получение данных из формы
            name = self.name_var.get().strip()
            description = self.description_var.get().strip()

            # Обработка дат
            start_date_str = self.start_date_var.get().strip()
            end_date_str = self.end_date_var.get().strip()

            if not name:
                self.main_window.show_error("Название проекта не может быть пустым")
                return

            if not start_date_str or not end_date_str:
                self.main_window.show_error("Укажите даты начала и окончания")
                return

            try:
                start_date = datetime.fromisoformat(start_date_str)
                end_date = datetime.fromisoformat(end_date_str)
            except ValueError:
                self.main_window.show_error("Неверный формат даты. Используйте ГГГГ-ММ-ДД")
                return

            # Добавление проекта
            project_id = self.project_controller.add_project(
                name, description, start_date, end_date
            )

            self.main_window.show_info(f"Проект добавлен с ID: {project_id}")
            self.clear_form()
            self.refresh()

        except Exception as e:
            self.main_window.show_error(f"Ошибка при добавлении проекта: {str(e)}")

    def update_project(self):
        """Обновление существующего проекта."""
        if not self.project_id:
            self.main_window.show_error("Выберите проект для обновления")
            return

        try:
            # Подготовка данных для обновления
            data = {}

            name = self.name_var.get().strip()
            if name:
                data['name'] = name

            description = self.description_var.get().strip()
            if description:
                data['description'] = description

            start_date_str = self.start_date_var.get().strip()
            if start_date_str:
                try:
                    data['start_date'] = datetime.fromisoformat(start_date_str)
                except ValueError:
                    self.main_window.show_error("Неверный формат даты начала")
                    return

            end_date_str = self.end_date_var.get().strip()
            if end_date_str:
                try:
                    data['end_date'] = datetime.fromisoformat(end_date_str)
                except ValueError:
                    self.main_window.show_error("Неверный формат даты окончания")
                    return

            status = self.status_var.get()
            if status:
                data['status'] = status

            if not data:
                self.main_window.show_error("Нет данных для обновления")
                return

            # Обновление проекта
            result = self.project_controller.update_project(self.project_id, **data)

            if result:
                self.main_window.show_info("Проект обновлен")
                self.clear_form()
                self.refresh()
            else:
                self.main_window.show_error("Проект не найден")

        except Exception as e:
            self.main_window.show_error(f"Ошибка при обновлении проекта: {str(e)}")

    def delete_project(self):
        """Удаление выбранного проекта."""
        selected = self.tree.selection()
        if not selected:
            self.main_window.show_error("Выберите проект для удаления")
            return

        project_id = self.tree.item(selected[0])['values'][0]

        if self.main_window.confirm(f"Удалить проект {project_id}? Будут удалены все связанные задачи!"):
            try:
                result = self.project_controller.delete_project(project_id)
                if result:
                    self.main_window.show_info("Проект удален")
                    self.clear_form()
                    self.refresh()
                else:
                    self.main_window.show_error("Проект не найден")
            except Exception as e:
                self.main_window.show_error(f"Ошибка при удалении: {str(e)}")

    def complete_project(self):
        """Завершение выбранного проекта."""
        selected = self.tree.selection()
        if not selected:
            self.main_window.show_error("Выберите проект")
            return

        project_id = self.tree.item(selected[0])['values'][0]

        try:
            result = self.project_controller.update_project_status(project_id, 'completed')
            if result:
                self.main_window.show_info("Проект завершен")
                self.refresh()
            else:
                self.main_window.show_error("Проект не найден")
        except Exception as e:
            self.main_window.show_error(f"Ошибка: {str(e)}")

    def activate_project(self):
        """Активация проекта."""
        selected = self.tree.selection()
        if not selected:
            self.main_window.show_error("Выберите проект")
            return

        project_id = self.tree.item(selected[0])['values'][0]

        try:
            result = self.project_controller.update_project_status(project_id, 'active')
            if result:
                self.main_window.show_info("Проект активирован")
                self.refresh()
            else:
                self.main_window.show_error("Проект не найден")
        except Exception as e:
            self.main_window.show_error(f"Ошибка: {str(e)}")

    def hold_project(self):
        """Приостановка проекта."""
        selected = self.tree.selection()
        if not selected:
            self.main_window.show_error("Выберите проект")
            return

        project_id = self.tree.item(selected[0])['values'][0]

        try:
            result = self.project_controller.update_project_status(project_id, 'on_hold')
            if result:
                self.main_window.show_info("Проект приостановлен")
                self.refresh()
            else:
                self.main_window.show_error("Проект не найден")
        except Exception as e:
            self.main_window.show_error(f"Ошибка: {str(e)}")

    def on_project_select(self, event):
        """Обработка выбора проекта в таблице."""
        selected = self.tree.selection()
        if not selected:
            return

        # Получение данных проекта
        values = self.tree.item(selected[0])['values']
        self.project_id = values[0]

        # Загрузка полной информации о проекте
        try:
            project = self.project_controller.get_project(self.project_id)
            if project:
                # Заполнение формы
                self.name_var.set(project.name)
                self.description_var.set(project.description)
                if project.start_date:
                    self.start_date_var.set(project.start_date.strftime("%Y-%m-%d"))
                if project.end_date:
                    self.end_date_var.set(project.end_date.strftime("%Y-%m-%d"))
                self.status_var.set(project.status)

                # Обновление прогресса
                progress = project.get_progress()
                self.progress_bar['value'] = progress
                self.progress_label.config(text=f"{progress:.1f}%")

                # Загрузка задач проекта
                self.load_project_tasks(self.project_id)

        except Exception as e:
            self.main_window.show_error(f"Ошибка загрузки проекта: {str(e)}")

    def load_project_tasks(self, project_id):
        """Загрузка задач проекта."""
        try:
            # Получаем контроллер задач через главное окно
            tasks = self.main_window.task_controller.get_tasks_by_project(project_id)

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

            for task in tasks:
                due_date = task.due_date.strftime("%Y-%m-%d") if task.due_date else ""

                self.tasks_tree.insert('', tk.END, values=(
                    task.id,
                    task.title,
                    status_map.get(task.status, task.status),
                    priority_map.get(task.priority, task.priority),
                    due_date,
                    f"ID:{task.assignee_id}"
                ))

        except Exception as e:
            self.main_window.show_error(f"Ошибка загрузки задач: {str(e)}")

    def refresh(self):
        """Обновление списка проектов."""
        try:
            projects = self.project_controller.get_all_projects()
            self.display_projects(projects)

        except Exception as e:
            self.main_window.show_error(f"Ошибка загрузки проектов: {str(e)}")

    def display_projects(self, projects):
        """Отображение проектов в таблице."""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Очистка таблицы задач
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)

        # Сброс прогресс-бара
        self.progress_bar['value'] = 0
        self.progress_label.config(text="0%")

        # Заполнение таблицы
        status_map = {
            "active": "Активный",
            "completed": "Завершен",
            "on_hold": "Приостановлен"
        }

        for project in projects:
            progress = project.get_progress()

            self.tree.insert('', tk.END, values=(
                project.id,
                project.name,
                status_map.get(project.status, project.status),
                project.start_date.strftime("%Y-%m-%d") if project.start_date else "",
                project.end_date.strftime("%Y-%m-%d") if project.end_date else "",
                f"{progress:.1f}%"
            ))

    def clear_form(self):
        """Очистка формы."""
        self.project_id = None
        self.name_var.set("")
        self.description_var.set("")
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.status_var.set("active")

        # Очистка таблицы задач и прогресса
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="0%")
