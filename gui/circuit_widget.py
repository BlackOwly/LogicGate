from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect, QTimer  # ← ДОБАВЬ QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QFont
import os
import sys

# ... остальной код без изменений ...
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

        # ДОБАВИМ ТАЙМЕР ДЛЯ ОГРАНИЧЕНИЯ СИГНАЛОВ
        self.change_timer = QTimer()
        self.change_timer.setSingleShot(True)
        self.change_timer.timeout.connect(self._emit_circuit_changed)
        self.pending_changes = False
        
        # ДОБАВИМ МАСШТАБИРОВАНИЕ
        self.scale = 1.0
        self.zoom_factor = 1.1
        self.offset = QPoint(0, 0)
        self.panning = False
        self.pan_start_pos = QPoint()
        

        self.last_mouse_pos = QPoint(0, 0)
        
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        gate_type = event.mimeData().text()
        
        # ПРЕОБРАЗУЕМ КООРДИНАТЫ С УЧЕТОМ МАСШТАБА И СМЕЩЕНИЯ
        position = self.transform_pos(event.pos()) - QPoint(Config.GATE_SIZE//2, Config.GATE_SIZE//2)
        
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
        grid_size = 20
        # Учитываем масштаб для размера сетки
        effective_grid_size = grid_size * self.scale
        
        painter.setPen(QPen(QColor(Config.GRID_COLOR), 1, Qt.DotLine))
        
        width = int(self.width() / self.scale) + 100
        height = int(self.height() / self.scale) + 100
        
        for x in range(-50, width, grid_size):
            painter.drawLine(x, -50, x, height)
        for y in range(-50, height, grid_size):
            painter.drawLine(-50, y, width, y)
    
    def draw_gate(self, painter, gate):
        x, y = gate.position
        size = Config.GATE_SIZE
        
        # ВЫДЕЛЯЕМ ТОЛЬКО ВЫБРАННЫЙ ВЕНТИЛЬ
        if gate == self.selected_gate:
            painter.setPen(QPen(QColor(Config.GATE_SELECTED_COLOR), 3))
        else:
            painter.setPen(QPen(QColor(Config.GATE_BORDER_COLOR), 1))
        
        # УСТАНАВЛИВАЕМ БЕЛЫЙ ФОН ТОЛЬКО ДЛЯ INPUT/OUTPUT
        if gate.gate_type in ['INPUT', 'OUTPUT']:
            painter.setBrush(Qt.white)  # Белый фон только для текстовых элементов
        else:
            painter.setBrush(Qt.NoBrush)  # Прозрачный фон для иконок
        
        # Рисуем прямоугольник вентиля с заливкой
        painter.drawRect(x, y, size, size)
        
        # УСТАНАВЛИВАЕМ ЧЕРНЫЙ ЦВЕТ ДЛЯ ТЕКСТА
        painter.setPen(QPen(Qt.black))
        
        # ДЛЯ INPUT/OUTPUT ЭЛЕМЕНТОВ - используем ТЕКСТ
        if gate.gate_type == 'INPUT':
            painter.drawText(x, y, size, size, Qt.AlignCenter, f"In\n{gate.name}")
        elif gate.gate_type == 'OUTPUT':
            painter.drawText(x, y, size, size, Qt.AlignCenter, f"Out\n{gate.name}")  # ← ДОБАВЬ ТЕКСТ ДЛЯ OUTPUT
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
        painter.setBrush(Qt.NoBrush)
        
        # Рисуем входы/выходы в зависимости от типа вентиля
        if gate.gate_type == 'INPUT':
            # У входного элемента только ОДИН ВЫХОД (справа)
            output_x = x + size
            output_y = y + size // 2
            painter.setBrush(Qt.black)  # Черная заливка для кружков
            painter.drawEllipse(output_x-3, output_y-3, 6, 6)
            
        elif gate.gate_type == 'OUTPUT':
            # У выходного элемента только ОДИН ВХОД (слева)
            input_x = x
            input_y = y + size // 2
            painter.setBrush(Qt.black)  # Черная заливка для кружков
            painter.drawEllipse(input_x-3, input_y-3, 6, 6)
            
            # === ДОБАВЬ ЗДЕСЬ ИНДИКАТОР СОЕДИНЕНИЯ ===
            # ПОКАЖЕМ ЕСТЬ ЛИ СОЕДИНЕНИЕ С ЭТИМ OUTPUT
            has_connection = any(conn[1] == gate for conn in self.circuit.connections)
            if has_connection:
                painter.setBrush(QColor(0, 255, 0, 150))
                painter.drawEllipse(input_x-5, input_y-5, 10, 10)
            
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
        """Рисуем все соединения между вентилями с обходом препятствий"""
        painter.setPen(QPen(QColor(Config.WIRE_COLOR), Config.WIRE_THICKNESS))
        
        for source_gate, target_gate, input_index in self.circuit.connections:
            # Координаты выхода source_gate
            source_x = source_gate.position[0] + Config.GATE_SIZE
            source_y = source_gate.position[1] + Config.GATE_SIZE // 2
            
            # Координаты входа target_gate
            target_x = target_gate.position[0]
            input_count = 1 if target_gate.gate_type == 'INVERTOR' else 2
            target_y = target_gate.position[1] + (input_index+1) * Config.GATE_SIZE // (input_count+1)
            
            start_point = QPoint(source_x, source_y)
            end_point = QPoint(target_x, target_y)
            
            # Проверяем есть ли препятствия на прямом пути
            if self.is_path_clear(start_point, end_point, source_gate, target_gate):
                # Прямой путь свободен - рисуем L-образный провод как раньше
                mid_x = (source_x + target_x) // 2
                painter.drawLine(source_x, source_y, mid_x, source_y)
                painter.drawLine(mid_x, source_y, mid_x, target_y)
                painter.drawLine(mid_x, target_y, target_x, target_y)
            else:
                # Путь заблокирован - ищем обходной путь
                path = self.find_wire_path(start_point, end_point, source_gate, target_gate)
                
                # Рисуем путь с углами (только горизонтальные/вертикальные линии)
                for i in range(len(path) - 1):
                    p1 = path[i]
                    p2 = path[i + 1]
                    painter.drawLine(p1, p2)

    def wheelEvent(self, event):
        """Обработка колесика мыши для масштабирования"""
        zoom_in = event.angleDelta().y() > 0
        
        old_scale = self.scale
        if zoom_in:
            self.scale *= self.zoom_factor
        else:
            self.scale /= self.zoom_factor
        
        # Ограничим масштаб
        self.scale = max(0.3, min(3.0, self.scale))
        
        # Корректируем смещение чтобы zoom был к курсору
        mouse_pos = event.pos()
        self.offset = mouse_pos - (mouse_pos - self.offset) * (self.scale / old_scale)
        
        self.update()



    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setFocus()
            pos = event.pos()
            
            # ЕСЛИ УЖЕ ПЕРЕТАСКИВАЕМ ВЕНТИЛЬ - останавливаем
            if self.dragging_gate:
                self.dragging_gate = None
                self.update()
                return
            
            # ПРЕОБРАЗУЕМ КООРДИНАТЫ С УЧЕТОМ МАСШТАБА
            transformed_pos = self.transform_pos(pos)
            gate = self.get_gate_at_position(transformed_pos)
            
            if gate:
                x, y = gate.position
                size = Config.GATE_SIZE
                local_x = transformed_pos.x() - x
                local_y = transformed_pos.y() - y
                
                # ЛЕВЫЙ КЛИК - соединения проводами
                if gate.gate_type == 'INPUT':
                    if local_x > size // 2:
                        output_x = x + size
                        output_y = y + size // 2
                        self.wire_start = QPoint(output_x, output_y)
                        self.wire_start_gate = gate
                        self.wire_is_output = True
                        self.last_mouse_pos = pos
                        return
                        
                elif gate.gate_type == 'OUTPUT':
                    if local_x < size // 2:
                        input_x = x
                        input_y = y + size // 2
                        self.wire_start = QPoint(input_x, input_y)
                        self.wire_start_gate = gate
                        self.wire_is_output = False
                        self.wire_input_index = 0
                        self.last_mouse_pos = pos
                        return
                        
                elif gate.gate_type == 'INVERTOR':
                    if local_x < size // 2:
                        input_x = x
                        input_y = y + size // 2
                        self.wire_start = QPoint(input_x, input_y)
                        self.wire_start_gate = gate
                        self.wire_is_output = False
                        self.wire_input_index = 0
                        self.last_mouse_pos = pos
                        return
                    else:
                        output_x = x + size
                        output_y = y + size // 2
                        self.wire_start = QPoint(output_x, output_y)
                        self.wire_start_gate = gate
                        self.wire_is_output = True
                        self.last_mouse_pos = pos
                        return
                        
                else:
                    if local_x > size // 2:
                        output_x = x + size
                        output_y = y + size // 2
                        self.wire_start = QPoint(output_x, output_y)
                        self.wire_start_gate = gate
                        self.wire_is_output = True
                        self.last_mouse_pos = pos
                        return
                    else:
                        if local_y < size // 2:
                            input_x = x
                            input_y = y + size // 3
                            self.wire_start = QPoint(input_x, input_y)
                            self.wire_start_gate = gate
                            self.wire_is_output = False
                            self.wire_input_index = 0
                            self.last_mouse_pos = pos
                            return
                        else:
                            input_x = x
                            input_y = y + 2 * size // 3
                            self.wire_start = QPoint(input_x, input_y)
                            self.wire_start_gate = gate
                            self.wire_is_output = False
                            self.wire_input_index = 1
                            self.last_mouse_pos = pos
                            return
                
                # Если не попали в зону соединения - начинаем перемещение вентиля
                self.dragging_gate = gate
                self.dragging_offset = transformed_pos - QPoint(*gate.position)
                self.selected_gate = gate
            
            else:
                # КЛИК ПО ПУСТОМУ МЕСТУ - начинаем панорамирование
                self.panning = True
                self.pan_start_pos = pos
                self.selected_gate = None
            
            self.update()
        
        elif event.button() == Qt.RightButton:
            # ПРАВАЯ КНОПКА - начало перемещения вентиля
            transformed_pos = self.transform_pos(event.pos())
            gate = self.get_gate_at_position(transformed_pos)
            
            if gate:
                self.dragging_gate = gate
                self.dragging_offset = transformed_pos - QPoint(*gate.position)
                self.selected_gate = gate
                print(f"Начато перемещение: {gate.gate_type}")
            
            self.update()
    def on_single_click(self):
        """Вызывается когда прошло время двойного клика, но второго клика не было"""
        pos = self.double_click_pos
        gate = self.potential_gate
        
        if gate:
            # ОДИНОЧНЫЙ КЛИК - проверяем зоны соединений
            x, y = gate.position
            size = Config.GATE_SIZE
            local_x = pos.x() - x
            local_y = pos.y() - y
            
            # ТОТ ЖЕ КОД ДЛЯ ЗОН СОЕДИНЕНИЙ, ЧТО БЫЛ РАНЬШЕ
            if gate.gate_type == 'INPUT':
                if local_x > size // 2:
                    output_x = x + size
                    output_y = y + size // 2
                    self.wire_start = QPoint(output_x, output_y)
                    self.wire_start_gate = gate
                    self.wire_is_output = True
                    self.update()
                    return
                    
            elif gate.gate_type == 'OUTPUT':
                if local_x < size // 2:
                    input_x = x
                    input_y = y + size // 2
                    self.wire_start = QPoint(input_x, input_y)
                    self.wire_start_gate = gate
                    self.wire_is_output = False
                    self.wire_input_index = 0
                    self.update()
                    return
                    
            elif gate.gate_type == 'INVERTOR':
                if local_x < size // 2:
                    input_x = x
                    input_y = y + size // 2
                    self.wire_start = QPoint(input_x, input_y)
                    self.wire_start_gate = gate
                    self.wire_is_output = False
                    self.wire_input_index = 0
                    self.update()
                    return
                else:
                    output_x = x + size
                    output_y = y + size // 2
                    self.wire_start = QPoint(output_x, output_y)
                    self.wire_start_gate = gate
                    self.wire_is_output = True
                    self.update()
                    return
                    
            else:
                if local_x > size // 2:
                    output_x = x + size
                    output_y = y + size // 2
                    self.wire_start = QPoint(output_x, output_y)
                    self.wire_start_gate = gate
                    self.wire_is_output = True
                    self.update()
                    return
                else:
                    if local_y < size // 2:
                        input_x = x
                        input_y = y + size // 3
                        self.wire_start = QPoint(input_x, input_y)
                        self.wire_start_gate = gate
                        self.wire_is_output = False
                        self.wire_input_index = 0
                        self.update()
                        return
                    else:
                        input_x = x
                        input_y = y + 2 * size // 3
                        self.wire_start = QPoint(input_x, input_y)
                        self.wire_start_gate = gate
                        self.wire_is_output = False
                        self.wire_input_index = 1
                        self.update()
                        return
        
        # Если не попали в зону соединения - просто выделяем вентиль
        self.selected_gate = gate
        self.update()
    def mouseMoveEvent(self, event):
        self.last_mouse_pos = event.pos()
        
        if self.dragging_gate:
            new_pos = self.transform_pos(event.pos()) - self.dragging_offset
            self.dragging_gate.position = (new_pos.x(), new_pos.y())
            self.schedule_circuit_changed()  # ← вместо circuit_changed.emit()
            self.update()
        elif self.wire_start:
            self.update()
        elif self.panning and event.buttons() & Qt.LeftButton:
            # Панорамирование левой кнопкой
            delta = event.pos() - self.pan_start_pos
            self.offset += delta
            self.pan_start_pos = event.pos()
            self.update()
                    
    def mouseReleaseEvent(self, event):
        if self.wire_start:
            # Завершаем рисование провода
            transformed_pos = self.transform_pos(event.pos())
            target_gate = self.get_gate_at_position(transformed_pos)
            
            if target_gate and target_gate != self.wire_start_gate:
                if self.wire_is_output:
                    # ПРОВЕРЯЕМ ДЛЯ OUTPUT - МОЖЕТ ИМЕТЬ ТОЛЬКО ОДИН ВХОД
                    if target_gate.gate_type == 'OUTPUT':
                        # Если у OUTPUT уже есть соединение - удаляем старое
                        existing_connections = [
                            conn for conn in self.circuit.connections 
                            if conn[1] == target_gate
                        ]
                        for conn in existing_connections:
                            self.circuit.connections.remove(conn)
                            print(f"Удалено старое соединение с выходом {target_gate.name}")
                    
                    # Соединяем выход с входом
                    input_count = 1 if target_gate.gate_type == 'INVERTOR' else 2
                    closest_input = 0
                    min_distance = float('inf')
                    for i in range(input_count):
                        input_y = target_gate.position[1] + (i+1) * Config.GATE_SIZE // (input_count+1)
                        distance = abs(transformed_pos.y() - input_y)
                        if distance < min_distance:
                            min_distance = distance
                            closest_input = i
                    
                    self.circuit.connect_gates(self.wire_start_gate, target_gate, closest_input)
                    self.schedule_circuit_changed()
                    print(f"Соединено: {self.wire_start_gate.gate_type} -> {target_gate.gate_type} {target_gate.name}")
                
            self.wire_start = None
            self.wire_start_gate = None
            self.update()
        
    def transform_pos(self, pos):
        """Преобразует экранные координаты в координаты схемы с учетом масштаба и смещения"""
        return QPoint(
            int((pos.x() - self.offset.x()) / self.scale),
            int((pos.y() - self.offset.y()) / self.scale)
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # ПРИМЕНЯЕМ МАСШТАБ И СМЕЩЕНИЕ
        painter.translate(self.offset)
        painter.scale(self.scale, self.scale)
        
        self.draw_grid(painter)
        self.draw_wires(painter)
        
        # РИСУЕМ ВСЕ ВЕНТИЛИ - нужно вызывать draw_gates (множественное число)
        for gate in self.circuit.gates:
            self.draw_gate(painter, gate)  # ← передаем конкретный вентиль
        
        if self.wire_start:
            painter.setPen(QPen(QColor(Config.WIRE_HOVER_COLOR), Config.WIRE_THICKNESS / self.scale))
            painter.drawLine(self.wire_start, self.transform_pos(self.last_mouse_pos))

    
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
        elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            self.scale *= self.zoom_factor
            self.scale = min(3.0, self.scale)
            self.update()
        elif event.key() == Qt.Key_Minus:
            self.scale /= self.zoom_factor
            self.scale = max(0.3, self.scale)
            self.update()
        elif event.key() == Qt.Key_0:  # Сброс масштаба
            self.scale = 1.0
            self.offset = QPoint(0, 0)
            self.update()
    
    def find_wire_path(self, start_point, end_point, source_gate=None, target_gate=None):
        """Находит угловатый путь для провода с обходом вентилей"""
        start_x, start_y = start_point.x(), start_point.y()
        end_x, end_y = end_point.x(), end_point.y()
        
        # Пробуем разные обходные маршруты
        paths_to_try = []
        
        # Маршрут 1: вверх -> вправо -> вниз
        avoid_y = start_y - 80
        path1 = [
            start_point,
            QPoint(start_x, avoid_y),      # вверх
            QPoint(end_x, avoid_y),        # вправо
            end_point
        ]
        if self.is_path_clear_multiple(path1, source_gate, target_gate):
            return path1
        
        # Маршрут 2: вниз -> вправо -> вверх
        avoid_y = start_y + 80
        path2 = [
            start_point,
            QPoint(start_x, avoid_y),      # вниз
            QPoint(end_x, avoid_y),        # вправо
            end_point
        ]
        if self.is_path_clear_multiple(path2, source_gate, target_gate):
            return path2
        
        # Если оба маршрута заблокированы, возвращаем базовый L-образный
        mid_x = (start_x + end_x) // 2
        return [
            start_point,
            QPoint(mid_x, start_y),
            QPoint(mid_x, end_y),
            end_point
        ]
    def is_path_clear(self, point1, point2, source_gate=None, target_gate=None):
        """Проверяет свободен ли путь между двумя точками"""
        # Создаем временный прямоугольник между точками
        rect = QRect(
            min(point1.x(), point2.x()) - 5,
            min(point1.y(), point2.y()) - 5,
            abs(point2.x() - point1.x()) + 10,
            abs(point2.y() - point1.y()) + 10
        )
        
        # Проверяем пересечение с каждым вентилем (кроме тех, что соединяем)
        for gate in self.circuit.gates:
            if source_gate and gate == source_gate:
                continue
            if target_gate and gate == target_gate:
                continue
                
            gate_rect = QRect(
                gate.position[0] - 5,
                gate.position[1] - 5,
                Config.GATE_SIZE + 10,
                Config.GATE_SIZE + 10
            )
            
            if rect.intersects(gate_rect):
                return False
        
        return True
    def is_path_clear_multiple(self, points, source_gate=None, target_gate=None):
        """Проверяет свободен ли путь через несколько точек"""
        for i in range(len(points) - 1):
            if not self.is_path_clear(points[i], points[i + 1], source_gate, target_gate):
                return False
        return True

    def line_intersects_rect(self, p1, p2, rect):
        """Проверяет пересекает ли линия прямоугольник"""
        # Простая проверка - если оба конца линии внутри rect
        if rect.contains(p1) or rect.contains(p2):
            return True
        
        # Проверяем пересечение с каждой стороной прямоугольника
        sides = [
            (rect.topLeft(), rect.topRight()),    # верх
            (rect.topRight(), rect.bottomRight()), # право
            (rect.bottomRight(), rect.bottomLeft()), # низ
            (rect.bottomLeft(), rect.topLeft())   # лево
        ]
        
        for side_start, side_end in sides:
            if self.lines_intersect(p1, p2, side_start, side_end):
                return True
        
        return False

    def lines_intersect(self, a1, a2, b1, b2):
        """Проверяет пересекаются ли два отрезка"""
        def ccw(A, B, C):
            return (C.y() - A.y()) * (B.x() - A.x()) > (B.y() - A.y()) * (C.x() - A.x())
        
        return ccw(a1, b1, b2) != ccw(a2, b1, b2) and ccw(a1, a2, b1) != ccw(a1, a2, b2)

    def path_length(self, points):
        """Вычисляет длину пути"""
        length = 0
        for i in range(len(points) - 1):
            dx = points[i+1].x() - points[i].x()
            dy = points[i+1].y() - points[i].y()
            length += (dx**2 + dy**2)**0.5
        return length
    def schedule_circuit_changed(self):
        """Планирует отправку сигнала об изменении с задержкой"""
        self.pending_changes = True
        self.change_timer.start(300)  # 300ms задержка

    def _emit_circuit_changed(self):
        """Фактическая отправка сигнала после задержки"""
        if self.pending_changes:
            self.circuit_changed.emit()
            self.pending_changes = False
