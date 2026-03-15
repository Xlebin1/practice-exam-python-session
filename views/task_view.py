import tkinter as tk
from tkinter import ttk
from datetime import datetime

# views/task_view.py

class TaskView(ttk.Frame):
    """Представление для управления задачами."""

    def __init__(self, parent, task_controller, project_controller, user_controller) -> None:
        """
        Инициализация представления задач.

        Args:
            parent: Родительский виджет
            task_controller: Контроллер задач
            project_controller: Контроллер проектов
            user_controller: Контроллер пользователей
        """
        super().__init__(parent)

        self.task_controller = task_controller
        self.project_controller = project_controller
        self.user_controller = user_controller
        self.main_window = self.get_main_window()

        # Переменные для формы
        self.task_id = None
        self.title_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.priority_var = tk.StringVar(value="2")
        self.due_date_var = tk.StringVar()
        self.project_id_var = tk.StringVar()
        self.assignee_id_var = tk.StringVar()

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

        # Правая панель - таблица и поиск
        self.create_table_panel(main_frame)

    def create_form_panel(self, parent):
        """Создание панели с формой."""
        form_frame = ttk.LabelFrame(parent, text="Добавление/редактирование задачи", padding=10)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Поля формы
        row = 0

        # Название
        ttk.Label(form_frame, text="Название:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.title_var, width=30).grid(row=row, column=1, pady=5, padx=(5, 0))
        row += 1

        # Описание
        ttk.Label(form_frame, text="Описание:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.description_var, width=30).grid(row=row, column=1, pady=5, padx=(5, 0))
        row += 1

        # Приоритет
        ttk.Label(form_frame, text="Приоритет:").grid(row=row, column=0, sticky=tk.W, pady=5)
        priority_frame = ttk.Frame(form_frame)
        priority_frame.grid(row=row, column=1, pady=5, padx=(5, 0))

        priorities = [("Высокий", "1"), ("Средний", "2"), ("Низкий", "3")]
        for i, (text, value) in enumerate(priorities):
            ttk.Radiobutton(
                priority_frame,
                text=text,
                variable=self.priority_var,
                value=value
            ).pack(side=tk.LEFT, padx=2)
        row += 1

        # Срок выполнения
        ttk.Label(form_frame, text="Срок выполнения:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.due_date_var, width=30).grid(row=row, column=1, pady=5, padx=(5, 0))
        ttk.Label(form_frame, text="ГГГГ-ММ-ДД", font=('Arial', 8)).grid(row=row+1, column=1, sticky=tk.W)
        row += 2

        # Проект
        ttk.Label(form_frame, text="Проект:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.project_combo = ttk.Combobox(form_frame, textvariable=self.project_id_var, width=27)
        self.project_combo.grid(row=row, column=1, pady=5, padx=(5, 0))
        self.load_projects()
        row += 1

        # Исполнитель
        ttk.Label(form_frame, text="Исполнитель:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.user_combo = ttk.Combobox(form_frame, textvariable=self.assignee_id_var, width=27)
        self.user_combo.grid(row=row, column=1, pady=5, padx=(5, 0))
        self.load_users()
        row += 2

        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Добавить", command=self.add_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Обновить", command=self.update_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Очистить", command=self.clear_form).pack(side=tk.LEFT, padx=2)

    def create_table_panel(self, parent):
        """Создание панели с таблицей и поиском."""
        table_frame = ttk.Frame(parent)
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Панель поиска и фильтрации
        filter_frame = ttk.Frame(table_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_tasks())
        ttk.Entry(filter_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="Статус:").pack(side=tk.LEFT, padx=(10, 2))
        self.status_filter_var = tk.StringVar(value="all")
        status_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.status_filter_var,
            values=["all", "pending", "in_progress", "completed"],
            width=15,
            state="readonly"
        )
        status_combo.pack(side=tk.LEFT)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_tasks())

        ttk.Label(filter_frame, text="Приоритет:").pack(side=tk.LEFT, padx=(10, 2))
        self.priority_filter_var = tk.StringVar(value="all")
        priority_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.priority_filter_var,
            values=["all", "1", "2", "3"],
            width=10,
            state="readonly"
        )
        priority_combo.pack(side=tk.LEFT)
        priority_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_tasks())

        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filters).pack(side=tk.LEFT, padx=5)

        # Таблица задач
        columns = ('ID', 'Название', 'Статус', 'Приоритет', 'Срок', 'Проект', 'Исполнитель')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)

        # Настройка колонок
        self.tree.heading('ID', text='ID')
        self.tree.heading('Название', text='Название')
        self.tree.heading('Статус', text='Статус')
        self.tree.heading('Приоритет', text='Приоритет')
        self.tree.heading('Срок', text='Срок')
        self.tree.heading('Проект', text='Проект')
        self.tree.heading('Исполнитель', text='Исполнитель')

        self.tree.column('ID', width=50)
        self.tree.column('Название', width=200)
        self.tree.column('Статус', width=100)
        self.tree.column('Приоритет', width=80)
        self.tree.column('Срок', width=100)
        self.tree.column('Проект', width=100)
        self.tree.column('Исполнитель', width=100)

        # Скроллбар
        ##scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        ##self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ##scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Привязка событий
        self.tree.bind('<<TreeviewSelect>>', self.on_task_select)

        # Кнопки действий
        action_frame = ttk.Frame(table_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(action_frame, text="Завершить", command=self.complete_task).pack(side=tk.TOP, pady=2)
        ttk.Button(action_frame, text="В работу", command=self.start_task).pack(side=tk.TOP, pady=2)
        ttk.Button(action_frame, text="Удалить", command=self.delete_task).pack(side=tk.TOP, pady=2)
        ttk.Button(action_frame, text="Обновить список", command=self.refresh).pack(side=tk.TOP, padx=2, pady=2)

    def load_projects(self):
        """Загрузка проектов в комбобокс."""
        try:
            projects = self.project_controller.get_all_projects()
            self.projects = {p.id: p.name for p in projects}
            self.project_combo['values'] = [f"{p.id}: {p.name}" for p in projects]
        except Exception as e:
            self.main_window.show_error(f"Ошибка загрузки проектов: {str(e)}")

    def load_users(self):
        """Загрузка пользователей в комбобокс."""
        try:
            users = self.user_controller.get_all_users()
            self.users = {u.id: u.username for u in users}
            self.user_combo['values'] = [f"{u.id}: {u.username}" for u in users]
        except Exception as e:
            self.main_window.show_error(f"Ошибка загрузки пользователей: {str(e)}")

    def add_task(self):
        """Добавление новой задачи."""
        try:
            # Получение данных из формы
            title = self.title_var.get().strip()
            description = self.description_var.get().strip()
            priority = int(self.priority_var.get())

            # Обработка даты
            due_date_str = self.due_date_var.get().strip()
            due_date = None
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str)
                except ValueError:
                    self.main_window.show_error("Неверный формат даты. Используйте ГГГГ-ММ-ДД")
                    return

            # Получение ID проекта и исполнителя
            project_id = self.get_id_from_combo(self.project_combo.get())
            assignee_id = self.get_id_from_combo(self.user_combo.get())

            if not title:
                self.main_window.show_error("Название задачи не может быть пустым")
                return

            if not due_date:
                self.main_window.show_error("Укажите срок выполнения")
                return

            # Добавление задачи
            task_id = self.task_controller.add_task(
                title, description, priority, due_date, project_id, assignee_id
            )

            self.main_window.show_info(f"Задача добавлена с ID: {task_id}")
            self.clear_form()
            self.refresh()

        except Exception as e:
            self.main_window.show_error(f"Ошибка при добавлении задачи: {str(e)}")

    def update_task(self):
        """Обновление существующей задачи."""
        if not self.task_id:
            self.main_window.show_error("Выберите задачу для обновления")
            return

        try:
            # Подготовка данных для обновления
            data = {}

            title = self.title_var.get().strip()
            if title:
                data['title'] = title

            description = self.description_var.get().strip()
            if description:
                data['description'] = description

            priority = self.priority_var.get()
            if priority:
                data['priority'] = int(priority)

            due_date_str = self.due_date_var.get().strip()
            if due_date_str:
                try:
                    data['due_date'] = datetime.fromisoformat(due_date_str)
                except ValueError:
                    self.main_window.show_error("Неверный формат даты")
                    return

            project_id = self.get_id_from_combo(self.project_combo.get())
            if project_id:
                data['project_id'] = project_id

            assignee_id = self.get_id_from_combo(self.user_combo.get())
            if assignee_id:
                data['assignee_id'] = assignee_id

            if not data:
                self.main_window.show_error("Нет данных для обновления")
                return

            # Обновление задачи
            result = self.task_controller.update_task(self.task_id, **data)

            if result:
                self.main_window.show_info("Задача обновлена")
                self.clear_form()
                self.refresh()
            else:
                self.main_window.show_error("Задача не найдена")

        except Exception as e:
            self.main_window.show_error(f"Ошибка при обновлении задачи: {str(e)}")

    def delete_task(self):
        """Удаление выбранной задачи."""
        selected = self.tree.selection()
        if not selected:
            self.main_window.show_error("Выберите задачу для удаления")
            return

        task_id = self.tree.item(selected[0])['values'][0]

        if self.main_window.confirm(f"Удалить задачу {task_id}?"):
            try:
                result = self.task_controller.delete_task(task_id)
                if result:
                    self.main_window.show_info("Задача удалена")
                    self.clear_form()
                    self.refresh()
                else:
                    self.main_window.show_error("Задача не найдена")
            except Exception as e:
                self.main_window.show_error(f"Ошибка при удалении: {str(e)}")

    def complete_task(self):
        """Завершение выбранной задачи."""
        selected = self.tree.selection()
        if not selected:
            self.main_window.show_error("Выберите задачу")
            return

        task_id = self.tree.item(selected[0])['values'][0]

        try:
            result = self.task_controller.update_task_status(task_id, 'completed')
            if result:
                self.main_window.show_info("Задача завершена")
                self.refresh()
            else:
                self.main_window.show_error("Задача не найдена")
        except Exception as e:
            self.main_window.show_error(f"Ошибка: {str(e)}")

    def start_task(self):
        """Перевод задачи в статус 'в работе'."""
        selected = self.tree.selection()
        if not selected:
            self.main_window.show_error("Выберите задачу")
            return

        task_id = self.tree.item(selected[0])['values'][0]

        try:
            result = self.task_controller.update_task_status(task_id, 'in_progress')
            if result:
                self.main_window.show_info("Задача переведена в работу")
                self.refresh()
            else:
                self.main_window.show_error("Задача не найдена")
        except Exception as e:
            self.main_window.show_error(f"Ошибка: {str(e)}")

    def on_task_select(self, event):
        """Обработка выбора задачи в таблице."""
        selected = self.tree.selection()
        if not selected:
            return

        # Получение данных задачи
        values = self.tree.item(selected[0])['values']
        self.task_id = values[0]

        # Заполнение формы
        self.title_var.set(values[1])

        # Получение полной задачи для описания
        try:
            task = self.task_controller.get_task(self.task_id)
            if task:
                self.description_var.set(task.description)
                self.priority_var.set(str(task.priority))
                if task.due_date:
                    self.due_date_var.set(task.due_date.strftime("%Y-%m-%d"))

                # Установка проекта
                for item in self.project_combo['values']:
                    if item.startswith(f"{task.project_id}:"):
                        self.project_combo.set(item)
                        break

                # Установка исполнителя
                for item in self.user_combo['values']:
                    if item.startswith(f"{task.assignee_id}:"):
                        self.user_combo.set(item)
                        break
        except Exception as e:
            self.main_window.show_error(f"Ошибка загрузки задачи: {str(e)}")

    def search_tasks(self):
        """Поиск задач по запросу."""
        query = self.search_var.get().strip()
        if query:
            try:
                tasks = self.task_controller.search_tasks(query)
                self.display_tasks(tasks)
            except Exception as e:
                self.main_window.show_error(f"Ошибка поиска: {str(e)}")
        else:
            self.filter_tasks()

    def filter_tasks(self):
        """Фильтрация задач."""
        try:
            all_tasks = self.task_controller.get_all_tasks()

            # Применение фильтров
            status_filter = self.status_filter_var.get()
            priority_filter = self.priority_filter_var.get()

            filtered_tasks = []
            for task in all_tasks:
                if status_filter != 'all' and task.status != status_filter:
                    continue
                if priority_filter != 'all' and str(task.priority) != priority_filter:
                    continue
                filtered_tasks.append(task)

            self.display_tasks(filtered_tasks)

        except Exception as e:
            self.main_window.show_error(f"Ошибка фильтрации: {str(e)}")

    def reset_filters(self):
        """Сброс фильтров."""
        self.search_var.set("")
        self.status_filter_var.set("all")
        self.priority_filter_var.set("all")
        self.refresh()

    def refresh(self):
        """Обновление списка задач."""
        try:
            tasks = self.task_controller.get_all_tasks()
            self.display_tasks(tasks)

            # Обновление проектов и пользователей
            self.load_projects()
            self.load_users()

        except Exception as e:
            self.main_window.show_error(f"Ошибка загрузки задач: {str(e)}")

    def display_tasks(self, tasks):
        """Отображение задач в таблице."""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Заполнение таблицы
        priority_map = {1: "Высокий", 2: "Средний", 3: "Низкий"}
        status_map = {
            "pending": "Ожидание",
            "in_progress": "В работе",
            "completed": "Завершено"
        }

        for task in tasks:
            # Получение названий проекта и исполнителя
            project_name = self.projects.get(task.project_id, f"ID:{task.project_id}")
            user_name = self.users.get(task.assignee_id, f"ID:{task.assignee_id}")

            # Форматирование даты
            due_date = task.due_date.strftime("%Y-%m-%d") if task.due_date else ""

            self.tree.insert('', tk.END, values=(
                task.id,
                task.title,
                status_map.get(task.status, task.status),
                priority_map.get(task.priority, task.priority),
                due_date,
                project_name,
                user_name
            ))

    def clear_form(self):
        """Очистка формы."""
        self.task_id = None
        self.title_var.set("")
        self.description_var.set("")
        self.priority_var.set("2")
        self.due_date_var.set("")
        self.project_combo.set("")
        self.user_combo.set("")

    def get_id_from_combo(self, value):
        """Получение ID из значения комбобокса."""
        if not value:
            return None
        try:
            return int(value.split(':')[0])
        except:
            return None
