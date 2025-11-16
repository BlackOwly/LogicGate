from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QPushButton)
from PyQt5.QtCore import Qt, QTimer
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from logic.simulator import Simulator

class TruthTableWidget(QWidget):
    def __init__(self, circuit):
        super().__init__()
        self.circuit = circuit
        self.simulator = Simulator(circuit)
        
        # ДОБАВИМ ТАЙМЕР ДЛЯ ОТЛОЖЕННОГО ОБНОВЛЕНИЯ
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._update_table_delayed)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Таблица истинности")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 12pt; margin: 10px;")
        layout.addWidget(title)
        
        # Кнопка для обновления таблицы
        self.update_btn = QPushButton("Обновить таблицу")
        self.update_btn.clicked.connect(self.update_table)
        self.update_btn.setStyleSheet("margin: 5px; padding: 8px;")
        layout.addWidget(self.update_btn)
        
        # Индикатор вычислений
        self.status_label = QLabel("Готово")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: green; margin: 5px;")
        layout.addWidget(self.status_label)
        
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
        # Первоначальное обновление с задержкой
        QTimer.singleShot(1000, self.update_table)
    
    def update_table(self):
        """Запускает обновление таблицы с задержкой"""
        self.status_label.setText("⏳ Вычисляется...")
        self.status_label.setStyleSheet("color: orange; margin: 5px;")
        
        # Останавливаем предыдущий таймер и запускаем новый с задержкой
        self.update_timer.stop()
        self.update_timer.start(500)  # 500ms задержка
    
    def _update_table_delayed(self):
        """Фактическое обновление таблицы после задержки"""
        try:
            input_combinations, truth_table = self.simulator.generate_truth_table()
            
            if not truth_table:
                self.table.setRowCount(1)
                self.table.setColumnCount(1)
                self.table.setItem(0, 0, QTableWidgetItem("Добавьте входы и выходы в схему"))
                self.status_label.setText("⚠️ Нет входов/выходов")
                self.status_label.setStyleSheet("color: gray; margin: 5px;")
                return
            
            # Настраиваем таблицу
            input_gates = [gate for gate in self.circuit.gates if gate.gate_type == 'INPUT']
            input_gates.sort(key=lambda gate: gate.name)
            output_gates = [gate for gate in self.circuit.gates if gate.gate_type == 'OUTPUT']
            output_gates.sort(key=lambda gate: gate.name)
            
            n_inputs = len(input_gates)
            n_outputs = len(output_gates)
            
            self.table.setRowCount(len(truth_table))
            self.table.setColumnCount(n_inputs + n_outputs)
            
            # Заголовки столбцов
            headers = []
            for i in range(n_inputs):
                headers.append(f"Вход {input_gates[i].name}")
            for i in range(n_outputs):
                headers.append(f"Выход {output_gates[i].name}")
            
            self.table.setHorizontalHeaderLabels(headers)
            
            # Заполняем данными
            for row, (inputs, outputs) in enumerate(truth_table):
                for col in range(n_inputs):
                    value = "1" if inputs[col] else "0"
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, item)
                
                for col in range(n_outputs):
                    value = "1" if outputs[col] else "0"
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignCenter)
                    # Подсветим выходные значения
                    if outputs[col]:
                        item.setBackground(Qt.green)
                    else:
                        item.setBackground(Qt.red)
                    self.table.setItem(row, col + n_inputs, item)
            
            self.status_label.setText("✅ Готово")
            self.status_label.setStyleSheet("color: green; margin: 5px;")
            
        except Exception as e:
            self.status_label.setText("❌ Ошибка вычислений")
            self.status_label.setStyleSheet("color: red; margin: 5px;")
            print(f"Ошибка при обновлении таблицы: {e}")
