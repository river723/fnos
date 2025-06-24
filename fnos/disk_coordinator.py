# disk_coordinator.py

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta


class DiskDataCoordinator(DataUpdateCoordinator):
    """专门用于更新磁盘相关数据的协调器"""

    def __init__(self, hass, config_entry, main_coordinator):
        """
        初始化磁盘专用协调器

        :param hass: HomeAssistant 实例
        :param config_entry: 配置条目
        :param main_coordinator: 主协调器实例，用于共享数据
        """
        super().__init__(
            hass,
            name="DiskDataCoordinator",
            logger=main_coordinator.logger,
            update_interval=timedelta(seconds=config_entry.options.get("scan_interval", 300)),
        )
        self.config_entry = config_entry
        self.main_coordinator = main_coordinator

    async def _async_update_data(self):
        """从主协调器中提取磁盘相关数据"""
        return {
            "disk_info": self.main_coordinator.data.get("disk_info", []),
            "disk_temps": self.main_coordinator.data.get("disk_temps", {}),
            "disk_speeds": self.main_coordinator.data.get("disk_speeds", {}),
        }