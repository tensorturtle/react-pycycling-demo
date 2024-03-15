import asyncio
import logging
import json
from enum import Enum

# bleak_fsm uses async internally,
# and this webserver is async, so nest_asyncio is needed to nest async loops.
import nest_asyncio
nest_asyncio.apply()

import transitions

logging.basicConfig(level=logging.INFO)

import websockets
from websockets.server import serve

from bleak_fsm import machine, BleakModel

from pycycling.sterzo import Sterzo

websocket = None

send_scan_results_event = asyncio.Event()
#disconnect_event = asyncio.Event() # Set when frontend requests to close all connections


class BLECyclingService(Enum):
    '''
    BLE Services and Characteristics that are broadcasted by the devices themselves when being scanned.

    Some are assigned: https://www.bluetooth.com/specifications/assigned-numbers/
    Others (like STERZO) are just made up by the manufacturer.
    '''
    STERZO = "347b0001-7635-408b-8918-8ff3949ce592"
    FITNESS = "00001826-0000-1000-8000-00805f9b34fb"
    POWERMETER = "00001818-0000-1000-8000-00805f9b34fb"

def get_implemented_services(advertisement_data):
    # return a a list of the BLECyclingService that the device implements
    implemented_services = []
    for service in BLECyclingService:
        if service.value in advertisement_data.service_uuids:
            implemented_services.append(service.name)
    return implemented_services

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

async def send_scan_results():
    while True:
        discovered_devices = BleakModel.bt_devices
        serialized_devices = serialize(discovered_devices)
        logging.debug(f"Sending scan results: {serialized_devices}" )
        await websocket.send(json.dumps({"event": "scan_reply", "data": serialized_devices}))
        if send_scan_results_event.is_set():
            logging.info("Scan results stopped")
            break
        await asyncio.sleep(0.5)

async def async_send_sterzo_measurement(value):
    await websocket.send(json.dumps({"event": "steering_angle", "data": value}))

def handle_sterzo_measurement(value):
    asyncio.create_task(async_send_sterzo_measurement(value))

async def main(websocket_):
    global websocket
    websocket = websocket_
    
    models = [] # BleakModel instances

    async for message in websocket:
        json_parsed = json.loads(message)
        logging.debug(f"Received websocket message. Event name: '{json_parsed['event']}'. Data: '{json_parsed['data']}'")
        event = json_parsed["event"]
        if event == "scan_start":
            send_scan_results_event.clear()
            logging.debug("Starting BLE scan")
            try:
                await BleakModel.start_scan()
            except:
                logging.error("Failed to start BLE scan. Continuing.")
            asyncio.create_task(send_scan_results())
        elif event == "scan_stop":
            send_scan_results_event.set()
            logging.debug("Stopping BLE scan")
            try:
                await BleakModel.stop_scan()
            except:
                logging.error("Failed to stop BLE scan. Continuing.")
        elif event == "connect":
            logging.debug(f"Connecting to device {json_parsed['data']['device']}")
            model = BleakModel()
            machine.add_model(model)
            model.wrap = lambda client: Sterzo(client)
            model.set_measurement_handler = lambda client: client.set_steering_measurement_callback(handle_sterzo_measurement)
            model.enable_notifications = lambda client: client.enable_steering_measurement_notifications()
            model.disable_notifications = lambda client: client.disable_steering_measurement_notifications()
            if await model.set_target(json_parsed["data"]["device"]):
                logging.info("Successfully set target")
                if await model.connect():
                    logging.info(f"Connected to device {json_parsed['data']['device']}")
                    await model.stream()
                    logging.info(f"Streaming from device {json_parsed['data']['device']}")

            # register it so that it can be cleaned up later
            models.append(model)
        elif event == "disconnect":
            new_models = []
            logging.debug("Disconnecting from all devices")
            for model in models:
                if model.state not in ["Connected", "Streaming"]:
                    logging.warning(f"WARNING: Device {model.target} is not in a state where it can be disconnected. State: {model.state}")
                    new_models.append(model)
                else:
                    await model.clean_up()
            
            models = new_models
        else:
            logging.warning(f"WARNING: This message has an unknown event name.")
            
    for model in models:
        await model.clean_up()

async def start_server():
    global webserver
    async with serve(main, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(start_server())
