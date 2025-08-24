# 🐙 Octopus Distributed Task Orchestration

## Quick Start Scripts

This repository includes PowerShell scripts for easy deployment and management of both server and client components.

### Prerequisites

1. **Anaconda or Miniconda** - Install from [anaconda.com](https://www.anaconda.com/products/distribution)
2. **PowerShell** (included with Windows)
3. **Git** (to clone the repository)

### Server Setup

Run the server setup script from the project root directory:

```powershell
# Basic setup (creates conda env, installs deps, starts server)
.\setup_server.ps1

# Skip environment setup if already configured
.\setup_server.ps1 -SkipEnvSetup

# Start server on custom port
.\setup_server.ps1 -Port 9000
```

The server will be available at `http://localhost:8000/dashboard` (or your custom port).

### Client Setup

Run the client setup script from the project root directory:

```powershell
# Basic setup (creates conda env, installs deps, starts client)
.\setup_client.ps1

# Skip environment setup if already configured
.\setup_client.ps1 -SkipEnvSetup

# Connect to remote server
.\setup_client.ps1 -ServerUrl "http://192.168.1.100:8000"

# Custom client name
.\setup_client.ps1 -ClientName "WorkstationClient"

# Combined options
.\setup_client.ps1 -ServerUrl "http://192.168.1.100:8000" -ClientName "WorkstationClient" -SkipEnvSetup
```

## What the Scripts Do

### Server Script (`setup_server.ps1`)
1. ✅ Checks for conda installation
2. ✅ Creates `octopus_server` conda environment with Python 3.11
3. ✅ Installs dependencies from `octopus_server/requirements.txt`
4. ✅ Extracts playwright browsers if `playwright_browsers.zip` exists
5. ✅ Starts the server with web dashboard

### Client Script (`setup_client.ps1`)
1. ✅ Checks for conda installation
2. ✅ Creates `octopus_client` conda environment with Python 3.11
3. ✅ Installs dependencies from `octopus_client/requirements.txt`
4. ✅ Extracts playwright browsers if `playwright_browsers.zip` exists
5. ✅ Tests server connectivity
6. ✅ Starts the client and connects to server

## Playwright Browser Setup

For projects that use Playwright, you may need browser binaries. Since direct `playwright install` may not work in corporate environments:

1. **On a machine with internet access:**
   ```bash
   playwright install
   # Then zip the browsers directory
   cd ~/.cache/ms-playwright  # Linux/Mac
   cd %USERPROFILE%\.cache\ms-playwright  # Windows
   # Create playwright_browsers.zip with all browser folders
   ```

2. **Place `playwright_browsers.zip` in the project root**
3. **The setup scripts will automatically extract it to the correct location**

## Manual Installation

If you prefer manual setup:

### Server
```powershell
conda create -n octopus_server python=3.11 -y
conda activate octopus_server
cd octopus_server
pip install -r requirements.txt
python main.py
```

### Client
```powershell
conda create -n octopus_client python=3.11 -y
conda activate octopus_client
cd octopus_client
pip install -r requirements.txt
python main.py --server-url "http://localhost:8000"
```

## Troubleshooting

### Common Issues

1. **"Conda not found"**
   - Install Anaconda/Miniconda and restart PowerShell
   - Ensure conda is in your PATH

2. **"Permission denied" or execution policy errors**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **"Cannot reach server"**
   - Ensure server is running first
   - Check firewall settings
   - Verify the server URL and port

4. **Playwright browser issues**
   - Ensure `playwright_browsers.zip` is in project root
   - Try manual installation: `playwright install`

### Getting Help

- Check the logs in `octopus_server/logs/server.log`
- Check the logs in `octopus_client/logs/client.log`
- Run scripts with `-Verbose` for detailed output

## Features

- 🔄 **Auto Environment Management** - Creates and manages conda environments
- 🌐 **Network Connectivity Tests** - Verifies server accessibility
- 📦 **Dependency Installation** - Handles all Python packages
- 🎭 **Playwright Support** - Automated browser setup
- 🎨 **Colored Output** - Easy-to-read status messages
- ⚡ **Quick Start** - One command to get everything running

## Production Deployment

For production environments:

1. **Server**: Use `setup_server.ps1` on your server machine
2. **Clients**: Distribute the project folder and `setup_client.ps1` to client machines
3. **Configure**: Update server URL in client script parameters
4. **Schedule**: Use Windows Task Scheduler to auto-start clients
