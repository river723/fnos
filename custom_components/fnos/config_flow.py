# config_flow.py

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, DEFAULT_PORT, CONF_HOST, CONF_USERNAME, CONF_PASSWORD, CONF_PORT, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

class FnosConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """FNOS 配置流程"""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    MINOR_VERSION = 2

    async def async_step_user(self, user_input=None):
        """处理用户输入"""
        errors = {}

        if user_input is not None:
            # 设置唯一ID（基于host），防止重复添加
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"FNOS {user_input[CONF_HOST]}",
                data=user_input
            )

        # 显示表单
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
            }),
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return FnosOptionsFlow(config_entry)


class FnosOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema({
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ): int,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )