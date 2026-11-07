"""Модуль интеграции Home Assistant с сервисом D-Keys."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DKeysApiClient
from .const import CONF_PHONE, CONF_TOKEN
from .coordinator import DKeysCoordinator
from .data import DKeysData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import DKeysConfigEntry

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.SENSOR]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DKeysConfigEntry,
) -> bool:
    """Настройка интеграции через UI."""
    api = DKeysApiClient(
        phone=entry.data[CONF_PHONE],
        token=entry.data[CONF_TOKEN],
        session=async_get_clientsession(hass, verify_ssl=False),
    )
    coordinator = DKeysCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = DKeysData(api=api, coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: DKeysConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
