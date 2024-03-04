# Python standard library imports
from enum import Enum
from typing import Dict, Tuple
import json
import asyncio

# Third party library imports
from websockets.server import serve
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

# Define a global list to store discovered devices
ble_devices: Dict[str, Tuple[BLEDevice, AdvertisementData]] = {} # key is address of the device. We store the BLEDevice object because we need it to connect to it later.

websocket = None  # Global definition

class BLECyclingService(Enum):
    '''
    BLE Services and Characteristics that are broadcasted by the devices themselves when being scanned.

    Some are assigned: https://www.bluetooth.com/specifications/assigned-numbers/
    Others (like STERZO) are just made up by the manufacturer.
    '''
    STERZO = "347b0001-7635-408b-8918-8ff3949ce592"
    FITNESS = "00001826-0000-1000-8000-00805f9b34fb"
    POWERMETER = "00001818-0000-1000-8000-00805f9b34fb"

def serialize(ble_devices):
    # Simplify the ble_devices dictionary to a JSON serializable format for sending scan results to client 
    discovered_devices = {}
    for address, (device, advertisement_data) in ble_devices.items():
        discovered_devices[address] = {
            "name": device.name, 
            "RSSI": advertisement_data.rssi,
            "services": get_implemented_services(advertisement_data)
            }
    return discovered_devices

def get_implemented_services(advertisement_data):
    # return a a list of the BLECyclingService that the device implements
    implemented_services = []
    for service in BLECyclingService:
        if service.value in advertisement_data.service_uuids:
            implemented_services.append(service.name)
    return implemented_services

# Define the callback function for the BleakScanner
def detection_callback(device, advertisement_data):
    # Here, we're adding device information to the global list
    # Note 'BLEDevice' is a BleakScanner object, which is not JSON serializable, so don't send that to client.
    # But we need it to connect to the device later (simply using the address text doesn't work)
    ble_devices[device.address] = (device, advertisement_data)
    # we eagerly send the results of the scan to the client through websocket
    async def eagerly_send_scan_results():
        # send `discovered_devices` except for the `BLEDevice` key
        await websocket.send(json.dumps({"event": "scan_reply", "data": serialize(ble_devices)}))

        # print(f"Eagerly Sending websocket message. Event name: 'scan_reply'. Data: {discovered_devices}")
        # await websocket.send(json.dumps({"event": "scan_reply", "data": discovered_devices}))
    if websocket is not None:
        asyncio.create_task(eagerly_send_scan_results())
    else:
        print("No active websocket connection.")

# This function will perform the Bluetooth scan
async def scan_bluetooth():
    # Clear previous devices
    ble_devices.clear()
    # Define a stop event for the scanner
    stop_event = asyncio.Event()

    # This will automatically stop the scanner after the given number of seconds
    def stop_scan():
        stop_event.set()
        async def send_scan_finished_message():
            print(f"Sending websocket message. Event name: 'scan_finished'. Data: (empty)")
            await websocket.send(json.dumps({"event": "scan_finished", "data": ""}))
        asyncio.create_task(send_scan_finished_message())

    # Start the scanner with the detection callback
    async with BleakScanner(detection_callback) as scanner:
        await asyncio.sleep(3)  # Scan for 2 seconds
        stop_scan()

    # Return the list of discovered devices
    return ble_devices

async def echo(websocket_):
    # for our convenience, we elevate the websocket to a global variable
    global websocket
    websocket = websocket_

    # iterator ends when the connection is closed
    async for message in websocket:
        json_parsed = json.loads(message)
        print(f"Received websocket message. Event name: '{json_parsed['event']}'. Data: '{json_parsed['data']}'")
        match json_parsed["event"]:
            case "scan_start":
                # Perform Bluetooth scan
                ble_devices = await scan_bluetooth()

                # # Send the overall list of discovered devices back to the client
                # print(f"Sending websocket message. Event name: 'scan_reply'. Data: {devices}")
                # await websocket.send(json.dumps({"event": "scan_reply", "data": devices}))

                # Send the specific list of devices which we have implemented the ability to read from
                # that is, devices which implement specific bluetooth service UUIDs
                connectable_devices = None
                print(f"Sending websocket message. Event name: 'connectable_devices'. Data: {connectable_devices}")
                await websocket.send(json.dumps({"event": "connectable_devices", "data": connectable_devices}))
            case _:
                print(f"WARNING: This message has an unknown event name.")

async def main():
    global websocket
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

print("Server is running")
asyncio.run(main())
