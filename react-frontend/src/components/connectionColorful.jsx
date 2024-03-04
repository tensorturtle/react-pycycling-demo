function ConnectionColorful(isOpen) {
    if (isOpen) {
        return (
            <div className="text-green-800">
                READY
            </div>
        )
    } else {
        return (
            <div className="flex">
                <div className="text-red-800">
                    NOT READY
                </div>
            </div>
        )
    }
}

export default ConnectionColorful