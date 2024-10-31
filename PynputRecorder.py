import json
from pynput import mouse

# List to store the recorded events
recorded_events = []
last_position = None
move_threshold = 10  # Minimum distance in pixels to record a movement

def distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

def on_move(x, y):
    global last_position
    current_position = (x, y)
    if last_position is None or distance(last_position, current_position) > move_threshold:
        last_position = current_position
        recorded_events.append(('move', x, y))
        print('Pointer moved to {0}'.format((x, y)))

def on_click(x, y, button, pressed):
    event_type = 'pressed' if pressed else 'released'
    recorded_events.append((event_type, x, y, str(button)))
    print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
    if button == mouse.Button.right and pressed:
        # Stop listener when right-click is pressed
        return False

def on_scroll(x, y, dx, dy):
    recorded_events.append(('scroll', x, y, dx, dy))
    print('Scrolled at {0}'.format((x, y)))

# Collect events until a right-click is made
with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
    listener.join()

# Save the recorded events to a file
with open('recorded_events.json', 'w') as f:
    json.dump(recorded_events, f)
