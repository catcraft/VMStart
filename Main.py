import hashlib
from flask import Flask, request, jsonify
import subprocess
import time
import configparser
import logging
import waitress

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')
server_ip = config['server']['ip']
server_port = int(config['server']['port'])

# Configure logging
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s %(message)s')

def generate_expected_tokens(hour):
    """
    Generate the expected tokens for all allowed users based on the current hour.
    """
    config.read('config.ini')
    allowed_users = config['auth']['allowed_users'].split(',')
    allowed_users = [user.strip() for user in allowed_users]
    
    tokens = {}
    for user in allowed_users:
        raw_string = f"{user}{hour}"
        tokens[user] = hashlib.sha256(raw_string.encode()).hexdigest()
    return tokens

def start_hyperv_vm(vm_name):
    """
    Starts a Hyper-V virtual machine using PowerShell.
    """
    try:
        command = [
            "powershell",
            "-Command",
            f"Start-VM -Name \"{vm_name}\""
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            if "WARNING: The virtual machine is already in the specified state." in result.stdout:
                return f"'{vm_name}' is already running."
            return f"'{vm_name}' started successfully."
        else:
            return f"Failed to start '{vm_name}': {result.stderr}"
    except Exception as e:
        return str(e)

@app.route('/start_vm', methods=['POST'])
def start_vm():
    data = request.json
    if not data or 'vm_name' not in data or 'token' not in data:
        return jsonify({"error": "Missing 'vm_name' or 'token' in request body"}), 400

    vm_name = data['vm_name']
    received_token = data['token']

    # Validate the token
    current_hour = f"{int(time.strftime('%H')):02}"  # Current hour in HH format
    expected_tokens = generate_expected_tokens(current_hour)

    if received_token not in expected_tokens.values():
        logging.info(f"Unauthorized access attempt for VM '{vm_name}' with token '{received_token}'")
        return jsonify({"error": "Unauthorized"}), 401
    user = [user for user, token in expected_tokens.items() if token == received_token][0]

    config.read('config.ini')
    allowed_vms = config['vms']['startable'].split(',')
    allowed_vms = [user.strip() for user in allowed_vms]

    if vm_name not in allowed_vms:
        logging.info(f"Not allowed to start VM '{vm_name}' by user {user}")
        return jsonify({"error": "VM cannot start, not allowed"}), 401
    
    # Start the VM
    response_message = start_hyperv_vm(vm_name)
    if "successfully" in response_message:
        logging.info(f"VM '{vm_name}' started successfully by user {user}")
        return jsonify({"message": response_message}), 200
    elif "already running" in response_message:
        logging.info(f"VM '{vm_name}' is already running, {user}")
        return jsonify({"message": response_message}), 200
    else:
        logging.error(f"Failed to start VM '{vm_name}': {response_message}, {user}")
        return jsonify({"error": response_message}), 500

if __name__ == '__main__':
    waitress.serve(app, host=server_ip, port=server_port)
