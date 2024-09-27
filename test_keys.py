import keyboard

try:
    while True:
        print(keyboard.read_event().to_json())
except KeyboardInterrupt:
    pass