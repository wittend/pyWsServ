#!/usr/bin/env python3
# WSS (WS over TLS) server example, with a self-signed certificate
#=================================================================
# Dependencies:
#    Flask==1.0.2
#    Flask-Login==0.4.1
#    Flask-Session==0.3.1
#    Flask_SocketIO
#    simple-websocket-0.3.0
#    wsproto-1.0.0
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
#
# This complains if runs from the default python environment. Use
# a 'venv'
#------------------------------------------------------------------
import os
import errno
import posix

from flask import Flask
from flask import render_template
from flask import copy_current_request_context
from flask import session

from flask_socketio import SocketIO
from flask_socketio import emit
from flask_socketio import disconnect
from threading import Lock


async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket_ = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

#async_mode = None
#app = Flask(__name__)

PipeIn = '/home/web/wsroot/pipein.PipeOut'
PipeOut = '/home/web/wsroot/pipeout.PipeOut'

def openPipes():
    # Pipe Stuff
    #----------------------------
    try:
        os.mkfifo(PipeOut)
    except OSError as oe:
        if oe.errno != errno.EEXIST:
            raise

    while True:
        print("Opening PipeOut...")
        with open(PipeOut,posix.O_WRONLY | posix.O_NONBLOCK) as PipeOut:
            print("PipeOut opened")
            while True:
                data = PipeOut.read()
                if len(data) == 0:
                    print("Writer closed")
                    break
                print('Read: "{0}"'.format(data))

# WebSocket stuff.
#----------------------------
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

@socket_.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socket_.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socket_.on('disconnect_request', namespace='/test')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)

# Secure (TLS) setup.
#----------------------------
#ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
#ssl_context.load_cert_chain(localhost_pem)
#
#start_server = websockets.serve(hello, "localhost", 8765, ssl=ssl_context)
#
#asyncio.get_event_loop().run_until_complete(start_server)
#asyncio.get_event_loop().run_forever()


# Life begins here.
#----------------------------
if __name__ == '__main__':
    socket_.run(app, debug=True)

