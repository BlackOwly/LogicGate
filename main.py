import sys
import os

# Добавляем все нужные пути
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'gui'))
sys.path.insert(0, os.path.join(current_dir, 'logic'))
sys.path.insert(0, os.path.join(current_dir, 'utils'))

try:
    from PyQt5.QtWidgets import QApplication
    from gui.main_window import MainWindow
    from logic.circuit import Circuit
    print("✓ Все модули успешно загружены!")
    
    # Проверим что файлы существуют
    print("Файлы в папках:")
    print("gui:", [f for f in os.listdir('gui') if f.endswith('.py')])
    print("logic:", [f for f in os.listdir('logic') if f.endswith('.py')])
    print("utils:", [f for f in os.listdir('utils') if f.endswith('.py')])
    
except ImportError as e:
    print(f"✗ Ошибка импорта: {e}")
    print("Полный traceback:")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def main():
    app = QApplication(sys.argv)
    circuit = Circuit()
    window = MainWindow(circuit)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
