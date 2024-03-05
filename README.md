# [React](https://react.dev/) frontend for [Pycycling](https://github.com/zacharyedwardbull/pycycling)

**Hit the ground running for your full-stack bluetooth project.**

This app is a clean, minimal demonstration of a React frontend that controls a Python server to scan and connect to bluetooth devices.
For demonstration purposes, we use [pycycling](https://github.com/zacharyedwardbull/pycycling) library to read and parse data from cycling-specific bluetooth devices. It is trivial to use your own parsers for other bluetooth devices.

Note, while we have reached MVP, this is a work in progress. I recommend you star this repo and look out for versioned updates.

I've prioritized the following when creating this app:
+ Well-commented
+ Educational
+ Minimalistic
+ Not-too-ugly (tailwindcss)

![](assets/mvp_screenshot.png)

# Getting Started

## Installation

`python_backend` is a Poetry project. 

If you already have Python Pip installed,
```
pipx install poetry
```
([See full Poetry installation instructions](https://python-poetry.org/docs/))

This project uses Python 3.10, so check that your system python is 3.10, or install it.
```
python3 --version
```
If it is not `Python 3.10.x`, then install it separately. On Mac:
```
brew install python@3.10
```

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
Note that you must re-launch the app after changes. There is no auto-loading.

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
This auto-loads the site upon changes.

Go to `http://localhost:3000` on your web browser.