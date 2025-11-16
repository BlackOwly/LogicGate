from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPixmap, QDrag, QPainter
import os
import sys

# Добавляем путь для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.config import Config

class GateItem(QLabel):
    def __init__(self, gate_type):
        super().__init__()
        self.gate_type = gate_type
        
        # Загружаем иконку
        icon_path = Config.get_icon_path(gate_type)
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.setPixmap(pixmap.scaled(70, 70, Qt.KeepAspectRatio))
        else:
            # Для INPUT/OUTPUT используем текст
            if gate_type == 'INPUT':
                self.setText("ВХОД")
            elif gate_type == 'OUTPUT':
                self.setText("ВЫХОД")
            else:
                self.setText(gate_type)
        
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            border: 2px solid #ccc; 
            border-radius: 8px;
            margin: 5px; 
            padding: 8px;
            background-color: white;
        """)
        self.setFixedSize(150, 80)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.startDrag()
    
    def startDrag(self):
        mime_data = QMimeData()
        mime_data.setText(self.gate_type)
        
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
        
        title = QLabel("Логические вентили")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 12pt; margin: 10px;")
        layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # ОСНОВНЫЕ ВЕНТИЛИ
        gate_types = ['AND', 'OR', 'NAND', 'NOR', 'XOR', 'XNOR', 'INVERTOR']
        for gate_type in gate_types:
            gate_item = GateItem(gate_type)
            scroll_layout.addWidget(gate_item)
        
        # РАЗДЕЛИТЕЛЬ И ВХОДЫ/ВЫХОДЫ
        separator = QLabel("────────────")
        separator.setAlignment(Qt.AlignCenter)
        separator.setStyleSheet("margin: 10px 5px; color: #666;")
        scroll_layout.addWidget(separator)
        
        input_label = QLabel("Входы / Выходы")
        input_label.setAlignment(Qt.AlignCenter)
        input_label.setStyleSheet("font-weight: bold; margin: 5px;")
        scroll_layout.addWidget(input_label)
        
        # ВХОДНЫЕ/ВЫХОДНЫЕ ЭЛЕМЕНТЫ
        input_types = ['INPUT', 'OUTPUT']
        input_names = ['Вход X', 'Выход Y']
        
        for i, input_type in enumerate(input_types):
            input_item = GateItem(input_type)
            label = QLabel(input_names[i])
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 9pt; margin: 2px;")
            scroll_layout.addWidget(input_item)
            scroll_layout.addWidget(label)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # УВЕЛИЧИМ ШИРИНУ ПАНЕЛИ
        self.setLayout(layout)
        self.setMinimumWidth(180)
        self.setMaximumWidth(400)  
        self.setFixedWidth(200)
