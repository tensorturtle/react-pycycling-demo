import React from 'react'

function Title() {
    return (
        <div className="flex flex-col mt-8 mx-8 mb-0 max-w-screen-md">
            <div className="w-full">
                <h1 className="text-5xl font-bold mb-4">
                    Bluetooth Demo with React and Python
                </h1>
                <h2 className="text-2xl">
                    This React frontend couples tightly to a Python backend using Websockets.
                </h2>
                <h2 className="text-2xl">
                    Which uses bleak and pycycling libraries to demonstrate Bluetooth scanning and connection.
                </h2>
            </div>
            <hr class="h-px my-8 bg-gray-200 border-0 dark:bg-gray-700"></hr>

        </div>
  
    )

}

export default Title
