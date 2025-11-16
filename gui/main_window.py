from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QSplitter, QToolBar, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os
import sys

# ПЕРЕНОСИМЫЙ ПУТЬ
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from circuit_widget import CircuitWidget
from gate_toolbar import GateToolbar
from truth_table_widget import TruthTableWidget
from utils.config import Config

class MainWindow(QMainWindow):
    def __init__(self, circuit):
        super().__init__()
        self.circuit = circuit
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Logic Gate Simulator")
        self.setGeometry(100, 100, Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        
        # Создаем меню
        self.create_menu()
        
        # Главный виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Основной layout
        main_layout = QHBoxLayout(main_widget)
        
        # Разделитель
        splitter = QSplitter(Qt.Horizontal)
        
        # 1. Панель с вентилями (слева) - СДЕЛАЕМ РЕГУЛИРУЕМОЙ
        self.gate_toolbar = GateToolbar(self.circuit)
        splitter.addWidget(self.gate_toolbar)
        
        # 2. Область схемы (центр)
        self.circuit_widget = CircuitWidget(self.circuit)
        splitter.addWidget(self.circuit_widget)
        
        # 3. Таблица истинности (справа)
        self.truth_table = TruthTableWidget(self.circuit)
        splitter.addWidget(self.truth_table)
        
        # УСТАНАВЛИВАЕМ МИНИМАЛЬНЫЕ И НАЧАЛЬНЫЕ РАЗМЕРЫ
        splitter.setSizes([200, 700, 350])
        splitter.setCollapsible(0, False)  # Нельзя полностью скрыть панель вентилей
        splitter.setHandleWidth(8)  # Шире ручку для удобства
        
        main_layout.addWidget(splitter)
        
        # Соединяем сигналы
        self.circuit_widget.circuit_changed.connect(self.truth_table.update_table)

    def create_menu(self):
        menubar = self.menuBar()
        
        # Меню File
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_circuit)
        file_menu.addAction(new_action)
        
        # Меню Help
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def new_circuit(self):
        self.circuit.clear()
        self.circuit_widget.update()
        self.truth_table.update_table()
    
    def show_about(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(self, "About", "Logic Gate Simulator\n\nDrag and drop gates to create circuits!")
