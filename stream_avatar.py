import numpy as np
import sounddevice as sd
from obsws_python import ReqClient
import time

print(sd.query_devices())

# OBS connection info
HOST = "192.168.0.28"
PORT = 4455

# OBS source names
SOURCE_CLOSED = "mouth_closed"
SOURCE_OPEN = "mouth_open"
THRESHOLD = 0.015

# Connect to OBS
ws = ReqClient(host=HOST, port=PORT)

def set_avatar_state(is_talking):
    scene_name = "Scene"

    # Get scene items
    scene_items = ws.get_scene_item_list(name=scene_name).scene_items

    for source, is_visible in [(SOURCE_OPEN, is_talking), (SOURCE_CLOSED, not is_talking)]:
        visible = bool(is_visible)  # Convert numpy.bool_ to native bool
        # Find the scene item ID matching the source name
        item_id = next((item['sceneItemId'] for item in scene_items if item['sourceName'] == source), None)
        if item_id is not None:
            ws.set_scene_item_enabled(
                scene_name=scene_name,
                item_id=item_id,
                enabled=visible
            )

# Audio callback
def audio_callback(indata, frames, time_info, status):
    volume = np.linalg.norm(indata) / len(indata)
    is_talking = volume > THRESHOLD
    set_avatar_state(is_talking)

# Start audio input stream
try:
    print("Starting voice detection...")
    set_avatar_state(False)
    with sd.InputStream(callback=audio_callback, device=13):
        while True:
            time.sleep(0.1)
except KeyboardInterrupt:
    print("Stopping...")
finally:
    ws.disconnect()
