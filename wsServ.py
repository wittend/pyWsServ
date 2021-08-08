#!/usr/bin/env python3
# WSS (WS over TLS) server example, with a self-signed certificate
#=================================================================
# Dependencies:
#    Flask==1.0.2
#    Flask-Login==0.4.1
#    Flask-Session==0.3.1
#    Flask_SocketIO
#
# Seem to be already present in Raspberry Pi OS (Py3)
##    itsdangerous==1.1.0
##    Jinja2==2.10
##    MarkupSafe==1.1.0
##    python-engineio
##    python-socketio
##    six==1.11.0
##    Werkzeug==0.14.1
##    import asyncio
##    import pathlib
##    import ssl
##    import websockets
#
# Put all in file called 'requirements.txt' in workingg folder.
# Then execute:
#     pip3 install requirements.txt
#------------------------------------------------------------------

from flask import Flask
from flask import render_template
from flask_socketio import SocketIO

async_mode = None
app = Flask(__name__)
socket_ = SocketIO(app, async_mode=async_mode)

@app.route('/')
def index():
    return render_template('index.html', sync_mode=socket_.async_mode)


async def hello(websocket, path):
    name = await websocket.recv()
    print(f"< {name}")

    greeting = f"Hello {name}!"

    await websocket.send(greeting)
    print(f"> {greeting}")

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
ssl_context.load_cert_chain(localhost_pem)

start_server = websockets.serve(hello, "localhost", 8765, ssl=ssl_context)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
from flask import

if __name__ == '__main__':
    socket_.run(app, debug=True)

