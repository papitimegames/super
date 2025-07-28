#!/usr/bin/env python3
# deepseek_terminal_advanced.py

import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time
import sys
import html
import threading
import queue
import mimetypes
import base64
from pathlib import Path
from prompt_toolkit import prompt, HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import run_in_terminal
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter

# Configuración
SESSION_FILE = "chat_session.json"
HISTORY_FILE = "chat_history.txt"
DEEPSEEK_URL = "https://chat.deepseek.com"
CLAUDE_URL = "https://claude.ai"
GEMINI_URL = "https://gemini.google.com"
CHATGPT_URL = "https://chat.openai.com"
MODEL = "deepseek-chat"  # deepseek-coder para programación
PLATFORM = "deepseek"  # puede ser 'deepseek', 'claude', 'gemini' o 'chatgpt'

# Información de la aplicación
APP_NAME = "Terminal Chat Multimodelo"
APP_VERSION = "1.0"
APP_COMPANY = "Papiweb Desarrollos Informáticos"
APP_YEAR = "2025"
APP_SUPPORT = "soporte@papiweb.com"

# Estilo para la terminal
style = Style.from_dict({
    'prompt': 'ansicyan bold',
    'assistant': 'ansigreen',
    'user': 'ansiblue',
    'system': 'ansimagenta',
    'error': 'ansired bold',
    'warning': 'ansiyellow',
    'code': 'ansicyan',
    'file': 'ansiyellow',
    'brand': 'ansiyellow bold',
})

# Colores ANSI para formato
COLORS = {
    'reset': '\033[0m',
    'bold': '\033[1m',
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
}

