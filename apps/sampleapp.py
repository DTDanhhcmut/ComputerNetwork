#
# Copyright (C) 2026 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
#
# AsynapRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#


"""
app.sampleapp
~~~~~~~~~~~~~~~~~

"""

import asyncio
import time



import sys
import os
import importlib.util
import json

from   daemon import AsynapRous

app = AsynapRous()

@app.route('/long-task', methods=['GET'])
async def long_task(headers, body):
    await asyncio.sleep(5) # Giả lập tác vụ tốn 5 giây
    return b"Task finished!"

@app.route('/login', methods=['POST'])
def login(headers="guest", body="anonymous"):
    """
    Handle user login via POST request.
    Verifies credentials and issues a session cookie.
    """
    print("[SampleApp] Processing login...")
    print("[SampleApp] Received body: {}".format(body))
    
    # Simple credential verification (e.g., admin/123)
    if "username=admin" in body and "password=123" in body:
        data = {"status": "success", "message": "Welcome Admin!"}
        res_body = json.dumps(data).encode("utf-8")
        
        # Return a tuple: (Response body, Additional Headers)
        # Set-Cookie instructs the browser to store the session identifier
        return (res_body, {"Set-Cookie": "session_id=BK-NET-2026; Path=/; HttpOnly"})
    
    # Unauthorized access
    data = {"status": "fail", "message": "Invalid username or password"}
    return (json.dumps(data).encode("utf-8"), 401)

@app.route('/secret', methods=['GET'])
async def secret(headers, body):
    """
    Protected route that requires a valid session cookie.
    """
    # Check if the 'session_id' cookie is present in the request headers
    if "session_id=BK-NET-2026" in str(headers):
        return b"Congratulations! You have accessed the secret page using a Cookie."
    
    # Forbidden access
    return b"No Cookie found - Access Denied!", 403

@app.route("/echo", methods=["POST"])
def echo(headers="guest", body="anonymous"):
    print("[SampleApp] received body {}".format(body))

    try:
        message = json.loads(body)
        data = {"received": message }
        # Convert to JSON string
        json_str = json.dumps(data)
        return (json_str.encode("utf-8"))
    except json.JSONDecodeError:
        data = {"error": "Invalid JSON"}
        # Convert to JSON string
        json_str = json.dumps(data)
        return (json_str.encode("utf-8"))


@app.route('/hello', methods=['GET', 'PUT'])
async def hello(headers, body):
    """
    Handle greeting via PUT request.

    This route prints a greeting message to the console using the provided headers
    and body.

    :param headers (str): The request headers or user identifier.
    :param body (str): The request body or message payload.
    """
    print("[SampleApp] ['PUT'] **ASYNC** Hello in {} to {}".format(headers, body))
    data =  {"id": 1, "name": "Alice", "email": "alice@example.com"}

    # Convert to JSON string
    json_str = json.dumps(data)
    return (json_str.encode("utf-8"))

def create_sampleapp(ip, port):
    # Prepare and launch the RESTful application
    app.prepare_address(ip, port)
    app.run()

# Store active peers in a dictionary { "ip:port": last_seen_timestamp }
active_peers = {}

@app.route('/submit-info', methods=['POST'])
async def submit_info(headers, body):
    """
    Endpoint for peers to register their presence.
    Expected body: {"ip": "127.0.0.1", "port": 5001}
    """
    try:
        data = json.loads(body)
        peer_key = f"{data['ip']}:{data['port']}"
        active_peers[peer_key] = time.time()
        print(f"[Tracker] Registered peer: {peer_key}")
        return b"Registration Successful"
    except Exception as e:
        return b"Registration Failed", 400

@app.route('/get-list', methods=['GET'])
async def get_list(headers, body):
    """
    Returns the list of all currently active peers.
    """
    # Optional: Filter out peers that haven't checked in for a long time
    return json.dumps(active_peers).encode('utf-8')

# Store chat history in memory for the demo
chat_history = []

@app.route('/receive-message', methods=['POST'])
async def receive_message(headers, body):
    try:
        data = json.loads(body)
        chat_history.append(data)
        print(f"[P2P] Message added to history: {data}")
        return b"Message Received"
    except Exception as e:
        print(f"[P2P] Error receiving message: {e}")
        return b"Invalid Message Format", 400

@app.route('/api/get-messages', methods=['GET'])
async def get_messages(headers, body):
    """
    API for the frontend (chat.html) to fetch the conversation history.
    """
    return json.dumps(chat_history).encode('utf-8')