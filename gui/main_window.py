from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QSplitter, QToolBar, QAction, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from circuit_widget import CircuitWidget
from gate_toolbar import GateToolbar
from truth_table_widget import TruthTableWidget
from utils.config import Config
from utils.serializer import ProjectSerializer

class MainWindow(QMainWindow):
    def __init__(self, circuit):
        super().__init__()
        self.circuit = circuit
        self.current_file = None  # Текущий открытый файл
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Logic Gate Simulator")
        self.setGeometry(100, 100, Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        
        # Создаем меню
        self.create_menu()
        
        # Создаем тулбар
        self.create_toolbar()
        
        # Главный виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Основной layout
        main_layout = QHBoxLayout(main_widget)
        
        # Разделитель
        splitter = QSplitter(Qt.Horizontal)
        
        # 1. Панель с вентилями (слева)
        self.gate_toolbar = GateToolbar(self.circuit)
        splitter.addWidget(self.gate_toolbar)
        
        # 2. Область схемы (центр)
        self.circuit_widget = CircuitWidget(self.circuit)
        splitter.addWidget(self.circuit_widget)
        
        # 3. Таблица истинности (справа)
        self.truth_table = TruthTableWidget(self.circuit)
        splitter.addWidget(self.truth_table)
        
        # Устанавливаем размеры
        splitter.setSizes([250, 800, 400])
        splitter.setCollapsible(0, False)
        splitter.setHandleWidth(10)
        
        main_layout.addWidget(splitter)
        
        # Соединяем сигналы
        self.circuit_widget.circuit_changed.connect(self.truth_table.update_table)
        
        # Статус бар
        self.statusBar().showMessage("Готово")
    
    def create_menu(self):
        """Создает меню приложения"""
        menubar = self.menuBar()
        
        # Меню File
        file_menu = menubar.addMenu('Файл')
        
        # Новый проект
        new_action = QAction('Новый', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        # Открыть
        open_action = QAction('Открыть...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        # Сохранить
        save_action = QAction('Сохранить', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        # Сохранить как
        save_as_action = QAction('Сохранить как...', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Выход
        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Help
        help_menu = menubar.addMenu('Помощь')
        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Создает панель инструментов"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Кнопка Новый
        new_btn = QAction('🆕 Новый', self)
        new_btn.triggered.connect(self.new_project)
        toolbar.addAction(new_btn)
        
        # Кнопка Сохранить
        save_btn = QAction('💾 Сохранить', self)
        save_btn.triggered.connect(self.save_project)
        toolbar.addAction(save_btn)
        
        # Кнопка Открыть
        open_btn = QAction('📂 Открыть', self)
        open_btn.triggered.connect(self.open_project)
        toolbar.addAction(open_btn)
        
        toolbar.addSeparator()
    
    def new_project(self):
        """Создает новый проект"""
        if self.check_unsaved_changes():
            self.circuit.clear()
            self.current_file = None
            self.circuit_widget.update()
            self.truth_table.update_table()
            self.update_title()
            self.statusBar().showMessage("Создан новый проект")
    
    def save_project(self):
        """Сохраняет проект"""
        if self.current_file:
            success = ProjectSerializer.save_project(self.circuit, self.current_file)
            if success:
                self.statusBar().showMessage(f"Проект сохранен: {os.path.basename(self.current_file)}")
            else:
                self.statusBar().showMessage("Ошибка сохранения")
        else:
            self.save_project_as()
    
    def save_project_as(self):
        """Сохраняет проект как новый файл"""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить проект",
            "",
            "Logic Gate Projects (*.lgp);;All Files (*)"
        )
        
        if filepath:
            if not filepath.endswith('.lgp'):
                filepath += '.lgp'
            
            success = ProjectSerializer.save_project(self.circuit, filepath)
            if success:
                self.current_file = filepath
                self.update_title()
                self.statusBar().showMessage(f"Проект сохранен: {os.path.basename(filepath)}")
            else:
                self.statusBar().showMessage("Ошибка сохранения")
    
    def open_project(self):
        """Открывает проект"""
        if self.check_unsaved_changes():
            filepath, _ = QFileDialog.getOpenFileName(
                self,
                "Открыть проект",
                "",
                "Logic Gate Projects (*.lgp);;All Files (*)"
            )
            
            if filepath:
                success = ProjectSerializer.load_project(self.circuit, filepath)
                if success:
                    self.current_file = filepath
                    self.update_title()
                    self.circuit_widget.update()
                    self.truth_table.update_table()
                    self.statusBar().showMessage(f"Проект загружен: {os.path.basename(filepath)}")
                else:
                    self.statusBar().showMessage("Ошибка загрузки")
    
    def check_unsaved_changes(self):
        """Проверяет есть ли несохраненные изменения"""
        # TODO: Реализовать проверку изменений
        return True
    
    def update_title(self):
        """Обновляет заголовок окна"""
        if self.current_file:
            filename = os.path.basename(self.current_file)
            self.setWindowTitle(f"Logic Gate Simulator - {filename}")
        else:
            self.setWindowTitle("Logic Gate Simulator - Новый проект")
    
    def show_about(self):
        """Показывает информацию о программе"""
        QMessageBox.about(self, "О программе", 
                         "Logic Gate Simulator\n\n"
                         "Профессиональный симулятор логических схем\n"
                         "• Создание и редактирование схем\n"
                         "• Автоматическая таблица истинности\n"
                         "• Сохранение и загрузка проектов\n"
                         "• Поддержка всех логических вентилей")
