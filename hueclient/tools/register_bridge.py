import argparse
from ..hue import HueBridge

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new user on the Hue bridge")
    parser.add_argument("bridge_ip", help="The IP address of the Hue bridge")
    parser.add_argument("device_name", help="The name of the device to create a user for")
    parser.add_argument("device_mac", help="The MAC address of the device to create a user for")
    args = parser.parse_args()

    result = HueBridge.register(args.bridge_ip, args.device_name, args.device_mac, link_attempts=120)
    print(result["username"])
