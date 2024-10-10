import os
import time
import logging
from dotenv import load_dotenv
from openrgb.utils import RGBColor
from .openrgb import OpenRGBClient
from .hue import HueBridge
from .color import light_state_to_rgb_color

# load environment variables
load_dotenv(".env")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    bridge = HueBridge(
        ip=os.environ["BRIDGE_IP"],
        username=os.environ["BRIDGE_USERNAME"],
        room=os.environ["BRIDGE_ROOM"],
    )
    openrgb = OpenRGBClient(
        host=os.environ["OPENRGB_HOST"],
        port=int(os.environ["OPENRGB_PORT"]),
        update_rate=10,
    )

    def update_lights(states: dict):
        colors = []
        
        # convert each state to an RGB color
        for state in states.values():
            try:
                color = light_state_to_rgb_color(state)
                colors.append(color)
            except Exception as e:
                print(f"Light '{state['metadata']['name']}': {e}")

        # set the colors on the OpenRGB client
        openrgb.set_colors(colors)

    bridge.on_update(update_lights)

    openrgb.start()
    openrgb.clear_colors()

    bridge.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Exiting...")

    openrgb.stop()
    bridge.stop()
