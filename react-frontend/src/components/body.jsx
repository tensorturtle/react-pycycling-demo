import React, { useState, useCallback, useEffect } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

import ConnectionColorful from './connectionColorful'
import ExampleDevice from './exampleDevice'

function Body() {
    let [devices, setDevices] = useState([])

    const [scanningLoading, setScanningLoading] = useState(false)

    const [socketUrl, setSocketUrl] = useState('ws://localhost:8765');
    const { sendJsonMessage, lastMessage, readyState } = useWebSocket(socketUrl);
    const handleClickSendMessage = useCallback(() => {
        setScanningLoading(true)
        sendJsonMessage({event: "scan_start", data: "start"})
        }, [sendJsonMessage]);
    const connectionStatus = {
        [ReadyState.CONNECTING]: 'Connecting',
        [ReadyState.OPEN]: 'Open',
        [ReadyState.CLOSING]: 'Closing',
        [ReadyState.CLOSED]: 'Closed',
        [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
      }[readyState];

    // handle incoming messages
    useEffect(() => {
        console.log(`Got a new message: ${lastMessage?.data}`)
        // parse the text message as JSON
        let message = lastMessage?.data
        if (message) {
            try {
                let json = JSON.parse(message)
                switch (json.event) {
                    case "scan_reply":
                        // server sends a JSON (sorted python dict) with the devices eagerly, as soon as they are found
                        // expect to receive like 10+ messages per second while scanning is happening.
                        let sortedDevices = Object.keys(json.data).sort((a, b) => {
                            return json.data[b].rssi - json.data[a].rssi
                        })
                        setDevices(sortedDevices.map((device) => {
                            return json.data[device].name
                        }))
                        break;
                    case "scan_finished":
                        // server will send this flag event when it's done scanning
                        setScanningLoading(false)
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
            <div className="flex flex-col bg-slate-200 rounded my-4 ">
                <div className="flex flex-col m-8">
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

            <div className="flex space-x-4 max-w-screen-md">
                <div className="flex flex-col bg-slate-200 rounded">
                    <div className="w-64 m-8">
                        <div className="text-md text-gray-500">
                            Step 2
                        </div>
                        <h1 className="text-4xl font-bold mb-4">
                            Run Scan
                        </h1>
                        <button 
                            onClick={handleClickSendMessage}
                            disabled={readyState !== ReadyState.OPEN || scanningLoading}
                            className="text-white p-4 w-full rounded bg-slate-900 hover:bg-slate-700">
                                { scanningLoading ? 
                                <div className="text-md text-gray-500">Scanning...</div> 
                                : 
                                <div className="text-md text-white">Scan Again</div>}
                        </button>
                        {/* <div>Last message: {lastMessage ? lastMessage.data: ""}</div> */}
                        <div className="flex flex-col mt-4">
                            <h2 className="text-2xl underline my-4">
                                Found Devices
                            </h2>
                            { devices.length > 0 ? devices.map((device, index) => {
                                return <div key={index}>{device}</div>
                            }) : <div className="text-md text-gray-500">
                                No devices found. Try running Scan again.
                                </div> }
                        </div>
                    </div>
                </div>

                <div className="flex flex-col bg-slate-200 rounded">
                    <div className="m-8">
                        <div className="flex flex-col">
                            <div className="text-md text-gray-500">
                                Step 3
                            </div>
                            <div className="text-4xl font-bold mb-4">
                                Connect to Device
                            </div>
                            <div className="flex space-x-4">
                                <ExampleDevice />
                                <ExampleDevice />
                                <ExampleDevice />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Body