class DeepSeekTerminal:
    def __init__(self):
        self.session = requests.Session()
        self.session_data = self.load_session()
        self.conversation_id = self.session_data.get('last_conversation', "")
        self.message_history = []
        self.streaming_active = False
        self.stop_stream = threading.Event()
        self.stream_queue = queue.Queue()
        self.key_bindings = self.create_key_bindings()
        
        # Configurar headers
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Referer": f"{DEEPSEEK_URL}/",
        })
        
        # Configurar cookies existentes
        for name, value in self.session_data.get('cookies', {}).items():
            self.session.cookies.set(name, value, domain='.deepseek.com')
    
    def create_key_bindings(self):
        bindings = KeyBindings()
        
        @bindings.add('c-c')
        def _(event):
            if self.streaming_active:
                self.stop_stream.set()
                self.print_message("\n\n🔴 Generación interrumpida\n", 'warning')
                event.app.exit()
            else:
                event.app.exit(exception=KeyboardInterrupt, style='class:aborting')
        
        return bindings
    
    def load_session(self):
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {"cookies": {}, "last_conversation": ""}
    
    def save_session(self):
        cookies = {}
        if PLATFORM == "chatgpt":
            cookies = {
                'session_token': self.session.cookies.get('__Secure-next-auth.session-token', ''),
                'cf_clearance': self.session.cookies.get('cf_clearance', '')
            }
        else:
            cookies = {
                'session_token': self.session.cookies.get('session_token', ''),
                'cf_clearance': self.session.cookies.get('cf_clearance', '')
            }
        
        self.session_data['cookies'] = cookies
        self.session_data['last_conversation'] = self.conversation_id
        with open(SESSION_FILE, 'w') as f:
            json.dump(self.session_data, f)
    
    def get_csrf_token(self):
        response = self.session.get(f"{DEEPSEEK_URL}/")
        soup = BeautifulSoup(response.text, 'html.parser')
        token_tag = soup.find('meta', attrs={'name': 'csrf-token'})
        return token_tag['content'] if token_tag else ""
    
    def login(self):
        if PLATFORM == "deepseek":
            platform_name = "DeepSeek Chat"
            login_url = f"{DEEPSEEK_URL}/auth/signin"
            domain = ".deepseek.com"
        elif PLATFORM == "claude":
            platform_name = "Claude.ai"
            login_url = f"{CLAUDE_URL}/auth/signin"
            domain = ".claude.ai"
        elif PLATFORM == "gemini":
            platform_name = "Google Gemini"
            login_url = f"{GEMINI_URL}/auth/signin"
            domain = ".google.com"
        else:  # chatgpt
            platform_name = "ChatGPT"
            login_url = f"{CHATGPT_URL}/auth/login"
            domain = ".openai.com"
            
        self.print_message(f"🔓 Iniciando sesión en {platform_name}...", 'system')
        csrf_token = self.get_csrf_token()
        response = self.session.post(login_url, data={
            "_token": csrf_token,
            "email": "tu_email@ejemplo.com",  # Reemplazar con tu email
            "password": "tu_password",         # Reemplazar con tu password
            "remember": "on"
        }, allow_redirects=False)
        
        if response.status_code == 302:
            self.print_message("✅ Sesión iniciada correctamente", 'system')
            self.save_session()
            return True
        else:
            self.print_message("❌ Error en inicio de sesión. Por favor inicia sesión manualmente:", 'error')
            self.print_message("1. Abre https://chat.deepseek.com en Chrome/Firefox", 'system')
            self.print_message("2. Inicia sesión con tu cuenta", 'system')
            self.print_message("3. Abre las herramientas de desarrollo (F12)", 'system')
            self.print_message("4. Ve a Application > Cookies y copia los valores de:", 'system')
            self.print_message("   - session_token", 'system')
            self.print_message("   - cf_clearance", 'system')
            
            cookies = {}
            cookies['session_token'] = input(f"{COLORS['yellow']}session_token: {COLORS['reset']}").strip()
            cookies['cf_clearance'] = input(f"{COLORS['yellow']}cf_clearance: {COLORS['reset']}").strip()
            
            for name, value in cookies.items():
                self.session.cookies.set(name, value, domain='.deepseek.com')
            
            return True
    
    def validate_session(self):
        if PLATFORM == "deepseek":
            test_url = f"{DEEPSEEK_URL}/api/v0/models"
        elif PLATFORM == "claude":
            test_url = f"{CLAUDE_URL}/api/organizations"
        elif PLATFORM == "gemini":
            test_url = f"{GEMINI_URL}/api/auth/session"
        else:  # chatgpt
            test_url = f"{CHATGPT_URL}/api/auth/session"
            
        response = self.session.get(test_url)
        
        if response.status_code == 200:
            return True
        elif response.status_code == 401:
            self.print_message("⚠️ Sesión expirada. Reautenticando...", 'warning')
            return self.login()
        else:
            self.print_message(f"❌ Error validando sesión: {response.status_code}", 'error')
            return False
    
    def encode_file(self, file_path):
        if not os.path.exists(file_path):
            self.print_message(f"❌ Archivo no encontrado: {file_path}", 'error')
            return None
        
        file_name = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        if not mime_type:
            mime_type = "application/octet-stream"
        
        with open(file_path, "rb") as file:
            file_data = base64.b64encode(file.read()).decode("utf-8")
        
        return {
            "file_name": file_name,
            "file_type": mime_type,
            "file_size": os.path.getsize(file_path),
            "data": file_data
        }
    
    def send_message(self, message, files=None):
        if PLATFORM == "deepseek":
            url = f"{DEEPSEEK_URL}/api/v0/chat/completions"
        elif PLATFORM == "claude":
            url = f"{CLAUDE_URL}/api/chat"
        elif PLATFORM == "gemini":
            url = f"{GEMINI_URL}/api/generate_content"
        else:  # chatgpt
            url = f"{CHATGPT_URL}/backend-api/conversation"
        
        # Construir el payload
        payload = {
            "messages": [{"role": "user", "content": message}],
            "model": MODEL,
            "temperature": 0.7,
            "max_tokens": 4096,
            "stream": True,
            "conversation_id": self.conversation_id
        }
        
        # Adjuntar archivos si existen
        if files:
            payload["files"] = [self.encode_file(f) for f in files if self.encode_file(f)]
        
        try:
            # Iniciar la solicitud de streaming
            with self.session.post(url, json=payload, stream=True, timeout=60) as response:
                if response.status_code != 200:
                    if response.status_code == 401 and self.login():
                        return self.send_message(message, files)
                    else:
                        return f"❌ Error HTTP {response.status_code}: {response.text}", ""
                
                full_response = ""
                self.streaming_active = True
                self.stop_stream.clear()
                
                for line in response.iter_lines():
                    if self.stop_stream.is_set():
                        break
                    
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data:'):
                            json_str = decoded_line[5:].strip()
                            
                            if json_str == "[DONE]":
                                break
                            
                            try:
                                data = json.loads(json_str)
                                if 'choices' in data and data['choices']:
                                    delta = data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    
                                    if content:
                                        full_response += content
                                        self.stream_queue.put(content)
                                    
                                    # Actualizar conversation_id
                                    if 'conversation_id' in data:
                                        self.conversation_id = data['conversation_id']
                                        self.save_session()
                            
                            except json.JSONDecodeError:
                                pass
                
                self.streaming_active = False
                return full_response, self.conversation_id
        
        except Exception as e:
            self.streaming_active = False
            return f"❌ Excepción: {str(e)}", ""
    
    def print_message(self, message, message_type='system'):
        color = COLORS.get(message_type, 'white')
        prefix = ""
        
        if message_type == 'user':
            prefix = "👤 Tú: "
        elif message_type == 'assistant':
            prefix = "🤖 DeepSeek: "
        elif message_type == 'system':
            prefix = "⚙️ Sistema: "
        elif message_type == 'warning':
            prefix = "⚠️ "
        elif message_type == 'error':
            prefix = "❌ Error: "
        
        sys.stdout.write(f"{color}{prefix}{message}{COLORS['reset']}\n")
        sys.stdout.flush()
    
    def print_stream(self):
        while self.streaming_active or not self.stream_queue.empty():
            try:
                chunk = self.stream_queue.get(timeout=0.1)
                sys.stdout.write(chunk)
                sys.stdout.flush()
                self.stream_queue.task_done()
            except queue.Empty:
                pass
    
    def highlight_code(self, text):
        # Detectar bloques de código
        pattern = r'```(\w+)\n(.*?)```'
        
        def replace_code(match):
            language = match.group(1)
            code = match.group(2)
            
            try:
                lexer = get_lexer_by_name(language, stripall=True)
                formatter = TerminalFormatter()
                highlighted = highlight(code, lexer, formatter)
                return highlighted
            except:
                return f"\n{COLORS['cyan']}```{language}\n{code}```{COLORS['reset']}\n"
        
        return re.sub(pattern, replace_code, text, flags=re.DOTALL)
    
    def choose_platform(self):
        while True:
            self.print_message("\n" + "="*50, 'system')
            self.print_message(f"🌟 {APP_COMPANY} 🌟", 'brand')
            self.print_message("Selección de Modelo de IA", 'system')
            self.print_message("=" * 50, 'system')
            self.print_message("\nModelos disponibles:", 'system')
            self.print_message("1. DeepSeek Chat - IA Avanzada", 'system')
            self.print_message("2. Claude.ai - Asistente Antropic", 'system')
            self.print_message("3. Google Gemini - IA de Google", 'system')
            self.print_message("4. ChatGPT - OpenAI GPT", 'system')
            choice = input(f"{COLORS['yellow']}Selecciona un modelo (1/2/3/4): {COLORS['reset']}").strip()
            
            if choice == "1":
                global PLATFORM
                PLATFORM = "deepseek"
                break
            elif choice == "2":
                global PLATFORM
                PLATFORM = "claude"
                break
            elif choice == "3":
                global PLATFORM
                PLATFORM = "gemini"
                break
            elif choice == "4":
                global PLATFORM
                PLATFORM = "chatgpt"
                break
            else:
                self.print_message("❌ Opción no válida. Por favor elige 1, 2, 3 o 4.", 'error')

    def run(self):
        self.choose_platform()
        
        if not self.validate_session():
            self.print_message("❌ No se pudo validar la sesión. Saliendo.", 'error')
            return
        
        self.save_session()
        
        self.print_message("\n" + "="*50, 'system')
        self.print_message("🌟 PAPIWEB DESARROLLOS INFORMÁTICOS 🌟", 'system')
        self.print_message("Terminal Chat Multimodelo - Versión 1.0", 'system')
        self.print_message("=" * 50, 'system')
        self.print_message("\n💬 Asistente Virtual Inteligente", 'system')
        self.print_message("Desarrollado por Papiweb © 2025\n", 'system')
        self.print_message("Comandos disponibles:", 'system')
        self.print_message("  /reset  - Reiniciar conversación", 'system')
        self.print_message("  /model  - Cambiar modelo (deepseek-chat, deepseek-coder)", 'system')
        self.print_message("  /attach - Adjuntar archivo como contexto", 'system')
        self.print_message("  /exit   - Salir del programa", 'system')
        self.print_message("  Ctrl+C  - Interrumpir generación\n", 'system')
        self.print_message("Soporte técnico: soporte@papiweb.com\n", 'system')
        
        while True:
            try:
                user_input = prompt(
                    f"{COLORS['blue']}👤 Tú:{COLORS['reset']} ",
                    history=FileHistory(HISTORY_FILE),
                    key_bindings=self.key_bindings,
                    multiline=False
                ).strip()
                
                if not user_input:
                    continue
                
                # Comandos especiales
                if user_input.startswith('/'):
                    if user_input == '/reset':
                        self.conversation_id = ""
                        self.message_history = []
                        self.print_message("🔄 Conversación reiniciada", 'system')
                        continue
                    elif user_input.startswith('/model '):
                        new_model = user_input.split(' ', 1)[1]
                        MODEL = new_model
                        self.print_message(f"🔄 Modelo cambiado a: {MODEL}", 'system')
                        continue
                    elif user_input.startswith('/attach '):
                        file_path = user_input.split(' ', 1)[1]
                        if os.path.exists(file_path):
                            self.print_message(f"📎 Archivo adjuntado: {file_path}", 'system')
                            # Guardar para enviar en el próximo mensaje
                            files_to_attach = [file_path]
                        else:
                            self.print_message(f"❌ Archivo no encontrado: {file_path}", 'error')
                        continue
                    elif user_input == '/exit':
                        break
                
                # Manejar archivos adjuntos
                files_to_attach = []
                
                self.print_message("", 'assistant')  # Nueva línea para la respuesta
                
                # Iniciar hilo para mostrar el stream
                self.stream_queue = queue.Queue()
                stream_thread = threading.Thread(target=self.print_stream, daemon=True)
                stream_thread.start()
                
                # Enviar mensaje
                full_response, conv_id = self.send_message(user_input, files_to_attach)
                
                # Esperar a que termine el stream
                while self.streaming_active:
                    time.sleep(0.1)
                
                # Procesar respuesta completa
                if full_response and not full_response.startswith('❌'):
                    # Guardar en historial
                    self.message_history.append({"role": "user", "content": user_input})
                    self.message_history.append({"role": "assistant", "content": full_response})
                    
                    # Mostrar respuesta formateada
                    self.print_message("\n\n💎 Respuesta formateada:", 'system')
                    formatted_response = self.highlight_code(full_response)
                    sys.stdout.write(formatted_response)
                    sys.stdout.write("\n\n")
                    sys.stdout.flush()
                
                files_to_attach = []  # Resetear archivos adjuntos
            
            except KeyboardInterrupt:
                self.stop_stream.set()
                self.print_message("\n🔁 Comando interrumpido", 'warning')
                continue
            except EOFError:
                self.print_message("\n👋 Sesión finalizada", 'system')
                break
            except Exception as e:
                self.print_message(f"❌ Error: {str(e)}", 'error')
                continue

if __name__ == "__main__":
    terminal = DeepSeekTerminal()
    terminal.run()