import React, { useState, useEffect } from 'react';

function ExampleDevice({sendJsonMessage, service, devices, deviceConnected, liveData}) {
    // This function is reponsible for requesting and displaying the data from each device.
    // The parent element doesn't have that information
    const [selectedAddress, setSelectedAddress] = useState('');

    // We want to make sure that if there is just one device, it is automatically selected
    // Without this useEffect, the selectedAddress would remain empty when there is just one device
    // and the user doesn't select it manually from the dropdown by changing it from some default empty selection
    useEffect(() => {
        if (devices.length > 0) {
            setSelectedAddress(devices[0].mac);
        } else {
            setSelectedAddress('');
        }
    }, [devices]); // This will re-run the effect whenever the 'devices' array changes


    const handleConnect = () => {
        if (devices.length === 0) {
            alert("No device selected")
            return
        }
        console.log(`Connecting to ${service} on ${selectedAddress}`)
        sendJsonMessage({event: "connect", data: {service: service, device: selectedAddress}});
    }

    const handleChange = (event) => {
        setSelectedAddress(event.target.value);
    };

    return (
        <div>
            <h1 className="text-3xl mb-4">
                {service}
            </h1>
            <h2>
                Select from available devices
            </h2>
            {/* The following element shows a radio-button selection from a list of devices */}
            <select 
                value={selectedAddress} 
                onChange={handleChange} 
                className="text-xs bg-white border border-gray-300 py-2 px-4 my-4 rounded-lg shadow-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            >
                {devices.map((device) => {
                    return (
                        <option key={device.mac} value={device.mac}>
                            {device.name} ({device.mac})
                        </option>
                    )
                })}
            </select>

            <button 
                onClick={handleConnect}
                disabled={deviceConnected}
                className="text-white p-4 w-full rounded bg-slate-900 hover:bg-slate-700">
                    { deviceConnected ? 
                    <div className="text-md text-green-400">Connected</div> 
                    : 
                    <div className="text-md text-white">Establish Connection</div>}
            </button>

            <div className="flex flex-col mt-4">
                <h2 className="text-2xl">
                    Live data from device
                </h2>
                <div>
                    {liveData}
                </div>
            </div>
        </div>
    )
}

export default ExampleDevice