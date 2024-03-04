function ScannedResultList({ devices }) {
    // devices is an object that looks like:
    // { (MAC address): {name: (name), RSSI: (RSSI), services: (services)}, ... }
    // sort it by RSSI first
    let sortedDevices = Object.keys(devices).sort((a, b) => devices[b].RSSI - devices[a].RSSI);
    // then filter so that only devices with a name are shown
    sortedDevices = sortedDevices.filter((mac) => devices[mac].name !== null);
    // then map to a list of JSX
    let deviceList = sortedDevices.map((mac) => {
        let device = devices[mac];
        // Determine the background color based on whether there are services that the backend recoggnizes
        let bgColorClass = device.services.length > 0 ? "bg-blue-300" : "bg-slate-300"; // Example: Green for non-zero services, red for zero services
        return (
            <div key={mac} className={`flex flex-col justify-between p-4 ${bgColorClass} rounded my-2 w-64`}>
                <h2 className="text-lg font-bold">{device.name}</h2>
                <div className="flex flex-col justify-between">
                    <h3 className="text-sm font-bold">Address</h3>
                    <p className="text-xs">{mac}</p>
                </div>
                <div className="flex flex-row justify-between">
                    <h3 className="text-sm font-bold">Signal (lower is better)</h3>
                    <p className="text-sm">{device.RSSI}</p>
                </div>
                <div className="flex flex-row justify-between">
                    <h3 className="text-sm font-bold">Services</h3>
                    <p className="text-sm">{device.services.join(", ")}</p>
                </div>
            </div>
        );
    });

    return <div>{deviceList}</div>;
}

export default ScannedResultList;
