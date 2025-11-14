from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QFont
import os
import sys

# ПЕРЕНОСИМЫЙ ПУТЬ
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from logic.gates import LogicGate
from utils.config import Config
class CircuitWidget(QWidget):
    circuit_changed = pyqtSignal()
    
    def __init__(self, circuit):
        super().__init__()
        self.circuit = circuit
        self.dragging_gate = None
        self.dragging_offset = QPoint()
        self.wire_start = None
        self.wire_start_gate = None
        self.wire_is_output = None
        self.selected_gate = None
        self.hovered_gate = None
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)  # Виджет может получать фокус
        self.setFocus()  # Устанавливаем фокус на этот виджет
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        gate_type = event.mimeData().text()
        position = event.pos() - QPoint(Config.GATE_SIZE//2, Config.GATE_SIZE//2)
        
        gate = self.circuit.add_gate(gate_type, position.x(), position.y())
        
        if gate_type == 'INVERTOR':
            gate.inputs = [False]
        else:
            gate.inputs = [False, False]
            
        gate.output = False
        
        self.circuit_changed.emit()
        self.update()
        event.acceptProposedAction()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        self.draw_grid(painter)
        self.draw_wires(painter)
        self.draw_gates(painter)
        
        # Рисуем провод который сейчас рисуем
        if self.wire_start:
            painter.setPen(QPen(QColor(Config.WIRE_HOVER_COLOR), Config.WIRE_THICKNESS))
            painter.drawLine(self.wire_start, self.last_mouse_pos)
    
    def draw_grid(self, painter):
        painter.setPen(QPen(QColor(Config.GRID_COLOR), 1, Qt.DotLine))
        grid_size = 20
        for x in range(0, self.width(), grid_size):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), grid_size):
            painter.drawLine(0, y, self.width(), y)
    
    def draw_gates(self, painter):
        for gate in self.circuit.gates:
            self.draw_gate(painter, gate)
    
    def draw_gate(self, painter, gate):
        x, y = gate.position
        size = Config.GATE_SIZE
        
        # УСТАНАВЛИВАЕМ БЕЛЫЙ ФОН для вентиля
        painter.setBrush(Qt.white)  # ← ДОБАВЬ ЭТУ СТРОКУ
        
        # Выделяем ТОЛЬКО выбранный вентиль
        if gate == self.selected_gate:
            painter.setPen(QPen(QColor(Config.GATE_SELECTED_COLOR), 3))
        else:
            painter.setPen(QPen(QColor(Config.GATE_BORDER_COLOR), 1))
        
        # Рисуем прямоугольник вентиля с заливкой
        painter.drawRect(x, y, size, size)
        
        # УСТАНАВЛИВАЕМ ЧЕРНЫЙ ЦВЕТ ДЛЯ ТЕКСТА
        painter.setPen(QPen(Qt.black))  # ← ДОБАВЬ ЭТУ СТРОКУ
        
        # ДЛЯ INPUT/OUTPUT ЭЛЕМЕНТОВ - используем ТЕКСТ
        if gate.gate_type == 'INPUT':
            painter.drawText(x, y, size, size, Qt.AlignCenter, f"In\n{gate.name}")
        elif gate.gate_type == 'OUTPUT':
            painter.drawText(x, y, size, size, Qt.AlignCenter, "Out")
        else:
            # Для обычных вентилей пытаемся загрузить иконку
            icon_path = Config.get_icon_path(gate.gate_type)
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                pixmap = pixmap.scaled(size-10, size-10, Qt.KeepAspectRatio)
                painter.drawPixmap(x+5, y+5, pixmap)
            else:
                # Если иконки нет, рисуем текст
                painter.drawText(x, y, size, size, Qt.AlignCenter, gate.gate_type)
        
        # СБРАСЫВАЕМ ЗАЛИВКУ для кружков
        painter.setBrush(Qt.NoBrush)  # ← ДОБАВЬ ЭТУ СТРОКУ
        
        # Рисуем входы/выходы в зависимости от типа вентиля
        if gate.gate_type == 'INPUT':
            # У входного элемента только ВЫХОД (справа)
            output_x = x + size
            output_y = y + size // 2
            painter.setBrush(Qt.black)  # Черная заливка для кружков
            painter.drawEllipse(output_x-3, output_y-3, 6, 6)
            
        elif gate.gate_type == 'OUTPUT':
            # У выходного элемента только ВХОД (слева)
            input_x = x
            input_y = y + size // 2
            painter.setBrush(Qt.black)  # Черная заливка для кружков
            painter.drawEllipse(input_x-3, input_y-3, 6, 6)
            
        else:
            # Обычные вентили - входы слева, выход справа
            input_count = 1 if gate.gate_type == 'INVERTOR' else 2
            for i in range(input_count):
                input_x = x
                input_y = y + (i+1) * size // (input_count+1)
                painter.setBrush(Qt.black)  # Черная заливка для кружков
                painter.drawEllipse(input_x-3, input_y-3, 6, 6)
            
            output_x = x + size
            output_y = y + size // 2
            painter.setBrush(Qt.black)  # Черная заливка для кружков
            painter.drawEllipse(output_x-3, output_y-3, 6, 6)
    def draw_wires(self, painter):
        """Рисуем все соединения между вентилями"""
        painter.setPen(QPen(QColor(Config.WIRE_COLOR), Config.WIRE_THICKNESS))
        
        for source_gate, target_gate, input_index in self.circuit.connections:
            # Координаты выхода source_gate
            source_x = source_gate.position[0] + Config.GATE_SIZE
            source_y = source_gate.position[1] + Config.GATE_SIZE // 2
            
            # Координаты входа target_gate
            target_x = target_gate.position[0]
            input_count = 1 if target_gate.gate_type == 'INVERTOR' else 2
            target_y = target_gate.position[1] + (input_index+1) * Config.GATE_SIZE // (input_count+1)
            
            # Рисуем провод с изгибом
            mid_x = (source_x + target_x) // 2
            painter.drawLine(source_x, source_y, mid_x, source_y)  # Горизонталь от выхода
            painter.drawLine(mid_x, source_y, mid_x, target_y)     # Вертикаль
            painter.drawLine(mid_x, target_y, target_x, target_y)  # Горизонталь ко входу

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            gate = self.get_gate_at_position(pos)
            
            if gate:
                # Проверяем клик по выходу (правый кружок)
                output_x = gate.position[0] + Config.GATE_SIZE
                output_y = gate.position[1] + Config.GATE_SIZE // 2
                output_rect = QRect(output_x-8, output_y-8, 16, 16)
                
                if output_rect.contains(pos):
                    # Начинаем рисовать провод от выхода
                    self.wire_start = QPoint(output_x, output_y)
                    self.wire_start_gate = gate
                    self.wire_is_output = True
                    return
                
                # Проверяем клик по входам (левые кружки)
                input_count = 1 if gate.gate_type == 'INVERTOR' else 2
                for i in range(input_count):
                    input_x = gate.position[0]
                    input_y = gate.position[1] + (i+1) * Config.GATE_SIZE // (input_count+1)
                    input_rect = QRect(input_x-8, input_y-8, 16, 16)
                    
                    if input_rect.contains(pos):
                        # Начинаем рисовать провод от входа
                        self.wire_start = QPoint(input_x, input_y)
                        self.wire_start_gate = gate
                        self.wire_is_output = False
                        self.wire_input_index = i
                        return
                
                # Клик по самому вентилю - выбираем его
                self.selected_gate = gate
                self.dragging_gate = gate
                self.dragging_offset = pos - QPoint(*gate.position)
            
            else:
                # КЛИК ПО ПУСТОМУ МЕСТУ - сбрасываем выбор вентиля
                self.selected_gate = None
            
            self.update()    
    def mouseMoveEvent(self, event):
        self.last_mouse_pos = event.pos()
        
        if self.dragging_gate:
            # Перемещаем вентиль
            new_pos = event.pos() - self.dragging_offset
            self.dragging_gate.position = (new_pos.x(), new_pos.y())
            self.circuit_changed.emit()
            self.update()
        elif self.wire_start:
            # Обновляем рисование провода
            self.update()
    
    def mouseReleaseEvent(self, event):
        if self.wire_start:
            # Завершаем рисование провода
            pos = event.pos()
            target_gate = self.get_gate_at_position(pos)
            
            if target_gate and target_gate != self.wire_start_gate:
                if self.wire_is_output:
                    # Соединяем выход с входом
                    input_count = 1 if target_gate.gate_type == 'INVERTOR' else 2
                    # Находим ближайший вход
                    closest_input = 0
                    min_distance = float('inf')
                    for i in range(input_count):
                        input_y = target_gate.position[1] + (i+1) * Config.GATE_SIZE // (input_count+1)
                        distance = abs(pos.y() - input_y)
                        if distance < min_distance:
                            min_distance = distance
                            closest_input = i
                    
                    self.circuit.connect_gates(self.wire_start_gate, target_gate, closest_input)
                    self.circuit_changed.emit()
            
            self.wire_start = None
            self.wire_start_gate = None
            self.update()
        
        self.dragging_gate = None
    
    def get_gate_at_position(self, pos):
        for gate in self.circuit.gates:
            x, y = gate.position
            size = Config.GATE_SIZE
            if (x <= pos.x() <= x + size and 
                y <= pos.y() <= y + size):
                return gate
        return None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete and self.selected_gate:
            # Удаляем выбранный вентиль
            self.circuit.gates.remove(self.selected_gate)
            # Удаляем все соединения с этим вентилем
            self.circuit.connections = [
                conn for conn in self.circuit.connections 
                if conn[0] != self.selected_gate and conn[1] != self.selected_gate
            ]
            self.selected_gate = None
            self.circuit_changed.emit()
            self.update()
