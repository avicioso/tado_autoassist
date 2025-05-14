import os
import sys
import time
import logging
from pathlib import Path
from PyTado.interface import Tado

# --- Configuration ---
def str_to_bool(val):
    return str(val).strip().lower() in ("true", "1", "yes")

CHECKING_INTERVAL = float(os.environ.get("CHECKING_INTERVAL", 10.0))
ERROR_RETRY_INTERVAL = float(os.environ.get("ERROR_RETRY_INTERVAL", 30.0))
MIN_TEMP = int(os.environ.get("MIN_TEMP", 5))
MAX_TEMP = int(os.environ.get("MAX_TEMP", 20))
ENABLE_TEMP_LIMIT = str_to_bool(os.environ.get("ENABLE_TEMP_LIMIT", "true"))
SAVE_LOG = str_to_bool(os.environ.get("SAVE_LOG", "false"))
LOG_FILE = os.environ.get("LOG_FILE", "logfile.log")
MAX_LOG_LINES = int(os.environ.get("MAX_LOG_LINES", 50))

TOKEN_FOLDER = Path(os.environ.get("TOKEN_FOLDER", "./token"))
TOKEN_FOLDER.mkdir(parents=True, exist_ok=True)
TOKEN_FILE = TOKEN_FOLDER / "token"

# --- Logging ---
logger = logging.getLogger("TadoMonitor")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s # %(message)s', "%d-%m-%Y %H:%M:%S")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

if SAVE_LOG:
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# --- Globals ---
tado = None
devices_home = []

# --- Core Functions ---
def authenticate():
    """
    Authenticates the user by connecting to the Tado API and handling the device 
    activation process.

    This function checks for the existence of the token file. If the token file is 
    missing, it initiates the authentication process. If the device activation status 
    is "PENDING", the user is prompted to visit a URL for authentication. Once the 
    activation status is "COMPLETED", the function logs a successful login. If the 
    authentication process fails, the function will retry after a set interval.

    It handles interruptions via KeyboardInterrupt and logs any exceptions encountered 
    during the authentication process. In case of errors, the function will retry 
    after waiting for a specified interval.

    Raises:
        KeyboardInterrupt: If the user interrupts the authentication process.
        Exception: If any unexpected error occurs during the authentication process.

    Returns:
        None
    """
    global tado
    while True:
        try:
            tado = Tado(token_file_path=TOKEN_FILE)
            if not TOKEN_FILE.exists():
                logger.info("No token file found. Starting authentication process...")

            status = tado.device_activation_status()
            if status == "PENDING":
                print("Please visit the following URL to authenticate:")
                print(tado.device_verification_url())
                tado.device_activation()
                status = tado.device_activation_status()

            if status == "COMPLETED":
                logger.info("Login successful.")
                return
            else:
                logger.warning(f"Login failed. Current status: {status}. Retrying in {ERROR_RETRY_INTERVAL} seconds...")
                time.sleep(ERROR_RETRY_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Authentication interrupted by user.")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Login error: {e}. Retrying in {ERROR_RETRY_INTERVAL} seconds...")
            time.sleep(ERROR_RETRY_INTERVAL)

def update_home_status():
    """
    Updates the home status based on the presence of devices and the current home state.

    This function checks the presence of devices at home by retrieving the state of mobile 
    devices with geo-tracking enabled. It compares the number of devices at home to the 
    current home state (either "HOME" or "AWAY"). Based on this comparison:
    - If there are no devices at home and the home state is "HOME", it switches the system 
      to "AWAY" mode.
    - If there are devices at home and the home state is "AWAY", it switches the system 
      to "HOME" mode and logs the names of the devices at home.

    The function handles errors that may occur during the process, and it logs information 
    about changes in the home status. It also manages a `KeyboardInterrupt` to allow the user 
    to interrupt the process manually.

    Raises:
        KeyboardInterrupt: If the user interrupts the update process.
        Exception: If any error occurs while retrieving or updating the home status.

    Returns:
        None
    """
    global devices_home
    try:
        home_state = tado.get_home_state().get("presence")
        devices_home = [
            dev["name"] for dev in tado.get_mobile_devices()
            if dev["settings"].get("geoTrackingEnabled") and
            dev.get("location") and
            dev["location"].get("atHome")
        ]

        if not devices_home and home_state == "HOME":
            logger.info("No devices at home. Switching to AWAY mode.")
            tado.set_away()
        elif devices_home and home_state == "AWAY":
            logger.info(f"Devices at home: {', '.join(devices_home)}. Switching to HOME mode.")
            tado.set_home()

    except KeyboardInterrupt:
        logger.info("Update interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error updating home status: {e}")
        raise

def monitor_zones():
    """
    Monitors the zones for open window status and temperature limits, adjusting 
    heating settings accordingly.

    This function continuously checks the status of each zone and performs the following:
    - Detects if a window is open in any of the zones, and if detected, activates the 
      OpenWindow mode to adjust the heating.
    - Monitors the temperature in zones where heating is enabled and applies limits:
        - If the current temperature exceeds the maximum allowed temperature (MAX_TEMP), 
          it lowers the temperature.
        - If the current temperature is below the minimum allowed temperature (MIN_TEMP), 
          it raises the temperature.

    The function repeats this process in a loop, periodically checking the status of each zone.

    Handles KeyboardInterrupt to allow for user interruption and logs any errors encountered 
    during monitoring, retrying the process after a specified interval.

    Raises:
        KeyboardInterrupt: If the user interrupts the monitoring process.
        Exception: If any unexpected error occurs during the monitoring process.

    Returns:
        None
    """
    logger.info("Monitoring zones for window status and temperature limits...")
    while True:
        try:
            update_home_status()

            for zone in tado.get_zones():
                zone_id = zone["id"]
                zone_name = zone["name"]
                state = tado.get_state(zone_id)

                if tado.get_open_window_detected(zone_id).get("openWindowDetected"):
                    logger.info(f"{zone_name}: Open window detected. Activating OpenWindow mode.")
                    tado.set_open_window(zone_id)

                if ENABLE_TEMP_LIMIT and state['setting']['type'] == 'HEATING' and state['setting']['power'] == "ON":
                    current_temp = float(state['setting']['temperature']['celsius'])
                    if current_temp > MAX_TEMP:
                        tado.set_zone_overlay(zone_id, 0, MAX_TEMP)
                        logger.info(f"{zone_name}: Temp {current_temp}°C > max {MAX_TEMP}°C. Lowering.")
                    elif current_temp < MIN_TEMP:
                        tado.set_zone_overlay(zone_id, 0, MIN_TEMP)
                        logger.info(f"{zone_name}: Temp {current_temp}°C < min {MIN_TEMP}°C. Raising.")
    
            time.sleep(CHECKING_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Monitoring interrupted by user.")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Monitoring error: {e}. Retrying in {ERROR_RETRY_INTERVAL} seconds...")
            time.sleep(ERROR_RETRY_INTERVAL)

# --- Entry Point ---
def main():
    authenticate()
    monitor_zones()

if __name__ == "__main__":
    main()
