class LogicGate:
    def __init__(self, gate_type, name):
        self.gate_type = gate_type  # 'AND', 'OR', 'NOT', etc.
        self.name = name
        self.inputs = []
        self.output = None
        self.position = (0, 0)  # x, y coordinates
    
    def calculate_output(self):
        """Вычисляет выход на основе входов с правильной логикой"""
        # Убедимся что все входы имеют булевы значения
        bool_inputs = [bool(inp) for inp in self.inputs]
        
        if self.gate_type == "AND":
            return all(bool_inputs) if bool_inputs else False
            
        elif self.gate_type == "OR":
            return any(bool_inputs) if bool_inputs else False
            
        elif self.gate_type == "NOT" or self.gate_type == "INVERTOR":
            return not bool_inputs[0] if bool_inputs else False
            
        elif self.gate_type == "NAND":
            return not all(bool_inputs) if bool_inputs else True
            
        elif self.gate_type == "NOR":
            return not any(bool_inputs) if bool_inputs else True
            
        elif self.gate_type == "XOR":
            # Исключающее ИЛИ: истинно когда входы разные
            if len(bool_inputs) >= 2:
                return bool_inputs[0] != bool_inputs[1]
            return False
            
        elif self.gate_type == "XNOR":
            # Исключающее ИЛИ-НЕ: истинно когда входы одинаковые
            if len(bool_inputs) >= 2:
                return bool_inputs[0] == bool_inputs[1]
            return False
            
        elif self.gate_type == "INPUT":
            return self.output  # INPUT просто возвращает свое значение
            
        elif self.gate_type == "OUTPUT":
            return bool_inputs[0] if bool_inputs else False
            
        else:
            return False
    
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
