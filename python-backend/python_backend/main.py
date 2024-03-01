import json
import asyncio
from websockets.server import serve
from bleak import BleakScanner

# Define a global list to store discovered devices
discovered_devices = {}

# Define the callback function for the BleakScanner
def detection_callback(device, advertisement_data):
    # Here, we're adding device information to the global list
    discovered_devices.update({device.address:{"name": device.name, "RSSI": advertisement_data.rssi}})

# This function will perform the Bluetooth scan
async def scan_bluetooth():
    # Clear previous devices
    discovered_devices.clear()
    # Define a stop event for the scanner
    stop_event = asyncio.Event()

    # This will automatically stop the scanner after 10 seconds
    def stop_scan():
        stop_event.set()

    # Start the scanner with the detection callback
    async with BleakScanner(detection_callback) as scanner:
        await asyncio.sleep(3)  # Scan for 2 seconds
        stop_scan()

    # Return the list of discovered devices
    return discovered_devices

async def echo(websocket):
    async for message in websocket:
        json_parsed = json.loads(message)
        match json_parsed["event"]:
            case "scan":
                print(f"Received scan message: {json_parsed['data']}")
                # Perform Bluetooth scan
                devices = await scan_bluetooth()
                # Send the list of discovered devices back to the client
                await websocket.send(json.dumps({"event": "scan", "data": devices}))

            case _:
                print(f"Received unknown message: {json_parsed['event']}")
                await websocket.send(json.dumps({"event": "error", "data": "Unknown event"}))

async def main():
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

print("Server is running")
asyncio.run(main())
