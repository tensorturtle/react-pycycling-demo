# Python Backend

This Python server uses [websockets](https://websockets.readthedocs.io/en/stable/) and [bleak](https://bleak.readthedocs.io/en/latest/)

## Recommended Reading

I used `Flask-SocketIO` to use websockets in the Python server. I recommend reading its [Getting Started page](https://flask-socketio.readthedocs.io/en/latest/getting_started.html)

## Notes & Background

**Why Websocket and not a higher-level abstraction like Socket.io?**
+ [Socket.io](https://socket.io/) provides an abstraction on top of websockets, and a slightly more ergonomic API.
+ Still, this project uses simple websockets because it provides more fine-grained control.
+ This application is designed as a starting point for your own implementation, so we try to minimize dependencies.