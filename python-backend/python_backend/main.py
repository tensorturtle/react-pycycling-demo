import json
import asyncio
from websockets.server import serve
from bleak import BleakScanner

# Define a global list to store discovered devices
discovered_devices = {}

websocket = None  # Global definition

# Define the callback function for the BleakScanner
def detection_callback(device, advertisement_data):
    # Here, we're adding device information to the global list
    discovered_devices.update({device.address:{"name": device.name, "RSSI": advertisement_data.rssi}})
    # we eagerly send the results of the scan to the client through websocket
    async def eagerly_send_scan_results():
        print(f"Eagerly Sending websocket message. Event name: 'scan_reply'. Data: {discovered_devices}")
        await websocket.send(json.dumps({"event": "scan_reply", "data": discovered_devices}))
    if websocket is not None:
        asyncio.create_task(eagerly_send_scan_results())
    else:
        print("No active websocket connection.")

# This function will perform the Bluetooth scan
async def scan_bluetooth():
    # Clear previous devices
    discovered_devices.clear()
    # Define a stop event for the scanner
    stop_event = asyncio.Event()

    # This will automatically stop the scanner after the given number of seconds
    def stop_scan():
        stop_event.set()
        async def send_scan_finished_message():
            print(f"Sending websocket message. Event name: 'scan_finished'. Data: 'Scan finished'")
            await websocket.send(json.dumps({"event": "scan_finished", "data": "Scan finished"}))
        asyncio.create_task(send_scan_finished_message())

    # Start the scanner with the detection callback
    async with BleakScanner(detection_callback) as scanner:
        await asyncio.sleep(3)  # Scan for 2 seconds
        stop_scan()

    # Return the list of discovered devices
    return discovered_devices

async def echo(websocket_):
    # for our convenience, we elevate the websocket to a global variable
    global websocket
    websocket = websocket_

    # iterator ends when the connection is closed
    async for message in websocket:
        json_parsed = json.loads(message)
        match json_parsed["event"]:
            case "scan_start":
                print(f"Received websocket message. Event name: 'Scan'. Data: '{json_parsed['data']}'")
                # Perform Bluetooth scan
                devices = await scan_bluetooth()
                # Send the list of discovered devices back to the client
                print(f"Sending websocket message. Event name: 'scan_reply'. Data: {devices}")
                await websocket.send(json.dumps({"event": "scan_reply", "data": devices}))

            case _:
                print(f"Received unknown message: {json_parsed['event']}")

async def main():
    global websocket
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

print("Server is running")
asyncio.run(main())
