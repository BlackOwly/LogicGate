import os

class Config:
    # Размеры
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 800
    GATE_SIZE = 60
    WIRE_THICKNESS = 3
    
    # Цвета
    WIRE_COLOR = "#2E86AB"
    WIRE_HOVER_COLOR = "#FF6B6B"
    GATE_SELECTED_COLOR = "#FF9F1C"
    GATE_BORDER_COLOR = "#333333"
    GRID_COLOR = "#E0E0E0"
    
    # Пути к иконкам
    ICON_PATHS = {
        'INVERTOR': 'icons/invertor.png',
        'AND': 'icons/and.png', 
        'NAND': 'icons/nand.png',
        'OR': 'icons/or.png',
        'NOR': 'icons/nor.png',
        'XOR': 'icons/xor.png',
        'XNOR': 'icons/xnor.png'
    }
    
    @staticmethod
    def get_icon_path(gate_type):
        return f"icons/{gate_type.lower()}.png"
