import React, { useState, useCallback, useEffect } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

import ConnectionColorful from './connectionColorful'
import ExampleDevice from './exampleDevice'
import ScannedResultList from './scannedResultList'

function Body() {
    let [devices, setDevices] = useState({})

    let [devicesByService, setDevicesByService] = useState({})

    const [scanningLoading, setScanningLoading] = useState(false)

    const [ sterzoConnected, setSterzoConnected ] = useState(false)
    const [ sterzoAngle, setSterzoAngle ] = useState(0.0)

    const [socketUrl, setSocketUrl] = useState('ws://localhost:8765');
    const { sendJsonMessage, lastMessage, readyState } = useWebSocket(socketUrl);
    const handleClickSendMessage = useCallback(() => {
        setScanningLoading(true)
        sendJsonMessage({event: "scan_start", data: ""})
        }, [sendJsonMessage]);
    const connectionStatus = {
        [ReadyState.CONNECTING]: 'Connecting',
        [ReadyState.OPEN]: 'Open',
        [ReadyState.CLOSING]: 'Closing',
        [ReadyState.CLOSED]: 'Closed',
        [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
      }[readyState];

    // as soon as devices are updated, sort them by services and store them in devicesByService dictionary
    useEffect(() => {
        // each service (key) may have multiple devices (value)
        let devicesByService = {}
        for (let mac in devices) {
            let device = devices[mac]
            for (let service of device.services) {
                if (devicesByService[service]) {
                    devicesByService[service].push(device)
                } else {
                    devicesByService[service] = [device]
                }
            }
        }
        setDevicesByService(devicesByService)
    }, [devices])


    // handle incoming messages
    useEffect(() => {
        // console.log(`Got a new message: ${lastMessage?.data}`)
        // parse the text message as JSON
        let message = lastMessage?.data
        if (message) {
            try {
                let json = JSON.parse(message)
                switch (json.event) {
                    case "scan_reply":
                        // Incoming json looks something like:
                        // {"event": "scan_reply", "data": {"50068FEA-E7A3-887D-BF13-EEB5ACD35B13": {"name": STERZO, "RSSI": -89, "services": [STERZO]}, ...
                        // expect to receive like 10+ messages per second while scanning is happening.
                        setDevices(json.data)
                        break;
                    case "scan_finished":
                        // server will send this flag event when it's done scanning
                        setScanningLoading(false)
                        break;
                    case "sterzo_connected":
                        // server sends this flag when it successfully connects to a device
                        console.log("Connected to STERZO")
                        setSterzoConnected(true)
                        break;
                    case "sterzo_disconnected":
                        // server sends this flag when it successfully disconnects from a device
                        console.log("Disconnected from STERZO")
                        setSterzoConnected(false)
                        break;
                    case "steering_angle":
                        // Live streaming data from sterzo sensor
                        // parse what could be either a float or a nan. If nan, 0
                        let angle = parseFloat(json.data) || 0.0
                        setSterzoAngle(angle)
                        break;
                    default:
                        console.log("Unknown event.")
                }
            } catch (e) {
                console.log(e)
            }
        }
    }, [lastMessage])

    return (
        <div>
            <div className="flex flex-col bg-slate-200 rounded my-4">
                <div className="flex flex-col m-4">
                    <div>
                        <div className="text-md text-gray-500">
                            Step 1
                        </div>
                        <h1 className="text-4xl font-bold mb-4">
                            Connect to a WebSocket Server
                        </h1>
                    </div>

                    <div className="flex">
                        <input
                            type="text"
                            value={socketUrl}
                            onChange={(e) => setSocketUrl(e.target.value)}
                            className="text-xl p-4 rounded"
                        />
                        <div className="flex-col">
                            <div className="text-3xl font-bold mx-4">
                            {ConnectionColorful(readyState === ReadyState.OPEN)}
                            </div>
                            <div className="text-sm text-slate-500 mx-4">
                                {connectionStatus}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="flex space-x-4 max-w-screen-md mb-16">
                <div className="flex flex-col bg-slate-200 rounded">
                    <div className="w-64 m-4">
                        <div className="text-md text-gray-500">
                            Step 2
                        </div>
                        <h1 className="text-4xl font-bold mb-4">
                            Run Scan
                        </h1>
                        <button 
                            onClick={handleClickSendMessage}
                            disabled={readyState !== ReadyState.OPEN || scanningLoading}
                            className="text-white p-4 w-full rounded bg-slate-900 hover:bg-slate-700 mb-4">
                                { scanningLoading ? 
                                <div className="text-md text-gray-500">Scanning...</div> 
                                : 
                                <div className="text-md text-white">Start Scan</div>}
                        </button>
                        <button
                            onClick={() => {
                                sendJsonMessage({event: "scan_stop", data: ""})
                                setScanningLoading(false)
                            }}
                            disabled={readyState !== ReadyState.OPEN || !scanningLoading}
                            className="text-white p-4 w-full rounded bg-slate-900 hover:bg-slate-700">
                                { scanningLoading ?
                                <div className="text-md text-white">Stop Scanning</div>
                                :
                                <div className="text-md text-gray-500">Waiting for Scan to Start</div>
                                }
                        </button>
                        <p className="text-xs my-2">Note: If you are currently connected to a device (Step 3), it will not show up here.</p>

                        {/* <div>Last message: {lastMessage ? lastMessage.data: ""}</div> */}
                        <div className="flex flex-col mt-4">
                            <h2 className="text-2xl underline my-4">
                                Found Devices
                            </h2>
                            <p className="text-xs">Blue means this application can read from the device</p>
                            <ScannedResultList devices={devices} />
                        </div>
                    </div>
                </div>
                <div className="flex flex-col">
                    <div className="flex flex-col bg-slate-200 rounded">
                        <div className="m-4">
                            <div className="flex flex-col">
                                <div className="text-md text-gray-500">
                                    Step 3
                                </div>
                                <div className="text-4xl font-bold mb-4">
                                    Connect to Device
                                </div>
                                <div className="flex flex-col space-x-4">
                                    {/* Filter the keys of devicesByService by service name if it's not empty, otherwise return empty list */}
                                    <ExampleDevice sendJsonMessage={sendJsonMessage} service="STERZO" devices={devicesByService["STERZO"] || []} deviceConnected={sterzoConnected} liveData={sterzoAngle} />
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="flex flex-col bg-slate-200 rounded mt-4">
                        <div className="m-4">
                            <div className="flex flex-col">
                                <div className="text-md text-gray-500">
                                    Step 4
                                </div>
                                <div className="text-4xl font-bold mb-4">
                                    Disconnect and Reset
                                </div>
                                <div className="flex flex-col space-x-4">
                                    <button 
                                        onClick={() => {
                                            sendJsonMessage({event: "disconnect", data: ""})
                                            setSterzoAngle("")
                                        }}
                                        disabled={readyState !== ReadyState.OPEN}
                                        className="text-white p-4 w-full rounded bg-slate-900 hover:bg-slate-700">
                                            Disconnect
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    )
}

export default Body