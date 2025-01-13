param(
    [Parameter(Mandatory = $true)]
    [string]$VMName
)

# Change this line to your server IP
$serverUrl = "http://your_server_ip:your_server_port/start_vm"

# User & Time
$currentUser = whoami
$currentHour = (Get-Date -Format "HH")

# Combine
$rawString = "$currentUser$currentHour"

# Hash
$hashBytes = [System.Text.Encoding]::UTF8.GetBytes($rawString)
$sha256 = [System.Security.Cryptography.SHA256]::Create()
$hashedToken = [System.BitConverter]::ToString($sha256.ComputeHash($hashBytes)).Replace("-", "").ToLower()

# Request body
$requestBody = @{
    vm_name = $VMName
    token = $hashedToken
} | ConvertTo-Json -Depth 10

# Headers
$headers = @{
    "Content-Type" = "application/json"
}

# Assembly for notifications
Add-Type -AssemblyName System.Windows.Forms

# Send POST request
try {
    $response = Invoke-RestMethod -Uri $serverUrl -Method POST -Body $requestBody -Headers $headers
    Write-Host "Response: $($response | ConvertTo-Json -Depth 10)"
    Write-Host "Message: $($response.message)"
    Write-Host "Status: $($response.status)"
    if ($response.message -match "successfully started") {
        Write-Host "The VM has started successfully."
        [System.Windows.Forms.MessageBox]::Show("The server has started successfully.", "Success", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
    } elseif ($response.message -match "already.") {
        Write-Host "The VM is already running."
        [System.Windows.Forms.MessageBox]::Show("$($response.message)", "Server already started", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning)
    } else {
        Write-Host "Failed to start the VM. Message: $($response.message)"
        [System.Windows.Forms.MessageBox]::Show("Failed to start the server. Message: $($response.message)", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    }
} catch {
    Write-Host "Failed to send request: $_"
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
    [System.Windows.Forms.MessageBox]::Show("Failed to send request: $_", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
}
