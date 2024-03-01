import React from 'react'

function Title() {
    return (
        <div className="flex flex-col bg-slate-200 rounded mt-8 mb-4 mx-8 max-w-screen-md">
            <div className="p-8 w-full">
                <h1 className="text-5xl font-bold mb-4">
                    Bluetooth Demo for React & Flask
                </h1>
                <h2 className="text-2xl">
                    This is a React frontend.
                </h2>
                <h2 className="text-2xl">
                    It connects to a Python backend using WebSockets.
                </h2>
                <h2 className="text-2xl">
                    The Python backend uses bleak to scan and connect to Bluetooth devices.
                </h2>
            </div>
        </div>    
    )

}

export default Title
