# fnos/button.py

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from .const import CONF_PASSWORD, DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

BUTTON_TYPES = {
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
    """设置按钮实体"""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # 等待协调器完成首次数据刷新
    await coordinator.async_config_entry_first_refresh()

    buttons = []
    for button_type in BUTTON_TYPES:
        buttons.append(FnosButton(coordinator, button_type, config_entry.entry_id, config_entry))

    async_add_entities(buttons)


class FnosButton(ButtonEntity):
    def __init__(self, coordinator, button_type, entry_id, config_entry):
        self.coordinator = coordinator
        self._button_type = button_type
        self._entry_id = entry_id
        self.config_entry = config_entry

    @property
    def name(self):
        return f"{BUTTON_TYPES[self._button_type]['name']}"

    @property
    def icon(self):
        return BUTTON_TYPES[self._button_type]["icon"]

    @property
    def unique_id(self):
        return f"{self._entry_id}_{self._button_type}"
    
    @property
    def entity_category(self):  
        return EntityCategory.CONFIG
        
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry_id)},  # 👈 必须与集成主设备的 identifiers 一致
            "name": "FNOS NAS",
            "manufacturer": "FNOS",
            "model": "NAS",
            "sw_version": "1.0"
        }

    async def async_press(self):
        """通过 SSH 执行重启或关机命令"""
        try:
            if not self.coordinator.ssh or not self.coordinator._is_ssh_active():
                await self.coordinator.connect_ssh()  # 确保 SSH 连接可用

            command = "reboot" if self._button_type == "reboot" else "shutdown -h now"
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

        except Exception as e:
            _LOGGER.error(f"执行远程命令失败: {e}", exc_info=True)