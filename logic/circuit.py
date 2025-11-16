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
        if not name:
            name = f"{gate_type}_{len(self.gates) + 1}"
        
        # ОБРАБАТЫВАЕМ ВХОДНЫЕ ЭЛЕМЕНТЫ С АВТОМАТИЧЕСКОЙ НУМЕРАЦИЕЙ
        if gate_type == 'INPUT':
            # Считаем сколько INPUT уже есть для нумерации X1, X2, X3...
            input_count = len([g for g in self.gates if g.gate_type == 'INPUT'])
            input_name = f"X{input_count + 1}"
            gate = InputGate(input_name, False)
            gate.gate_type = 'INPUT'
            gate.position = (x, y)
            self.input_gates.append(gate)
            self.gates.append(gate)
            print(f"✓ Добавлен входной элемент: {input_name}")
            return gate
            
        elif gate_type == 'OUTPUT':
            # Считаем сколько OUTPUT уже есть для нумерации Y1, Y2, Y3...
            output_count = len([g for g in self.gates if g.gate_type == 'OUTPUT'])
            output_name = f"Y{output_count + 1}"
            gate = OutputGate(output_name)
            gate.gate_type = 'OUTPUT'
            gate.position = (x, y)
            self.output_gates.append(gate)
            self.gates.append(gate)
            print(f"✓ Добавлен выходной элемент: {output_name}")
            return gate
            
        else:
            # Обычные логические вентили
            gate = LogicGate(gate_type, name)
            gate.position = (x, y)
            
            if gate_type == 'INVERTOR':
                gate.inputs = [False]
            else:
                gate.inputs = [False, False]
                
            gate.output = False
            self.gates.append(gate)
            print(f"✓ Добавлен логический вентиль: {gate_type}")
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
