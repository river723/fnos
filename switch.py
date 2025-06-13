# fnos/switch.py

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from .const import CONF_PASSWORD, DOMAIN
import logging


_LOGGER = logging.getLogger(__name__)

SWITCH_TYPES = {
    "reboot": {
        "name": "重启设备",
        "icon": "mdi:restart",
    },
    "shutdown": {
        "name": "关闭设备",
        "icon": "mdi:power",
    },
}

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: dict,
    async_add_entities
):
    """设置开关实体"""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    switches = []
    for switch_type in SWITCH_TYPES:
        switches.append(FnosSwitch(coordinator, switch_type, config_entry.entry_id, config_entry))

    async_add_entities(switches)


class FnosSwitch(SwitchEntity):
    def __init__(self, coordinator, switch_type, entry_id, config_entry):
        self.coordinator = coordinator
        self._switch_type = switch_type
        self._is_on = False
        self._entry_id = entry_id
        self.config_entry = config_entry

    @property
    def name(self):
        return f"{SWITCH_TYPES[self._switch_type]['name']}"

    @property
    def is_on(self):
        return self._is_on

    @property
    def icon(self):
        return SWITCH_TYPES[self._switch_type]["icon"]

    @property
    def unique_id(self):
        return f"{self._entry_id}_{self._switch_type}"

    async def async_turn_on(self, **kwargs):
        """通过 SSH 执行重启或关机命令"""
        try:
            if not self.coordinator.ssh or not self.coordinator._is_ssh_active():
                await self.coordinator.connect_ssh()  # 确保 SSH 连接可用

            command = "reboot" if self._switch_type == "reboot" else "shutdown -h now"
            full_command = f"echo '{self.config_entry.data[CONF_PASSWORD]}' | sudo -S {command}"
            _LOGGER.info(f"正在执行远程命令: {full_command}")

            stdin, stdout, stderr = await self.hass.async_add_executor_job(
                self.coordinator.ssh.exec_command, full_command, True  # get_pty=True
            )

            exit_code = stdout.channel.recv_exit_status()
            if exit_code != 0:
                error_output = stderr.read().decode()
                _LOGGER.error(f"命令执行失败: {error_output}")
            else:
                _LOGGER.info(f"成功执行远程命令: {command}")
                self._is_on = True
                self.async_write_ha_state()

        except Exception as e:
            _LOGGER.error(f"执行远程命令失败: {e}", exc_info=True)
    async def async_turn_off(self, **kwargs):
        """保持关闭状态"""
        self._is_on = False
        self.async_write_ha_state()