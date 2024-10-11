import time
import logging
import threading
import requests

class HueBridge():
    def __init__(self, ip: str, username: str, room: str):
        self._ip = ip
        self._username = username
        self._room = room

        self._session = requests.Session()
        self._session.headers.update({ "hue-application-key": self._username })
        self._session.verify = False

        self._update_callback = None

        self._thread = threading.Thread(target=self._run)
        self._stop_event = threading.Event()

        # disable SSL warnings on missing certificate
        requests.packages.urllib3.disable_warnings(category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

    def _get_request(self, path: str, *args, **kwargs) -> dict:
        response = self._session.get(f"https://{self._ip}{path}", *args, **kwargs)
        response.raise_for_status()
        return response.json()

    def _run(self) -> dict:
        logging.debug("Getting device info...")
        devices = self._get_request("/clip/v2/resource/device")["data"]
        devices = { d["id"]: d for d in devices }

        logging.debug("Getting room info...")
        rooms = self._get_request("/clip/v2/resource/room")["data"]

        # get room resource by name
        room = next((r for r in rooms if r["metadata"]["name"] == self._room), None)
        if not room:
            raise ValueError(f"Room '{self._room}' not found")

        logging.debug("Getting room lights...")
        room_lights = {}
        for child in room["children"]:
            # get the corresponding device if it exists
            rid = child["rid"]
            if rid not in devices:
                continue
            device = devices[rid]

            # get the light service if it exists
            light_service = next((s for s in device["services"] if s["rtype"] == "light"), None)
            if not light_service:
                continue

            # store the light device
            logging.info(f"Found Light: {device['metadata']['name']}")
            device["_light_service_rid"] = light_service["rid"]
            room_lights[rid] = device

        if not room_lights:
            raise ValueError(f"No lights found in room '{self._room}'")

        # get the current state of all lights
        self._light_states = {}
        for rid, light in room_lights.items():
            state = self._get_request(f"/clip/v2/resource/light/{light['_light_service_rid']}")["data"][0]
            self._light_states[rid] = state

        # initial update
        if self._update_callback:
            self._update_callback(self._light_states)

        # poll for updates
        logging.debug("Listening for light state changes...")
        while not self._stop_event.is_set():
            try:
                events = self._get_request("/eventstream/clip/v2", timeout=5)

                updated = False
                for event in events:
                    if event["type"] != "update":
                        continue

                    for update in event["data"]:
                        if update["type"] != "light":
                            continue

                        light_rid = update["owner"]["rid"]
                        if light_rid not in room_lights:
                            continue

                        # get the light
                        light_state = self._light_states[light_rid]
                        logging.debug(f"Light '{light_state['metadata']['name']}' changed")

                        # update the light state
                        attributes = {}
                        if "on" in update:
                            attributes["on"] = update["on"]
                        if "color" in update:
                            attributes["color"] = update["color"]
                        if "dimming" in update:
                            attributes["dimming"] = update["dimming"]
                        self._light_states[light_rid] = {**light_state, **attributes}

                        # update the zones
                        updated = True

                # invoke the update callback
                if updated and self._update_callback:
                    self._update_callback(self._light_states)

            except requests.Timeout:
                pass
            except requests.RequestException as e:
                logging.error(f"Request failed: {e}")
                time.sleep(5)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join()

    def on_update(self, callback):
        self._update_callback = callback

    @staticmethod
    def register(ip: str, device_name: str, device_mac: str, link_attempts: int = 60) -> dict:
        requests.packages.urllib3.disable_warnings(category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

        for _ in range(link_attempts):
            response = requests.post(f"https://{ip}/api", json={
                "devicetype": f"{device_name}#{device_mac}",
                "generateclientkey": True,
            }, verify=False)
            response.raise_for_status()
            data = response.json()[0]

            if "success" in data:
                return data["success"]
            elif "error" in data:
                if data["error"]["type"] == 101:
                    logging.debug("Link button not pressed, retrying...")
                else:
                    raise ValueError(f"Link failed: {data['error']['description']}")

            time.sleep(1)
