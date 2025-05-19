import pynput.mouse as mouse
import pynput.keyboard as keyboard
import time
import pyautogui

is_recording = False
events = []

def on_press(key):
    global is_recording, events
    try:
        if key == keyboard.Key.f7:
            if not is_recording:
                is_recording = True
                events = []
                print("Recording started. Press F8 to stop.")
        elif key == keyboard.Key.f8:
            if is_recording:
                is_recording = False
                print("Recording stopped. Generating code...")
                generate_code(events)
                return False
    except AttributeError:
        pass

def on_move(x, y):
    if is_recording:
        events.append(('move', x, y, time.time()))

def on_click(x, y, button, pressed):
    if is_recording:
        events.append(('click', x, y, button, pressed, time.time()))

def on_scroll(x, y, dx, dy):
    if is_recording:
        events.append(('scroll', x, y, dx, dy, time.time()))

def generate_code(events):
    if not events:
        print("No events recorded.")
        return

    code = [
        "import pyautogui",
        "import time",
        "",
        "pyautogui.PAUSE = 0",
        ""
    ]

    prev_time = events[0][-1]
    
    for event in events:
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
            btn_name = button.name
            action = 'mouseDown' if pressed else 'mouseUp'
            code.append(f"pyautogui.{action}({x}, {y}, button='{btn_name}')")
        elif event[0] == 'scroll':
            x, y, dx, dy = event[1], event[2], event[3], event[4]
            code.append(f"pyautogui.scroll({int(dy * 100)})")

    with open('recorded_script.py', 'w') as f:
        f.write('\n'.join(code))
    print("Script generated: 'recorded_script.py'")

print("Presiona F7 para iniciar la grabación y F8 para detenerla")
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()
keyboard_listener.join()
mouse_listener.stop()