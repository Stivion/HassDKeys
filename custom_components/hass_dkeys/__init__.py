"""Модуль интеграции Home Assistant с сервисом D-Keys."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import DKeysConfigEntry

PLATFORMS: list[Platform] = [Platform.BUTTON]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DKeysConfigEntry,
) -> bool:
    """Настройка интеграции через UI."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: DKeysConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
