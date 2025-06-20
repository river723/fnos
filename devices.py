# devices.py

from homeassistant.helpers.device_registry import async_get as async_get_device_registry


async def register_disk_devices(hass, config_entry, disks):
    """
    注册所有磁盘为独立设备（每个磁盘一个设备）
    
    :param hass: HomeAssistant 实例
    :param config_entry: 配置条目
    :param disks: 磁盘列表，来自 lsblk 输出解析后的数据
    """
    device_registry = async_get_device_registry(hass)

    for disk in disks:
        device_registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            identifiers={(config_entry.domain, disk["name"])},
            name=f"mdi:harddisk {disk['name']}",
            manufacturer="Generic",
            model="HDD/SSD",
            icon="mdi:harddisk",
            via_device=(config_entry.domain, config_entry.entry_id),
        )


async def create_disk_entities(coordinator):
    """
    根据当前协调器的数据生成磁盘相关的传感器实体
    
    :param coordinator: 数据协调器
    :return: 一组磁盘传感器实体
    """
    from .entities import (
        DiskTemperatureSensor,
        DiskReadSpeedSensor,
        DiskWriteSpeedSensor,
        DiskInfoEntity,
    )

    entities = []
    disk_info_list = coordinator.data.get("disk_info", [])

    for disk in disk_info_list:
        disk_name = disk["name"]
        entities.append(DiskTemperatureSensor(coordinator, disk_name))
        entities.append(DiskReadSpeedSensor(coordinator, disk_name))
        entities.append(DiskWriteSpeedSensor(coordinator, disk_name))
        entities.append(DiskInfoEntity(coordinator, disk_name))

    return entities