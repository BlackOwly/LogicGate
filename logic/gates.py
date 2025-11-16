class LogicGate:
    def __init__(self, gate_type, name):
        self.gate_type = gate_type  # 'AND', 'OR', 'NOT', etc.
        self.name = name
        self.inputs = []
        self.output = None
        self.position = (0, 0)  # x, y coordinates
    
    def calculate_output(self):
        """Вычисляет выход на основе входов с правильной логикой"""
        # Убедимся что все входы инициализированы и являются булевыми
        if not hasattr(self, 'inputs') or self.inputs is None:
            self.inputs = []
        
        # Создаем безопасный список входов
        safe_inputs = []
        for inp in self.inputs:
            if inp is None:
                safe_inputs.append(False)
            else:
                safe_inputs.append(bool(inp))
        
        print(f"🔍 {self.gate_type} вычисление: входы = {safe_inputs}")
        
        if self.gate_type == "AND":
            result = all(safe_inputs) if safe_inputs else False
            
        elif self.gate_type == "OR":
            result = any(safe_inputs) if safe_inputs else False
            
        elif self.gate_type == "NOT" or self.gate_type == "INVERTOR":
            result = not safe_inputs[0] if safe_inputs else False
            
        elif self.gate_type == "NAND":
            result = not all(safe_inputs) if safe_inputs else True
            
        elif self.gate_type == "NOR":
            result = not any(safe_inputs) if safe_inputs else True
            
        elif self.gate_type == "XOR":
            # Исключающее ИЛИ: истинно когда входы разные
            if len(safe_inputs) >= 2:
                result = safe_inputs[0] != safe_inputs[1]
            else:
                result = False
            
        elif self.gate_type == "XNOR":
            # Исключающее ИЛИ-НЕ: истинно когда входы одинаковые
            if len(safe_inputs) >= 2:
                result = safe_inputs[0] == safe_inputs[1]
            else:
                result = False
            
        elif self.gate_type == "INPUT":
            result = self.output  # INPUT просто возвращает свое значение
            
        elif self.gate_type == "OUTPUT":
            result = safe_inputs[0] if safe_inputs else False
            
        else:
            result = False
        
        print(f"🎯 {self.gate_type} результат: {result}")
        return result
    
    def set_input(self, index, value):
        """Устанавливает значение входа по индексу"""
        if index < len(self.inputs):
            self.inputs[index] = value
        else:
            while len(self.inputs) <= index:
                self.inputs.append(False)
            self.inputs[index] = value


class InputGate(LogicGate):
    """Специальный вентиль для входных данных"""
    def __init__(self, name, value=False):
        super().__init__("INPUT", name)
        self.output = value
    
    def calculate_output(self):
        return self.output
    
    def set_value(self, value):
        self.output = bool(value)


class OutputGate(LogicGate):
    """Специальный вентиль для выходных данных"""
    def __init__(self, name):
        super().__init__("OUTPUT", name)
    
    def calculate_output(self):
        return self.inputs[0] if self.inputs else False
