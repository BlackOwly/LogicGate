import json
import os

class ProjectSerializer:
    @staticmethod
    def save_project(circuit, filepath):
        """Сохраняет проект в файл"""
        project_data = {
            'version': '1.0',
            'gates': [],
            'connections': []
        }
        
        # Сохраняем все вентили
        for gate in circuit.gates:
            gate_data = {
                'type': gate.gate_type,
                'position': gate.position,
                'name': getattr(gate, 'name', ''),
                'inputs': getattr(gate, 'inputs', []),
                'output': getattr(gate, 'output', False)
            }
            project_data['gates'].append(gate_data)
        
        # Сохраняем все соединения
        for source_gate, target_gate, input_index in circuit.connections:
            connection_data = {
                'source_index': circuit.gates.index(source_gate),
                'target_index': circuit.gates.index(target_gate),
                'input_index': input_index
            }
            project_data['connections'].append(connection_data)
        
        # Сохраняем в файл
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Проект сохранен: {filepath}")
        return True
    
    @staticmethod
    def load_project(circuit, filepath):
        """Загружает проект из файла"""
        if not os.path.exists(filepath):
            print(f"❌ Файл не найден: {filepath}")
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Очищаем текущую схему
            circuit.clear()
            
            # Восстанавливаем вентили
            for gate_data in project_data['gates']:
                gate = circuit.add_gate(
                    gate_data['type'],
                    gate_data['position'][0],
                    gate_data['position'][1],
                    gate_data.get('name', '')
                )
                gate.inputs = gate_data.get('inputs', [])
                gate.output = gate_data.get('output', False)
            
            # Восстанавливаем соединения
            for conn_data in project_data['connections']:
                source_gate = circuit.gates[conn_data['source_index']]
                target_gate = circuit.gates[conn_data['target_index']]
                circuit.connect_gates(source_gate, target_gate, conn_data['input_index'])
            
            print(f"✅ Проект загружен: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            return False
