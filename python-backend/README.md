# Python Backend

This Python server uses [websockets](https://websockets.readthedocs.io/en/stable/) and [bleak](https://bleak.readthedocs.io/en/latest/)

## Recommended Reading

I used `Flask-SocketIO` to use websockets in the Python server. I recommend reading its [Getting Started page](https://flask-socketio.readthedocs.io/en/latest/getting_started.html)

## Prerequisites

`python_backend` is a Poetry project. Install poetry.([See official Poetry installation instructions](https://python-poetry.org/docs/))

If you already have Python Pip installed,
```
pipx install poetry
```

This project uses Python 3.10, so check that your system python is 3.10, or install it.
```
python3 --version
```
If it is not `Python 3.10.x`, then install it separately. On Mac:
```
brew install python@3.10
```
On Ubuntu, use `deadnskaes` ppa.

`react-frontend` is a React.js project. It requires NPM (Node Package Manager). [See official NPM installation instructions](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

On Mac, the quickest way is to [install homebrew](https://brew.sh/), then:
```
brew install npm
```

## Run App

In one terminal,
```
cd python-backend
```

Just once, install the dependencies:
```
poetry install
```

Run the app:
```
poetry run python3 python_backend/main.py
```

In another terminal:
```
cd react-frontend
```

Just once, install the dependencies:
```
npm install
```

Start web server:
```
npm start
```
Go to `http://localhost:3000` on your web browser.