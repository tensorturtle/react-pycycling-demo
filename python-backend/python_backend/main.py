# Python standard library imports
from enum import Enum
from typing import Dict, Tuple
import json
import asyncio

# Third party library imports
from websockets.server import serve
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

# Pycycling imports
from pycycling.sterzo import Sterzo

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
            "mac": address,
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

def detection_callback(device, advertisement_data):
    # Here, we're adding device information to the global list
    # Note 'BLEDevice' is a BleakScanner object, which is not JSON serializable, so don't send that to client.
    # But we need it to connect to the device later (simply using the address text doesn't work)
    ble_devices[device.address] = (device, advertisement_data)
    # we eagerly send the results of the scan to the client through websocket
    async def eagerly_send_scan_results():
        # send `discovered_devices` except for the `BLEDevice` key
        print(f"Sending websocket message. Event name: 'scan_reply'. Data: {serialize(ble_devices)}")
        await websocket.send(json.dumps({"event": "scan_reply", "data": serialize(ble_devices)}))
    if websocket is not None:
        asyncio.create_task(eagerly_send_scan_results())
    else:
        print("No active websocket connection.")

async def scan_bluetooth():
    ble_devices.clear()
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

async def connect_to_sterzo(sterzo_device: BLEDevice, disconnect_event: asyncio.Event):
    async with BleakClient(sterzo_device) as client:
        def steering_handler(steering_angle):
            # Since websocket.send() is a coroutine, we need to create a task to run it asynchronously inside the existing coroutine
            async def websocket_send(steering_angle):
                print(f"Sending websocket message. Event name: 'steering_angle'. Data: {steering_angle}")
                await websocket.send(json.dumps({"event": "steering_angle", "data": steering_angle}))
            asyncio.create_task(websocket_send(steering_angle))

        await client.is_connected()

        async def websocket_send_connection_initiated():
            print(f"Sending websocket message. Event name: 'sterzo_connected'. Data: (empty)")
            await websocket.send(json.dumps({"event": "sterzo_connected", "data": ""}))
        asyncio.create_task(websocket_send_connection_initiated())

        sterzo = Sterzo(client)
        sterzo.set_steering_measurement_callback(steering_handler)
        await sterzo.enable_steering_measurement_notifications()
        print("Enabled steering measurement notifications")
        await disconnect_event.wait() # Wait until the disconnect event is set
        print("Disconnecting from Sterzo")
        await sterzo.disable_steering_measurement_notifications()
        await client.disconnect()

        async def websocket_send_connection_terminated():
            print(f"Sending websocket message. Event name: 'sterzo_disconnected'. Data: (empty)")
            await websocket.send(json.dumps({"event": "sterzo_disconnected", "data": ""}))
        asyncio.create_task(websocket_send_connection_terminated())


async def echo(websocket_):
    # for our convenience, we elevate the websocket to a global variable
    global websocket
    websocket = websocket_

    disconnect_event = asyncio.Event() # This event will be set when the frontend requests to close all connections
    # See: https://docs.python.org/3/library/asyncio-sync.html#event


    # iterator ends when the connection is closed
    async for message in websocket:
        json_parsed = json.loads(message)
        print(f"Received websocket message. Event name: '{json_parsed['event']}'. Data: '{json_parsed['data']}'")
        match json_parsed["event"]:
            case "scan_start":
                _ble_devices = await scan_bluetooth() # this routine sends the scan results to the client through the detection_callback
            case "connect": # Given a device address, connect to it and stream data from it
                data = json_parsed["data"]
                service = data["service"]
                device_address = data["device"]
                print(f"Connecting to device {device_address} with service {service}")
                device, _advertisement_data = ble_devices[device_address]

                if service == "STERZO":
                    sterzo_task = asyncio.create_task(connect_to_sterzo(device, disconnect_event))
                else:
                    print(f"WARNING: This service has not been implemented yet.")

            case "disconnect": # Client wants to disconnect from all devices and stop all BLE operations
                print("Disconnecting from all devices")
                disconnect_event.set()
                await sterzo_task
                disconnect_event.clear() # Clear the event so that it can be used again

            case _:
                print(f"WARNING: This message has an unknown event name.")

async def main():
    global websocket
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

print("Server is running")
asyncio.run(main())
