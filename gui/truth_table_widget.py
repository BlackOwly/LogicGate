from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel)
from PyQt5.QtCore import Qt

class TruthTableWidget(QWidget):
    def __init__(self, circuit):
        super().__init__()
        self.circuit = circuit
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Таблица истинности")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.update_table()
    
    def update_table(self):
        # TODO: Здесь будет логика генерации таблицы истинности
        # на основе количества входов в схеме
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        
        # Заглушка - показываем сообщение
        self.table.setRowCount(1)
        self.table.setColumnCount(1)
        self.table.setItem(0, 0, QTableWidgetItem("Таблица будет обновлена после добавления входов"))
