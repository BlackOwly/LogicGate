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

class InputItem(QLabel):
    def __init__(self, input_type, display_name):
        super().__init__()
        self.input_type = input_type
        self.display_name = display_name
        
        # Создаем виджет с текстом
        self.setText(display_name)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            border: 1px solid #4CAF50; 
            margin: 3px; 
            padding: 5px;
            background-color: #E8F5E8;
            border-radius: 5px;
        """)
        self.setFixedSize(120, 40)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.startDrag()
    
    def startDrag(self):
        mime_data = QMimeData()
        mime_data.setText(self.input_type)
        
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        
        pixmap = QPixmap(self.size())
        painter = QPainter(pixmap)
        painter.drawPixmap(self.rect(), self.grab())
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(self.rect().center())
        
        drag.exec_(Qt.CopyAction)



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
        # ВХОДНЫЕ/ВЫХОДНЫЕ ЭЛЕМЕНТЫ
        separator = QLabel("─────")
        separator.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(separator)

        input_label = QLabel("Входы/Выходы")
        input_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(input_label)

        # ТОЛЬКО ОДИН INPUT и ОДИН OUTPUT
        input_types = ['INPUT', 'OUTPUT']
        input_names = ['Вход X', 'Выход Y']

        for i, input_type in enumerate(input_types):
            input_item = InputItem(input_type, input_names[i])
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
