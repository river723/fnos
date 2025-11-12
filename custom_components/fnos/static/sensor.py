# sensor.py
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SENSOR_TYPES
from .coordinator import FnosDataCoordinator
from .disk_coordinator import DiskDataCoordinator
from .devices import create_disk_entities
# from .entities import (
#     DiskTemperatureSensor,
#     DiskReadSpeedSensor,
#     DiskWriteSpeedSensor,
#     DiskInfoEntity,
# )

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    main_coordinator = FnosDataCoordinator(hass, config_entry)
    await main_coordinator.async_config_entry_first_refresh()

    # 只保留非磁盘相关传感器
    MAIN_SENSOR_TYPES = {
        key: value for key, value in SENSOR_TYPES.items()
        if key not in {"disk_info", "disk_speeds", "disk_temps"}
    }
    sensors = [
        FnosSensor(main_coordinator, config_entry, sensor_type)
        for sensor_type in MAIN_SENSOR_TYPES
    ]

    try:
        disk_data = main_coordinator.data.get('disk_info', [])
    except AttributeError:
        disk_data = []

    if disk_data:
        disk_coordinator = DiskDataCoordinator(hass, config_entry, main_coordinator)
        await disk_coordinator.async_request_refresh()

        try:
            if disk_coordinator.data and disk_coordinator.data.get("disk_info"):
                disk_entities = await create_disk_entities(disk_coordinator)
                sensors.extend(disk_entities)
            else:
                _LOGGER.warning("磁盘协调器数据为空，跳过磁盘传感器创建")
        except Exception as ex:
            _LOGGER.warning("无法创建磁盘传感器: %s", ex)

    async_add_entities(sensors, update_before_add=True)


class FnosSensor(CoordinatorEntity, SensorEntity):
    """FNOS 传感器实体类"""

    def __init__(
        self,
        coordinator: FnosDataCoordinator,
        config_entry: ConfigEntry,
        sensor_type: str
    ):
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._type = sensor_type

        sensor_names = {
            'cpu': 'CPU 使用率',
            'memory': '内存使用率',
            'disk': '磁盘使用率',
            'download_speed': '下载速度',
            'upload_speed': '上传速度',
            'uptime': '系统运行时间',
            'cpu_temperature': 'CPU 温度'
        }

        self._attr_name = sensor_names.get(sensor_type, sensor_type)
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_type}"
        self._attr_native_unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self._attr_icon = SENSOR_TYPES[sensor_type][2]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=f"FNOS {config_entry.data['host']}",
            manufacturer="FNOS",
        )

    @property
    def native_value(self):
       
        return self.coordinator.data.get(self._type)
    
    