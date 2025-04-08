import numpy as np
import sounddevice as sd
from obsws_python import ReqClient
import time

# OBS connection info
HOST = "192.168.0.28"
PORT = 4455

# OBS source names
SOURCE_CLOSED = "mouth_closed"
SOURCE_OPEN = "mouth_open"
THRESHOLD = 0.015

# OBS connection
ws = ReqClient(host=HOST, port=PORT)

def set_avatar_state(is_talking):
    scene_name = "Scene"
    scene_items = ws.get_scene_item_list(name=scene_name).scene_items

    for source, is_visible in [(SOURCE_OPEN, is_talking), (SOURCE_CLOSED, not is_talking)]:
        visible = bool(is_visible)
        item_id = next((item['sceneItemId'] for item in scene_items if item['sourceName'] == source), None)
        if item_id is not None:
            ws.set_scene_item_enabled(
                scene_name=scene_name,
                item_id=item_id,
                enabled=visible
            )

# Try detecting audio on a device
def test_device(device_index):
    detected = []

    def temp_callback(indata, frames, time_info, status):
        volume = np.linalg.norm(indata) / len(indata)
        if volume > THRESHOLD:
            detected.append(True)

    try:
        with sd.InputStream(device=device_index, channels=1, callback=temp_callback):
            print(f"Testing device {device_index}: {sd.query_devices(device_index)['name']}")
            time.sleep(1.0)  # Give it a second to pick up sound
        return bool(detected)
    except Exception as e:
        print(f"Device {device_index} failed: {e}")
        return False

# Find a working input device
def find_working_input_device():
    print("Searching for a working audio input device...")
    for i, dev in enumerate(sd.query_devices()):
        if dev['max_input_channels'] >= 1:
            if test_device(i):
                print(f"✅ Using device {i}: {dev['name']}")
                return i
    raise RuntimeError("No suitable input device found.")

# Main detection loop
def run_voice_detection(device_index):
    print("Starting voice detection...")
    set_avatar_state(False)

    def audio_callback(indata, frames, time_info, status):
        volume = np.linalg.norm(indata) / len(indata)
        is_talking = volume > THRESHOLD
        set_avatar_state(is_talking)

    with sd.InputStream(callback=audio_callback, device=device_index, channels=1):
        while True:
            print('Sleeping')
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        input_device = find_working_input_device()
        run_voice_detection(input_device)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        ws.disconnect()
