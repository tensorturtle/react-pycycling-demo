from enum import Enum
import asyncio

from bleak import BleakClient
from pycycling.sterzo import Sterzo
from pycycling.fitness_machine_service import FitnessMachineService

class BLECyclingService(Enum):
    '''
    BLE Services and Characteristics that are broadcasted by the devices themselves when being scanned.

    Some are assigned: https://www.bluetooth.com/specifications/assigned-numbers/
    Others (like STERZO) are just made up by the manufacturer.
    '''
    STERZO = "347b0001-7635-408b-8918-8ff3949ce592"
    FITNESS = "00001826-0000-1000-8000-00805f9b34fb"

def filter_cycling_accessories(devices):
    relevant_devices = {
        'sterzos': [],
        'smart_trainers': [],
    }

    for k,v in devices.items():
        bledevice, advertisement_data = v
        services = advertisement_data.service_uuids

        if BLECyclingService.STERZO.value in services: 
            relevant_devices['sterzos'].append(bledevice)
        if BLECyclingService.FITNESS.value in services:
            relevant_devices['smart_trainers'].append(bledevice)
    print(f"Found {len(relevant_devices['sterzos'])} sterzos and {len(relevant_devices['smart_trainers'])} smart trainers")
    return relevant_devices

class PycyclingInput:
    def __init__(self, sterzo_device, powermeter_device, on_steering_update, on_power_update, on_speed_update, on_cadence_update):
        '''
        sterzo_device: BLEDevice
        powermeter_device: BLEDevice
        on_steering_update: callback function (used to send steering angle to carla client)
        on_power_update: callback function (used to send power to carla client)
        '''
        self.sterzo_device = sterzo_device
        self.powermeter_device = powermeter_device
        self.on_steering_update = on_steering_update
        self.on_power_update = on_power_update
        self.on_speed_update = on_speed_update
        self.on_cadence_update = on_cadence_update

        self.ftms = None
        self.ftms_max_resistance = None
        self.ftms_desired_resistance = 0
    async def run_all(self):
        loop = asyncio.get_running_loop()
        loop.create_task(self.connect_to_sterzo())
        #loop.create_task(self.connect_to_fitness_machine())
        await asyncio.Future() # run forever
    async def connect_to_sterzo(self):
        async with BleakClient(self.sterzo_device) as client:
            await client.is_connected()
            sterzo = Sterzo(client)
            sterzo.set_steering_measurement_callback(self.on_steering_update)
            await sterzo.enable_steering_measurement_notifications()
            await asyncio.Future() # run forever
    async def connect_to_fitness_machine(self):
        async with BleakClient(self.powermeter_device, timeout=20) as client: 
            # long timeout is required. Somehow FTMS takes longer to setup.
            await client.is_connected()

            self.ftms = FitnessMachineService(client)
            print("Connected to FTMS")

            res_levels = await self.ftms.get_supported_resistance_level_range()
            print(f"Resistance level range: {res_levels}")
            self.ftms_max_resistance = res_levels.maximum_resistance

            def print_control_point_response(message):
                pass
                # print("Received control point response:")
                # print(message)
                # print()
            self.ftms.set_control_point_response_handler(print_control_point_response)

            
            def print_indoor_bike_data(data):
                # print("Received indoor bike data:")
                # print(data)
                power = data.instant_power
                self.on_power_update(power)

                speed = data.instant_speed
                self.on_speed_update(speed)

                cadence = data.instant_cadence
                self.on_cadence_update(cadence)

            self.ftms.set_indoor_bike_data_handler(print_indoor_bike_data)
            await self.ftms.enable_indoor_bike_data_notify()

            supported_features = await self.ftms.get_fitness_machine_feature()

            if not supported_features.resistance_level_supported:
                print("WARNING: Resistance level not supported on this smart trainer.")
                return

            if not supported_features.resistance_level_supported:
                print("WARNING: Resistance level not supported on this smart trainer.")
                return
            
            await self.ftms.enable_control_point_indicate()
            await self.ftms.request_control()
            await self.ftms.reset()

            while True:
                if self.ftms_desired_resistance > self.ftms_max_resistance:
                    print("Warning: Desired resistance is greater than max resistance. Setting to max resistance.")
                    self.ftms_desired_resistance = self.ftms_max_resistance
                #print(f"Setting resistance to {self.ftms_desired_resistance}")
                await self.ftms.set_target_resistance_level(self.ftms_desired_resistance)
                await asyncio.sleep(1)
