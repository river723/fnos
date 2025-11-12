# entities.py

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity


class DiskTemperatureSensor(CoordinatorEntity, SensorEntity):
    """表示磁盘温度的传感器实体"""

    def __init__(self, coordinator, disk_name):
        super().__init__(coordinator)
        self.disk_name = disk_name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{disk_name}_temperature"
        self._attr_name = f"{disk_name} 温度"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_icon = "mdi:thermometer"
        self._attr_device_info = DeviceInfo(
            identifiers={(coordinator.config_entry.domain, f"{disk_name}")},
            name=f"磁盘 {disk_name}",
            manufacturer="Generic",
            model="HDD/SSD",
            via_device=(coordinator.config_entry.domain, coordinator.config_entry.entry_id),
        )

    @property
    def native_value(self):
        return self.coordinator.data.get("disk_temps", {}).get(self.disk_name)


class DiskReadSpeedSensor(CoordinatorEntity, SensorEntity):
    """表示磁盘读取速度的传感器实体"""

    def __init__(self, coordinator, disk_name):
        super().__init__(coordinator)
        self.disk_name = disk_name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{disk_name}_read_speed"
        self._attr_name = f"{disk_name} 读取速度"
        self._attr_native_unit_of_measurement = "MB/s"
        self._attr_icon = "mdi:speedometer"
        self._attr_device_info = DeviceInfo(
            identifiers={(coordinator.config_entry.domain, f"{disk_name}")},
            name=f"磁盘 {disk_name}",
            manufacturer="Generic",
            model="HDD/SSD",
            via_device=(coordinator.config_entry.domain, coordinator.config_entry.entry_id),
        )

    @property
    def native_value(self):
        speeds = self.coordinator.data.get("disk_speeds", {})
        return speeds.get(self.disk_name, (0.0, 0.0))[0]


class DiskWriteSpeedSensor(CoordinatorEntity, SensorEntity):
    """表示磁盘写入速度的传感器实体"""

    def __init__(self, coordinator, disk_name):
        super().__init__(coordinator)
        self.disk_name = disk_name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{disk_name}_write_speed"
        self._attr_name = f"{disk_name} 写入速度"
        self._attr_native_unit_of_measurement = "MB/s"
        self._attr_icon = "mdi:speedometer"
        self._attr_device_info = DeviceInfo(
            identifiers={(coordinator.config_entry.domain, f"{disk_name}")},
            name=f"磁盘 {disk_name}",
            manufacturer="Generic",
            model="HDD/SSD",
            via_device=(coordinator.config_entry.domain, coordinator.config_entry.entry_id),
        )

    @property
    def native_value(self):
        speeds = self.coordinator.data.get("disk_speeds", {})
        return speeds.get(self.disk_name, (0.0, 0.0))[1]


class DiskInfoEntity(CoordinatorEntity, SensorEntity):
    """表示磁盘基本信息的文本型传感器（如容量）"""

    def __init__(self, coordinator, disk_name):
        super().__init__(coordinator)
        self.disk_name = disk_name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{disk_name}_info"
        self._attr_name = f"{disk_name} 容量"
        self._attr_icon = "mdi:harddisk"
        self._attr_device_info = DeviceInfo(
            identifiers={(coordinator.config_entry.domain, f"{disk_name}")},
            name=f"磁盘 {disk_name}",
            manufacturer="Generic",
            model="HDD/SSD",
            via_device=(coordinator.config_entry.domain, coordinator.config_entry.entry_id),
        )

    @property
    def native_value(self):
        for disk in self.coordinator.data.get("disk_info", []):
            if disk["name"] == self.disk_name:
                return disk["size"]
        return None
        