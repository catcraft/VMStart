# VMStart

## Description
VMStart is a utility tool designed to simplify the process of starting virtual machines. It provides an option to remotely start a Hyper-V VM without an admin's help.

## Installation
To install VMStart, follow these steps:
1. Download the files from the repository.
2. Navigate to the project directory:
    ```sh
    cd VMStart
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration
1. Open the `config.ini` file in the project directory.
2. Configure the server settings:
    ```ini
    [server]
    ip = your_server_ip
    port = your_server_port
    ```
3. Configure the authentication settings:
    ```ini
    [auth]
    allowed_users = user1,user2,user3
    ```
4. Configure the virtual machines that can be started:
    ```ini
    [vms]
    startable = vm1,vm2,vm3
    ```
5. Update the server IP in the PowerShell script `Startskript.ps1`:
    ```powershell
    # Change this line to your server IP
    $serverUrl = "http://your_server_ip:your_server_port/start_vm"
    ```

## Usage
To start the Flask server:
```sh
flask run
```

To start using VMStart, use the provided PowerShell script or any other script:
```sh
./start-vm.ps1
```
Follow the on-screen instructions to manage your virtual machines.

### Permissions
For the script to work, it either needs to be run with highest permissions in Task Scheduler or the user needs to be in the Hyper-V Administrators group.

- [How to create a Python Task in Task Scheduler](https://www.jcchouinard.com/python-automation-using-task-scheduler/)
- [How to add a user to the Hyper-V Administrators group](https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/user-account-control-and-hyper-v)

### Security
Ensure that only authorized users have access to the `config.ini` file and the PowerShell script. The tokens generated for authentication are based on the current hour and the username, so it is crucial to keep the configuration secure to prevent unauthorized access.

### Example Setup
```plaintext
├── Client Device/
│   └── Start VM.lnk
├── Hyper-V Server/
│   ├── config.ini
│   ├── Main.py
│   ├── requirements.txt
│   └── server.log
└── Storage Server/
    └── Startskript.ps1
```

Here, the server logic is added to the Hyper-V Server, which acts as the web server. The Storage Server is accessible from the clients, and the clients have a shortcut that starts the script with the appropriate arguments:
```plaintext
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -ExecutionPolicy Bypass -File "\\StorageServer\VMStart\Startskript.ps1" -VMName "TestVM"
```