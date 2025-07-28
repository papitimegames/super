import time
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox

class MouseRecorderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Papiweb - Grabador de Movimientos del Mouse")
        self.root.geometry("800x700")  # Aumentamos altura para el branding
        
        self.events = []
        self.current_time = time.time()
        
        # Configurar estilo del branding
        style = ttk.Style()
        style.configure("Brand.TLabel", font=("Arial", 14, "bold"), foreground="#2c3e50")
        style.configure("BrandFooter.TLabel", font=("Arial", 8), foreground="#7f8c8d")
        
        self.setup_gui()
        
    def setup_gui(self):
        # Header con branding
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Logo y título
        brand_label = ttk.Label(
            header_frame,
            text="Papiweb Desarrollos Informáticos",
            style="Brand.TLabel"
        )
        brand_label.pack(side="left")
        
        # Panel de Vista Previa
        preview_frame = ttk.LabelFrame(self.root, text="Vista Previa", padding="10")
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        preview_header = ttk.Frame(preview_frame)
        preview_header.pack(fill="x", padx=5, pady=2)
        
        # Panel de configuración del pincel
        brush_frame = ttk.Frame(preview_header)
        brush_frame.pack(side="left", padx=10)
        
        ttk.Label(brush_frame, text="Color:").pack(side="left")
        self.color_var = tk.StringVar(value="blue")
        color_combo = ttk.Combobox(brush_frame, textvariable=self.color_var, width=10, state="readonly")
        color_combo['values'] = ('blue', 'red', 'green', 'black', 'purple', 'orange')
        color_combo.pack(side="left", padx=5)
        
        ttk.Label(brush_frame, text="Tamaño:").pack(side="left", padx=5)
        self.size_var = tk.IntVar(value=5)
        size_spin = ttk.Spinbox(brush_frame, from_=1, to=20, width=5, textvariable=self.size_var)
        size_spin.pack(side="left")
        
        # Selector de modo de dibujo
        ttk.Label(brush_frame, text="Modo:").pack(side="left", padx=5)
        self.draw_mode = tk.StringVar(value="point")
        mode_combo = ttk.Combobox(brush_frame, textvariable=self.draw_mode, width=10, state="readonly")
        mode_combo['values'] = ('point', 'line', 'circle', 'rectangle', 'straight_line')
        mode_combo.pack(side="left", padx=5)
        
        # Selector de relleno para figuras
        self.fill_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(brush_frame, text="Rellenar", variable=self.fill_var).pack(side="left", padx=5)
        
        # Indicador de estado de grabación
        self.status_label = ttk.Label(preview_header, text="⚫ En espera", foreground="gray")
        self.status_label.pack(side="left", padx=10)
        
        # Ayuda de teclas
        ttk.Label(preview_header, text="[Espacio] para iniciar/detener grabación", foreground="gray").pack(side="right")
        
        self.canvas = tk.Canvas(preview_frame, width=400, height=300, bg='white')
        self.canvas.pack(pady=5)
        
        # Variables para el dibujo de líneas
        self.last_x = None
        self.last_y = None
        
        # Eventos del mouse y teclado en el canvas
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<Button-1>', self.on_mouse_click)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_release)
        self.canvas.bind('<MouseWheel>', self.on_mouse_wheel)  # Para Windows
        self.canvas.bind('<Button-4>', self.on_mouse_wheel)    # Para Linux scroll up
        self.canvas.bind('<Button-5>', self.on_mouse_wheel)    # Para Linux scroll down
        
        # Tecla espaciadora para control de grabación
        self.root.bind('<space>', lambda e: self.toggle_recording())
        
        # Panel de Control
        control_frame = ttk.LabelFrame(self.root, text="Control", padding="10")
        control_frame.pack(fill="x", padx=10, pady=5)
        
        self.recording = False
        self.record_button = ttk.Button(control_frame, text="⏵ Grabar Mouse", command=self.toggle_recording)
        self.record_button.pack(side="left", padx=5)
        ttk.Button(control_frame, text="⏵ Ejemplo", command=self.run_sample).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Limpiar", command=self.clear_preview).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Generar Código", command=self.generate_code).pack(side="left", padx=5)
        ttk.Button(control_frame, text="💾 Guardar Archivo", command=lambda: self.save_code(None)).pack(side="left", padx=5)
        
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
        self.log_text.insert("end", "- También puedes usar el botón 'Grabar Mouse' y dibujar directamente\n")
        self.log_text.insert("end", "\nEventos registrados:\n")
        self.log_text.config(state='disabled')
        
        # Estilo para el botón de grabación
        style = ttk.Style()
        style.configure("Recording.TButton", background="red", foreground="white")
        
        # Footer con información de copyright
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(
            footer_frame,
            text="© 2025 Papiweb Desarrollos Informáticos - Herramienta de Automatización",
            style="BrandFooter.TLabel"
        ).pack(side="right")
    
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
    
    def draw_point(self, x, y, color=None, show_coords=True):
        # Escalar coordenadas al tamaño del canvas
        scale = 0.75
        cx = x * scale
        cy = y * scale
        size = self.size_var.get()
        color = color if color else self.color_var.get()
        mode = self.draw_mode.get()
        
        if mode == 'line' and self.last_x is not None:
            # Línea continua a mano alzada
            self.canvas.create_line(
                self.last_x, self.last_y,
                cx, cy,
                fill=color,
                width=size
            )
        elif mode in ['circle', 'rectangle', 'straight_line'] and self.last_x is not None:
            # Borrar la figura previa de vista previa si existe
            if hasattr(self, 'preview_shape'):
                self.canvas.delete(self.preview_shape)
            
            # Dibujar la figura según el modo
            if mode == 'circle':
                radius = ((cx - self.last_x) ** 2 + (cy - self.last_y) ** 2) ** 0.5
                self.preview_shape = self.canvas.create_oval(
                    self.last_x - radius, self.last_y - radius,
                    self.last_x + radius, self.last_y + radius,
                    fill=color if self.fill_var.get() else "",
                    outline=color,
                    width=size
                )
            elif mode == 'rectangle':
                self.preview_shape = self.canvas.create_rectangle(
                    self.last_x, self.last_y,
                    cx, cy,
                    fill=color if self.fill_var.get() else "",
                    outline=color,
                    width=size
                )
            elif mode == 'straight_line':
                self.preview_shape = self.canvas.create_line(
                    self.last_x, self.last_y,
                    cx, cy,
                    fill=color,
                    width=size
                )
        else:
            # Punto normal
            self.canvas.create_oval(
                cx-size, cy-size,
                cx+size, cy+size,
                fill=color,
                outline=color
            )
            self.last_x = cx
            self.last_y = cy
        
        if show_coords:
            self.canvas.create_text(cx, cy-15, text=f"({x},{y})", font=("Arial", 8))
        
        if mode == 'point' or mode == 'line':
            self.last_x = cx
            self.last_y = cy
    
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
        self.last_x = None
        self.last_y = None
        if hasattr(self, 'preview_shape'):
            delattr(self, 'preview_shape')
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
    
    def toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            self.record_button.configure(text="⏺ Detener Grabación", style="Recording.TButton")
            self.status_label.configure(text="⚫ Grabando", foreground="red")
            self.events = []
            self.log_event("Grabación iniciada - Mueve el mouse en el área de vista previa")
            self.canvas.focus_set()  # Dar foco al canvas para detectar la tecla espaciadora
        else:
            self.record_button.configure(text="⏵ Grabar Mouse", style="")
            self.status_label.configure(text="⚫ En espera", foreground="gray")
            self.log_event("Grabación detenida")
    
    def on_mouse_move(self, event):
        if self.recording:
            # Convertir coordenadas del canvas a coordenadas escaladas
            x = int(event.x / 0.75)  # Invertir el escalado que usamos en draw_point
            y = int(event.y / 0.75)
            self.events.append(('move', x, y, time.time()))
            self.draw_point(x, y)
            self.log_event(f"Mover a ({x}, {y})")
    
    def on_mouse_click(self, event):
        if self.recording:
            x = int(event.x / 0.75)
            y = int(event.y / 0.75)
            self.events.append(('click', x, y, 'left', True, time.time()))
            mode = self.draw_mode.get()
            
            if mode in ['circle', 'rectangle', 'straight_line']:
                # Para figuras, guardamos el punto inicial
                scale = 0.75
                self.last_x = x * scale
                self.last_y = y * scale
                # No dibujamos nada hasta que el usuario arrastre o suelte
            else:
                self.draw_point(x, y, 'red')
            
            self.log_event(f"Click en ({x}, {y})")
    
    def on_mouse_release(self, event):
        if self.recording:
            x = int(event.x / 0.75)
            y = int(event.y / 0.75)
            self.events.append(('click', x, y, 'left', False, time.time()))
            
            mode = self.draw_mode.get()
            if mode in ['circle', 'rectangle', 'straight_line']:
                # Confirmar la figura final
                if hasattr(self, 'preview_shape'):
                    # La figura ya está dibujada en preview_shape
                    delattr(self, 'preview_shape')
            
            # Resetear las coordenadas
            self.last_x = None
            self.last_y = None
            
    def on_mouse_wheel(self, event):
        if self.recording:
            x = int(event.x / 0.75)
            y = int(event.y / 0.75)
            # En Windows, event.delta será múltiplo de 120
            # En Linux, event.num será 4 (arriba) o 5 (abajo)
            if hasattr(event, 'delta'):
                delta = event.delta // 120
            else:
                delta = 1 if event.num == 4 else -1
            self.events.append(('scroll', x, y, 0, delta, time.time()))
            self.draw_point(x, y, 'green')
            self.log_event(f"Scroll en ({x}, {y}) delta={delta}")
    
    def check_code(self, code_lines):
        """Verifica la validez del código generado."""
        try:
            # Verificar sintaxis
            complete_code = "\n".join(code_lines)
            compile(complete_code, "<string>", "exec")
            
            # Verificar importaciones
            required_imports = {"pyautogui", "time"}
            found_imports = set()
            for line in code_lines:
                if line.startswith("import "):
                    found_imports.add(line.split()[1])
            
            missing_imports = required_imports - found_imports
            if missing_imports:
                return False, f"Faltan importaciones: {', '.join(missing_imports)}"
            
            return True, "Código válido"
            
        except SyntaxError as e:
            return False, f"Error de sintaxis: {str(e)}"
        except Exception as e:
            return False, f"Error en la verificación: {str(e)}"
    
    def preview_code(self, code_lines):
        """Muestra una vista previa del código en una nueva ventana."""
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Vista Previa del Código")
        preview_window.geometry("600x400")
        preview_window.transient(self.root)  # Hacer la ventana modal
        preview_window.grab_set()  # Forzar foco en esta ventana
        
        # Marco superior con mensaje y estado
        message_frame = ttk.Frame(preview_window, padding="10")
        message_frame.pack(fill="x")
        
        status_label = ttk.Label(
            message_frame,
            text="✓ Código verificado correctamente",
            foreground="green"
        )
        status_label.pack(side="right")
        
        ttk.Label(
            message_frame,
            text="Revise el código generado antes de guardar:",
            style="Brand.TLabel"
        ).pack(side="left")
        
        # Área de código
        code_frame = ttk.Frame(preview_window, padding="10")
        code_frame.pack(fill="both", expand=True)
        
        code_text = scrolledtext.ScrolledText(
            code_frame,
            wrap=tk.NONE,
            font=("Courier", 10)
        )
        code_text.pack(fill="both", expand=True)
        code_text.insert("1.0", "\n".join(code_lines))
        code_text.config(state="disabled")
        
        # Botones
        button_frame = ttk.Frame(preview_window, padding="10")
        button_frame.pack(fill="x")
        
        # Guardar el código en una variable de la ventana
        preview_window.code_lines = code_lines
        
        save_button = ttk.Button(
            button_frame,
            text="✓ Guardar Script",
            command=lambda: self.save_code(preview_window)
        )
        save_button.pack(side="right", padx=5)
        
        cancel_button = ttk.Button(
            button_frame,
            text="❌ Cancelar",
            command=preview_window.destroy
        )
        cancel_button.pack(side="right", padx=5)
        
        # Centrar la ventana
        preview_window.update_idletasks()
        width = preview_window.winfo_width()
        height = preview_window.winfo_height()
        x = (preview_window.winfo_screenwidth() // 2) - (width // 2)
        y = (preview_window.winfo_screenheight() // 2) - (height // 2)
        preview_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Asegurarse de que la ventana tenga foco
        preview_window.focus_set()
    
    def save_code(self, preview_window=None):
        """Guarda el código después de la vista previa o directamente."""
        if not self.events:
            messagebox.showwarning(
                "Sin eventos",
                "No hay eventos para guardar. Grabe algunos movimientos primero.",
                parent=self.root
            )
            return

        try:
            # Generar el código si no viene de la vista previa
            if preview_window is None:
                code_lines = [
                    "import pyautogui",
                    "import time",
                    "",
                    "# Script generado por Papiweb Desarrollos Informáticos",
                    "# Fecha: " + time.strftime("%Y-%m-%d %H:%M:%S"),
                    "",
                    "pyautogui.PAUSE = 0",
                    ""
                ]
                
                prev_time = self.events[0][-1]
                for event in self.events:
                    current_time = event[-1]
                    delay = current_time - prev_time
                    if delay > 0:
                        code_lines.append(f"time.sleep({delay:.3f})")
                    prev_time = current_time
                    
                    if event[0] == 'move':
                        x, y = event[1], event[2]
                        code_lines.append(f"pyautogui.moveTo({x}, {y})")
                    elif event[0] == 'click':
                        x, y, button, pressed = event[1], event[2], event[3], event[4]
                        action = 'mouseDown' if pressed else 'mouseUp'
                        code_lines.append(f"pyautogui.{action}({x}, {y}, button='{button}')")
                    elif event[0] == 'scroll':
                        x, y, dx, dy = event[1], event[2], event[3], event[4]
                        code_lines.append(f"pyautogui.scroll({int(dy * 100)})")
            else:
                code_lines = preview_window.code_lines

            # Crear diálogo de guardado
            file_path = filedialog.asksaveasfilename(
                parent=self.root,  # Usar la ventana principal como padre
                defaultextension=".py",
                filetypes=[("Python files", "*.py"), ("All files", "*.*")],
                initialfile="recorded_script.py",
                title="Guardar script de mouse"
            )
            
            if file_path:  # Si el usuario no canceló el diálogo
                # Guardar el archivo
                with open(file_path, 'w') as f:
                    f.write("\n".join(code_lines))
                
                # Mostrar mensaje de éxito
                self.log_event(f"✓ Script guardado exitosamente en: '{file_path}'")
                
                # Cerrar la ventana de vista previa si existe
                if preview_window is not None:
                    preview_window.destroy()
                
                # Mostrar mensaje de confirmación
                tk.messagebox.showinfo(
                    "Éxito",
                    f"El script se ha guardado correctamente en:\n{file_path}",
                    parent=self.root
                )
        except Exception as e:
            # Mostrar error si algo falla
            tk.messagebox.showerror(
                "Error al guardar",
                f"No se pudo guardar el archivo:\n{str(e)}",
                parent=self.root if preview_window is None else preview_window
            )
            self.log_event(f"Error al guardar el script: {str(e)}", error=True)
    
    def generate_code(self):
        if not self.events:
            self.log_event("No hay eventos para generar código", error=True)
            return
            
        code = [
            "import pyautogui",
            "import time",
            "",
            "# Script generado por Papiweb Desarrollos Informáticos",
            "# Fecha: " + time.strftime("%Y-%m-%d %H:%M:%S"),
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
        
        # Verificar el código
        is_valid, message = self.check_code(code)
        if not is_valid:
            self.log_event(f"Error en el código generado: {message}", error=True)
            return
        
        # Mostrar vista previa
        self.preview_code(code)

def main():
    root = tk.Tk()
    app = MouseRecorderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
