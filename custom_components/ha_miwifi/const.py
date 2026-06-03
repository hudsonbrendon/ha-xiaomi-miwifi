"""Constants for the MiWiFi integration."""
from __future__ import annotations

DOMAIN = "ha_miwifi"

CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_CONSIDER_HOME = "consider_home"
CONF_EXCLUDED_MACS = "excluded_macs"

DEFAULT_NAME = "MiWiFi"
DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 600
DEFAULT_CONSIDER_HOME = 180

MANUFACTURER = "Xiaomi"

EVENT_DEVICE_CONNECTED = "ha_miwifi_device_connected"
EVENT_DEVICE_DISCONNECTED = "ha_miwifi_device_disconnected"
EVENT_NEW_DEVICE = "ha_miwifi_new_device"
