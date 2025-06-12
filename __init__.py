from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .sensor import FnosDataCoordinator
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """确保正确初始化"""
    hass.data.setdefault(DOMAIN, {})
    
    # 存储coordinator供其他平台使用
    coordinator = FnosDataCoordinator(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # 触发传感器平台加载
    await hass.config_entries.async_forward_entry_setup(entry, "sensor")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
