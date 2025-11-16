import sys
import os

# Добавляем путь для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from logic.gates import LogicGate

class Simulator:
    def __init__(self, circuit):
        self.circuit = circuit
    
    def simulate(self, input_values):
        """Запускает симуляцию схемы с заданными значениями входов"""
        # Сбрасываем все значения
        self.reset_circuit()
        
        # Устанавливаем значения входных вентилей
        input_gates = [gate for gate in self.circuit.gates if gate.gate_type == 'INPUT']
        input_gates.sort(key=lambda gate: gate.name)  # Сортируем по имени X1, X2, X3...
        
        for i, value in enumerate(input_values):
            if i < len(input_gates):
                input_gates[i].output = bool(value)
                print(f"Установлен вход {input_gates[i].name} = {value}")
        
        # Вычисляем схему (несколько проходов для стабильности)
        for pass_num in range(20):  # Максимум 20 проходов
            changed = self.propagate_signals()
            print(f"Проход {pass_num + 1}: изменений = {changed}")
            if not changed:
                break
        
        # Собираем результаты с выходных вентилей
        output_gates = [gate for gate in self.circuit.gates if gate.gate_type == 'OUTPUT']
        output_gates.sort(key=lambda gate: gate.name)  # Сортируем по имени Y1, Y2, Y3...
        
        outputs = []
        for gate in output_gates:
            output_value = gate.calculate_output()
            outputs.append(output_value)
            print(f"Выход {gate.name} = {output_value}")
        
        return outputs
    
    def reset_circuit(self):
        """Сбрасывает все значения в схеме"""
        for gate in self.circuit.gates:
            if gate.gate_type not in ['INPUT', 'OUTPUT']:
                gate.output = False
            if hasattr(gate, 'inputs'):
                # Оставляем структуру входов, но сбрасываем значения
                gate.inputs = [False] * len(gate.inputs) if gate.inputs else []
    
    def propagate_signals(self):
        """Распространяет сигналы по схеме, возвращает True если были изменения"""
        changed = False
        
        # ОБНОВЛЯЕМ ВХОДЫ ВСЕХ ВЕНТИЛЕЙ ИЗ СОЕДИНЕНИЙ
        for source_gate, target_gate, input_index in self.circuit.connections:
            if input_index < len(target_gate.inputs):
                new_value = source_gate.calculate_output()
                if target_gate.inputs[input_index] != new_value:
                    target_gate.inputs[input_index] = new_value
                    changed = True
                    print(f"📡 {source_gate.gate_type} -> вход[{input_index}] {target_gate.gate_type}: {new_value}")
        
        # ВЫЧИСЛЯЕМ ВЫХОДЫ ВСЕХ ВЕНТИЛЕЙ
        for gate in self.circuit.gates:
            if gate.gate_type not in ['INPUT']:
                old_output = gate.output
                new_output = gate.calculate_output()
                
                if old_output != new_output:
                    gate.output = new_output
                    changed = True
                    print(f"🎯 {gate.gate_type} выход: {old_output} -> {new_output} (входы: {gate.inputs})")
        
        return changed
        
    def generate_truth_table(self):
        """Генерирует полную таблицу истинности для схемы"""
        input_gates = [gate for gate in self.circuit.gates if gate.gate_type == 'INPUT']
        input_gates.sort(key=lambda gate: gate.name)  # Сортируем по имени
        
        output_gates = [gate for gate in self.circuit.gates if gate.gate_type == 'OUTPUT']
        output_gates.sort(key=lambda gate: gate.name)  # Сортируем по имени
        
        print(f"Найдено входов: {len(input_gates)}, выходов: {len(output_gates)}")
        
        if not input_gates:
            return [], []
        
        # Генерируем все комбинации входов (2^n)
        input_combinations = []
        n_inputs = len(input_gates)
        
        for i in range(2 ** n_inputs):
            combination = []
            for j in range(n_inputs):
                # Генерируем комбинацию в правильном порядке
                bit_value = bool((i >> (n_inputs - 1 - j)) & 1)
                combination.append(bit_value)
            input_combinations.append(combination)
        
        # Симулируем каждую комбинацию
        truth_table = []
        for inputs in input_combinations:
            print(f"Симуляция для входов: {inputs}")
            outputs = self.simulate(inputs)
            truth_table.append((inputs, outputs))
        
        return input_combinations, truth_table
