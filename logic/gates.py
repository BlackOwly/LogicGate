class LogicGate:
    def __init__(self, gate_type, name):
        self.gate_type = gate_type  # 'AND', 'OR', 'NOT', etc.
        self.name = name
        self.inputs = []
        self.output = None
        self.position = (0, 0)  # x, y coordinates
    
    def calculate_output(self):
        """Вычисляет выход на основе входов"""
        if self.gate_type == "AND":
            return all(self.inputs)
        elif self.gate_type == "OR":
            return any(self.inputs)
        elif self.gate_type == "NOT":
            return not self.inputs[0] if self.inputs else False
        elif self.gate_type == "NAND":
            return not all(self.inputs)
        elif self.gate_type == "NOR":
            return not any(self.inputs)
        elif self.gate_type == "XOR":
            return sum(self.inputs) == 1 if len(self.inputs) == 2 else False
        elif self.gate_type == "XNOR":
            return sum(self.inputs) != 1 if len(self.inputs) == 2 else False
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
