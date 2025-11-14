import sys
import os
sys.path.append(os.path.dirname(__file__))
from gates import LogicGate, InputGate, OutputGate

class Circuit:
    def __init__(self):
        self.gates = []
        self.connections = []  # (source_gate, target_gate, target_input_index)
        self.input_gates = []
        self.output_gates = []
    
    def add_gate(self, gate_type, x, y, name=None):
        """Добавляет новый вентиль в схему"""
        if not name:
            name = f"{gate_type}_{len(self.gates) + 1}"
        
        # Создаем вентиль с правильным количеством входов
        if gate_type == 'INVERTOR':
            gate = LogicGate(gate_type, name)
            gate.inputs = [False]  # Один вход для инвертора
        else:
            gate = LogicGate(gate_type, name) 
            gate.inputs = [False, False]  # Два входа для остальных
        
        gate.output = False
        gate.position = (x, y)
        self.gates.append(gate)
        
        # Автоматически добавляем в соответствующие списки
        if gate_type == 'INPUT':
            self.input_gates.append(gate)
        elif gate_type == 'OUTPUT':
            self.output_gates.append(gate)
            
        return gate
    
    def add_input_gate(self, name, value=False):
        """Добавляет входной вентиль"""
        gate = InputGate(name, value)
        self.input_gates.append(gate)
        self.gates.append(gate)
        return gate
    
    def add_output_gate(self, name):
        """Добавляет выходной вентиль"""
        gate = OutputGate(name)
        self.output_gates.append(gate)
        self.gates.append(gate)
        return gate
    
    def connect_gates(self, source_gate, target_gate, target_input_index=0):
        """Соединяет два вентиля"""
        connection = (source_gate, target_gate, target_input_index)
        if connection not in self.connections:
            self.connections.append(connection)
            return True
        return False
    
    def simulate(self, input_values=None):
        """Запускает симуляцию схемы"""
        # TODO: Реализовать симуляцию
        print("Симуляция запущена (заглушка)")
        return [False]  # Заглушка
    
    def clear(self):
        """Очищает схему"""
        self.gates.clear()
        self.connections.clear()
        self.input_gates.clear()
        self.output_gates.clear()
        print("Схема очищена")
    
    def get_input_count(self):
        """Возвращает количество входных вентилей"""
        return len(self.input_gates)
    
    def get_output_count(self):
        """Возвращает количество выходных вентилей""" 
        return len(self.output_gates)
