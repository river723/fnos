# -*- coding: utf-8 -*-
"""
FNOS 传感器模块，用于通过 SSH 获取远程服务器状态（CPU、内存、磁盘使用率）。
"""

import logging
import paramiko
import backoff 
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, SENSOR_TYPES, DEFAULT_SCAN_INTERVAL, CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_PORT, CONF_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    根据配置条目初始化传感器实体。

    参数：
        hass (HomeAssistant): Home Assistant 核心对象。
        config_entry (ConfigEntry): 配置条目，包含用户输入的连接信息。
        async_add_entities (AddEntitiesCallback): 回调函数，用于添加传感器实体。
    """
    # 创建数据协调器，用于定期更新远程服务器数据
    coordinator = FnosDataCoordinator(hass, config_entry)
    await coordinator.async_config_entry_first_refresh()

    # 构建所有传感器实例
    sensors = [
        FnosSensor(coordinator, config_entry, sensor_type)
        for sensor_type in SENSOR_TYPES
    ]
    # 添加传感器到系统，并在添加前刷新一次数据
    async_add_entities(sensors, update_before_add=True)


class FnosDataCoordinator(DataUpdateCoordinator):
    """数据协调器：定期通过 SSH 获取远程服务器状态数据。"""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """
        初始化数据协调器。

        参数：
            hass (HomeAssistant): Home Assistant 核心对象。
            config_entry (ConfigEntry): 配置条目，包含连接参数。
        """
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=config_entry.options.get(
                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
            ))
        )
        self.config_entry = config_entry
        self.ssh = None  # 缓存 SSH 连接
    async def connect_ssh(self):
        """建立或复用 SSH 连接"""
        if self.ssh and self._is_ssh_active():
            return

        try:
            if self.ssh:
                self.ssh.close()
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            host = self.config_entry.data[CONF_HOST]
            port = self.config_entry.data.get(CONF_PORT, 22)
            username = self.config_entry.data[CONF_USERNAME]
            password = self.config_entry.data.get(CONF_PASSWORD)
            

           
            # 使用密码认证
            await self.hass.async_add_executor_job(
                    self.ssh.connect,
                    host, port, username, password, None, None, None, 10
                )

            _LOGGER.debug("SSH连接成功")

        except Exception as e:
            _LOGGER.error("SSH连接失败: %s", e)
            self.ssh = None
            raise

    def _is_ssh_active(self):
        """检查当前 SSH 是否活跃"""
        return self.ssh and self.ssh.get_transport() and self.ssh.get_transport().is_active()

    @backoff.on_exception(backoff.expo, (paramiko.SSHException, ConnectionResetError), max_tries=3)
    async def _async_update_data(self):
        """
        异步更新数据的方法，执行 SSH 连接并获取远程服务器状态。

        返回：
            dict: 包含 CPU、内存、磁盘使用率的字典数据。
        """
        # 定义远程服务器执行的命令（获取 CPU、内存、磁盘使用率）
        # SSH_COMMAND = "echo \"cpu:$(top -bn1 | grep load | awk '{printf \"%.1f\", $(NF-2)}');mem:$(free | grep Mem | awk '{print $3/$2 * 100.0}');disk:$(df -h / | tail -n1 | awk '{print $5}' | tr -d '%')\""
        try:
            await self.connect_ssh()

            stdin, stdout, stderr = await self.hass.async_add_executor_job(
                self.ssh.exec_command, "echo \"CPU:$(top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}');"
                "MEMORY:$(free | awk 'NR==2{printf \"%.1f\", $3/$2 * 100}');"
                "DISK:$(df --output=pcent / | awk 'NR==2{print $1}' | tr -d '%')\""
            )

            output = stdout.read().decode().strip()
            _LOGGER.debug("命令输出: %s", output)

            data = {}
            for item in output.split(';'):
                if ':' in item:
                    key, value = item.split(':', 1)
                    try:
                        data[key.lower()] = float(value)
                    except ValueError:
                        _LOGGER.warning(f"无法解析数据项: {item}")
            return data

        except Exception as e:
            _LOGGER.error("数据获取失败: %s", e, exc_info=True)
            self.ssh = None  # 断开后下次自动重连
            raise

    async def shutdown(self):
        """关闭 SSH 连接"""
        if self.ssh:
            await self.hass.async_add_executor_job(self.ssh.close)
            _LOGGER.debug("SSH连接已关闭")


class FnosSensor(CoordinatorEntity, SensorEntity):
    """FNOS 传感器实体类，表示一个具体的传感器。"""

    def __init__(
        self,
        coordinator: FnosDataCoordinator,
        config_entry: ConfigEntry,
        sensor_type: str
    ):
        """
        初始化传感器实体。

        参数：
            coordinator (FnosDataCoordinator): 数据协调器，提供共享数据。
            config_entry (ConfigEntry): 配置条目。
            sensor_type (str): 传感器类型（如 cpu、mem、disk）。
        """
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._type = sensor_type
        # 修改为中文名称
        sensor_names = {
            'cpu': 'CPU 使用率',
            'memory': '内存使用率',
            'disk': '磁盘使用率'
        }
        self._attr_name = sensor_names.get(sensor_type, sensor_type) #f"FNOS {SENSOR_TYPES[sensor_type][0]}"
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_type}"
        self._attr_native_unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self._attr_icon = SENSOR_TYPES[sensor_type][2]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=f"FNOS {config_entry.data[CONF_HOST]}",
            manufacturer="FNOS",
            # configuration_url=f"ssh://{config_entry.data[CONF_HOST]}"
        )

    @property
    def native_value(self):
        """
        返回当前传感器类型的数值。

        返回：
            float: 当前传感器值（从协调器中获取）。
        """
        return self.coordinator.data.get(self._type)