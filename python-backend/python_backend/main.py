import asyncio
import logging
import json
from enum import Enum

# bleak_fsm uses async internally,
# and this webserver is async, so nest_asyncio is needed to nest async loops.
import nest_asyncio
nest_asyncio.apply()

logging.basicConfig(level=logging.INFO)

from websockets.server import serve

from bleak_fsm import machine, BleakModel

from pycycling.sterzo import Sterzo

websocket = None

send_scan_results_event = asyncio.Event()

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
        logging.info(f"Sending scan results: {serialized_devices}" )
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
    
    disconnect_event = asyncio.Event() # Set when frontend requests to close all connections

    models = [] # BleakModel instances

    async for message in websocket:
        json_parsed = json.loads(message)
        logging.debug(f"Received websocket message. Event name: '{json_parsed['event']}'. Data: '{json_parsed['data']}'")
        event = json_parsed["event"]
        if event == "scan_start":
            send_scan_results_event.clear()
            await BleakModel.start_scan()
            asyncio.create_task(send_scan_results())
        elif event == "scan_stop":
            send_scan_results_event.set()
            logging.debug("Stopping BLE scan")
            await BleakModel.stop_scan()
        elif event == "connect":
            logging.debug(f"Connecting to device {json_parsed['data']['device']}")
            model = BleakModel()
            machine.add_model(model)
            await model.set_target(json_parsed["data"]["device"])
            model.wrap = lambda client: Sterzo(client)
            model.set_measurement_handler = lambda client: client.set_steering_measurement_callback(handle_sterzo_measurement)
            model.enable_notifications = lambda client: client.enable_steering_measurement_notifications()
            model.disable_notifications = lambda client: client.disable_steering_measurement_notifications()

            await model.connect()
            await model.stream()

            # register it so that it can be cleaned up later
            models.append(model)
        elif event == "disconnect":
            disconnect_event.set()

            logging.debug("Disconnecting from all devices")
            [await model.clean_up() for model in models]
            models = []
            disconnect_event.clear() # Clear the event so that it can be used again
        else:
            logging.warning(f"WARNING: This message has an unknown event name.")
            
    [await model.clean_up() for model in models]

async def start_server():
    global webserver
    async with serve(main, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(start_server())
