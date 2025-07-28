import time
import tkinter as tk
from tkinter import ttk, scrolledtext

class MouseRecorderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Grabador de Movimientos del Mouse")
        self.root.geometry("800x600")
        
        self.events = []
        self.current_time = time.time()
        
        self.setup_gui()
        
    def setup_gui(self):
        # Panel de Vista Previa
        preview_frame = ttk.LabelFrame(self.root, text="Vista Previa", padding="10")
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.canvas = tk.Canvas(preview_frame, width=400, height=300, bg='white')
        self.canvas.pack(pady=5)
        
        # Panel de Control
        control_frame = ttk.LabelFrame(self.root, text="Control", padding="10")
        control_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(control_frame, text="Ejemplo", command=self.run_sample).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Limpiar", command=self.clear_preview).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Generar Código", command=self.generate_code).pack(side="left", padx=5)
        
        # Panel de Entrada Manual
        input_frame = ttk.LabelFrame(self.root, text="Entrada Manual", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(input_frame, text="Comando:").pack(side="left", padx=5)
        self.cmd_entry = ttk.Entry(input_frame, width=40)
        self.cmd_entry.pack(side="left", padx=5)
        self.cmd_entry.bind('<Return>', self.process_command)
        ttk.Button(input_frame, text="Añadir", command=self.process_command).pack(side="left", padx=5)
        
        # Panel de Registro
        log_frame = ttk.LabelFrame(self.root, text="Registro de Eventos", padding="10")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill="both", expand=True)
        
        # Instrucciones
        self.log_text.insert("1.0", "Instrucciones:\n")
        self.log_text.insert("end", "- move x y: Mover a coordenadas\n")
        self.log_text.insert("end", "- click x y: Click en coordenadas\n")
        self.log_text.insert("end", "- scroll x y delta: Scroll en coordenadas\n")
        self.log_text.insert("end", "\nEventos registrados:\n")
        self.log_text.config(state='disabled')
    
    def process_command(self, event=None):
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return
            
        parts = cmd.split()
        if not parts:
            return
            
        try:
            if parts[0] == 'move' and len(parts) == 3:
                x, y = map(int, parts[1:])
                self.events.append(('move', x, y, time.time()))
                self.draw_point(x, y, 'blue')
                self.log_event(f"Mover a ({x}, {y})")
                
            elif parts[0] == 'click' and len(parts) == 3:
                x, y = map(int, parts[1:])
                self.events.append(('click', x, y, 'left', True, time.time()))
                self.events.append(('click', x, y, 'left', False, time.time() + 0.1))
                self.draw_point(x, y, 'red')
                self.log_event(f"Click en ({x}, {y})")
                
            elif parts[0] == 'scroll' and len(parts) == 4:
                x, y, delta = map(int, parts[1:])
                self.events.append(('scroll', x, y, 0, delta, time.time()))
                self.draw_point(x, y, 'green')
                self.log_event(f"Scroll en ({x}, {y}) delta={delta}")
            else:
                self.log_event("Comando no reconocido", error=True)
        except ValueError:
            self.log_event("Valores inválidos", error=True)
            
        self.cmd_entry.delete(0, tk.END)
    
    def draw_point(self, x, y, color):
        # Escalar coordenadas al tamaño del canvas
        scale = 0.75
        cx = x * scale
        cy = y * scale
        size = 5
        self.canvas.create_oval(cx-size, cy-size, cx+size, cy+size, fill=color)
        self.canvas.create_text(cx, cy-15, text=f"({x},{y})", font=("Arial", 8))
    
    def log_event(self, message, error=False):
        self.log_text.config(state='normal')
        if error:
            self.log_text.insert("end", "ERROR: " + message + "\n", "error")
        else:
            self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state='disabled')
    
    def clear_preview(self):
        self.canvas.delete("all")
        self.events = []
        self.log_text.config(state='normal')
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert("1.0", "Vista previa limpiada\n")
        self.log_text.config(state='disabled')
    
    def run_sample(self):
        self.clear_preview()
        current_time = time.time()
        sample_actions = [
            ('move', 100, 100, current_time),
            ('move', 200, 200, current_time + 1),
            ('click', 200, 200, 'left', True, current_time + 2),
            ('click', 200, 200, 'left', False, current_time + 2.1),
            ('move', 300, 300, current_time + 3),
            ('scroll', 300, 300, 0, 1, current_time + 4),
        ]
        for event in sample_actions:
            if event[0] == 'move':
                self.draw_point(event[1], event[2], 'blue')
                self.log_event(f"Mover a ({event[1]}, {event[2]})")
            elif event[0] == 'click':
                self.draw_point(event[1], event[2], 'red')
                self.log_event(f"Click en ({event[1]}, {event[2]})")
            elif event[0] == 'scroll':
                self.draw_point(event[1], event[2], 'green')
                self.log_event(f"Scroll en ({event[1]}, {event[2]})")
        self.events = sample_actions
    
    def generate_code(self):
        if not self.events:
            self.log_event("No hay eventos para generar código", error=True)
            return
            
        code = [
            "import pyautogui",
            "import time",
            "",
            "pyautogui.PAUSE = 0",
            ""
        ]
        
        prev_time = self.events[0][-1]
        for event in self.events:
            current_time = event[-1]
            delay = current_time - prev_time
            
            if delay > 0:
                code.append(f"time.sleep({delay:.3f})")
            prev_time = current_time
            
            if event[0] == 'move':
                x, y = event[1], event[2]
                code.append(f"pyautogui.moveTo({x}, {y})")
            elif event[0] == 'click':
                x, y, button, pressed = event[1], event[2], event[3], event[4]
                action = 'mouseDown' if pressed else 'mouseUp'
                code.append(f"pyautogui.{action}({x}, {y}, button='{button}')")
            elif event[0] == 'scroll':
                x, y, dx, dy = event[1], event[2], event[3], event[4]
                code.append(f"pyautogui.scroll({int(dy * 100)})")
                
        with open('recorded_script.py', 'w') as f:
            f.write('\n'.join(code))
        self.log_event("Script generado: 'recorded_script.py'")

def main():
    root = tk.Tk()
    app = MouseRecorderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
