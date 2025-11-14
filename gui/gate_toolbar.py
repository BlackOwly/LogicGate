from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPixmap, QDrag, QPainter
from utils.config import Config
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPixmap, QDrag, QPainter
import os
import sys

# ДОБАВЬ ЭТО - переносимый путь
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.config import Config


class GateToolbar(QWidget):
    def __init__(self, circuit):
        super().__init__()
        self.circuit = circuit
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Логические вентили")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Область прокрутки для иконок
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Добавляем все иконки вентилей
        gate_types = ['AND', 'OR', 'NAND', 'NOR', 'XOR', 'XNOR', 'INVERTOR']
        
        for gate_type in gate_types:
            gate_item = GateItem(gate_type)
            scroll_layout.addWidget(gate_item)
        # ДОБАВЬ ЭТО - разделитель и входные элементы
        separator = QLabel("Входы/Выходы")
        separator.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(separator)
        
        # Создаем входные элементы (X, Y, Z, W)
        input_items = ['INPUT_X', 'INPUT_Y', 'INPUT_Z', 'INPUT_W', 'OUTPUT']
        for input_type in input_items:
            input_item = GateItem(input_type)
            scroll_layout.addWidget(input_item)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
        self.setFixedWidth(120)


class GateItem(QLabel):
    def __init__(self, gate_type):
        super().__init__()
        self.gate_type = gate_type
        
        # Загружаем иконку
        icon_path = Config.get_icon_path(gate_type)
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio))
        else:
            self.setText(gate_type)  # Fallback если иконки нет
        
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid gray; margin: 5px; padding: 5px;")
        self.setFixedSize(80, 80)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.startDrag()
    
    def startDrag(self):
        # Создаем данные для перетаскивания
        mime_data = QMimeData()
        mime_data.setText(self.gate_type)
        
        # Создаем drag объект
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        
        # Создаем изображение для перетаскивания
        pixmap = QPixmap(self.size())
        painter = QPainter(pixmap)
        painter.drawPixmap(self.rect(), self.grab())
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(self.rect().center())
        
        # Запускаем перетаскивание
        drag.exec_(Qt.CopyAction)
