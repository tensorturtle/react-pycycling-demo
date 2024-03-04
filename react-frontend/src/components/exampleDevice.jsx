function ExampleDevice() {
    return (
        <div>
            <h1 className="text-3xl mb-4">
                Sterzo
            </h1>
            <button className="text-black p-4 w-full rounded outline outline-1 bg-slate-50 hover:bg-slate-100">
                Connect
            </button>
            <div className="flex flex-col mt-4">
                <h2 className="text-2xl">
                    Live data from device
                </h2>
            </div>
        </div>
    )
}

export default ExampleDevice