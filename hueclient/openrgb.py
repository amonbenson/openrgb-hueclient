import time
import logging
import threading
from openrgb import OpenRGBClient as _OpenRGBClient
from openrgb.utils import RGBColor

class OpenRGBClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 6742, *, reconnect_attempts: int = 10, update_rate: int = 10, transition_speed: float = 1.0):
        self._host = host
        self._port = port
        self._reconnect_attempts = reconnect_attempts
        self._update_rate = update_rate

        self._thread = threading.Thread(target=self._run)
        self._stop_event = threading.Event()

        self._from_colors: list[RGBColor] = []
        self._to_colors: list[RGBColor] = []
        self._colors: list[RGBColor] = []
        self._lock = threading.Lock()

        self._transition_progress = 0.0
        self._transition_speed = transition_speed

    def _run(self):
        # try to connect a few times
        client = None
        for _ in range(self._reconnect_attempts):
            if self._stop_event.is_set():
                break

            try:
                client = _OpenRGBClient(self._host, self._port)
                client.connect()
                break
            except Exception as e:
                logging.error(f"Failed to connect to OpenRGB: {e}")

            self._stop_event.wait(1)

        if client is None:
            logging.error("Too many connection attempts, exiting...")
            return

        # get all zones from all devices that support direct updating
        zones = [zone for device in client.ee_devices for zone in device.zones]

        while not self._stop_event.is_set():
            with self._lock:
                # update color transition
                for i, (from_color, to_color) in enumerate(zip(self._from_colors, self._to_colors)):
                    self._transition_progress += self._transition_speed / self._update_rate

                    if self._transition_progress >= 1.0:
                        self._transition_progress = 1.0
                        self._colors[i] = to_color
                    else:
                        r = int(from_color.red + (to_color.red - from_color.red) * self._transition_progress)
                        g = int(from_color.green + (to_color.green - from_color.green) * self._transition_progress)
                        b = int(from_color.blue + (to_color.blue - from_color.blue) * self._transition_progress)
                        self._colors[i] = RGBColor(r, g, b)

                # update zones
                for i, zone in enumerate(zones):
                    if self._colors:
                        color_index = i % len(self._colors)
                        color = self._colors[color_index]
                    else:
                        color = RGBColor(0, 0, 0)

                    zone.set_color(color, fast=True)

            # show changes
            for zone in zones:
                zone.show()

            # wait for next update
            self._stop_event.wait(1 / self._update_rate)

    def start(self):
        self._thread.start()

    def stop(self):
        # clear colors and wait for transition to finish
        self.clear_colors()
        time.sleep(5 / self._update_rate)

        self._stop_event.set()
        self._thread.join()

    def set_colors(self, next_colors: list[RGBColor]):
        with self._lock:
            # set to colors
            self._to_colors = next_colors

            # resize current colors array
            if len(next_colors) < len(self._colors):
                self._colors = self._colors[:len(next_colors)]
            elif len(next_colors) > len(self._colors):
                self._colors += [RGBColor(0, 0, 0)] * (len(next_colors) - len(self._colors))
                
            # set from colors
            self._from_colors = self._colors.copy()

            # reset progress
            self._transition_progress = 0.0

    def clear_colors(self):
        self.set_colors([])
