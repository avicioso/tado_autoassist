# Tado Monitor

📡 **Tado Monitor** is a script to monitor and manage the Tado home system. This project allows you to:

- Detect if there are open windows in the zones and automatically activate the `OpenWindow` mode.
- Monitor the temperatures of heating zones and adjust temperature limits.
- Manage the home presence status based on connected mobile devices.

## 🚀 Features

- **Authentication**: Connects to the Tado API and handles the authentication process.
- **Home Status**: Updates the home status (HOME/AWAY) based on the presence of devices.
- **Zone Monitoring**:
  - Detects open windows in zones and adjusts heating accordingly.
  - Applies temperature limits to ensure the heating system does not exceed predefined values.

## 🛠 Requirements

- **Python 3.11+**
- **PyTado**: To interact with the Tado API (check the appropriate version in `pyproject.toml`).

## 🔧 Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/tado-monitor.git
   cd tado-monitor
   ```
2. **Create a virtual environment using uv:**:
    ```bash
    uv sync
    ```
## ⚙️ Configuration

### Environment Variables

Set the following environment variables as needed:

- `CHECKING_INTERVAL`: Interval (in seconds) for checking the home and zone status. (Default: `10.0`).
- `ERROR_RETRY_INTERVAL`: Interval (in seconds) to retry in case of an error. (Default: `30.0`).
- `MIN_TEMP`: Minimum temperature for heating zones. (Default: `5`).
- `MAX_TEMP`: Maximum temperature for heating zones. (Default: `20`).
- `ENABLE_TEMP_LIMIT`: Enables or disables temperature limiting. (Default: `true`).
- `SAVE_LOG`: If enabled, saves logs to a file. (Default: `false`).
- `LOG_FILE`: Path to the log file. (Default: `logfile.log`).
- `MAX_LOG_LINES`: Maximum number of log lines. (Default: `50`).
- `TOKEN_FOLDER`: Folder to store the authentication token. (Default: `./token`).

### Example `.env`

```env
CHECKING_INTERVAL=10.0
ERROR_RETRY_INTERVAL=30.0
MIN_TEMP=5
MAX_TEMP=20
ENABLE_TEMP_LIMIT=true
SAVE_LOG=true
LOG_FILE=logfile.log
MAX_LOG_LINES=50
TOKEN_FOLDER=./token
```

## 🔑 Authentication

To connect to the Tado API, a token file is required. If the file does not exist, the script will automatically start the authentication process.

### Authentication Process:

1. If the token file is not found, the script will prompt you to visit a URL to authenticate.
2. Once authentication is completed, the system will store the token for future runs.

## 📝 Notes

- **Manual interruption**: You can interrupt the script by pressing `Ctrl + C`. The process will handle the exception and exit cleanly.
- **Logs**: Logs will be displayed in the console and, if enabled, saved to a file.

## 📚 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔄 Acknowledgements

This script contains code taken from the original [Tado Auto-Assist for Geofencing and Open Window Detection + Temperature Limit](https://github.com/mzettwitz/tado_aa_geo) by [Adrian Slabu](mailto:adrianslabu@icloud.com), created on 11.02.2021.

The original script is licensed under the GPLv3 License. Please refer to the original repository for more information.