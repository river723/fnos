"""Constants for FNOS integration."""
DOMAIN = "fnos"
DEFAULT_PORT = 22
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes

CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"

SENSOR_TYPES = {
    "cpu": ["CPU Usage", "%", "mdi:cpu-64-bit"],
    "memory": ["Memory Usage", "%", "mdi:memory"],
    "disk": ["Disk Usage", "%", "mdi:harddisk"]
}

