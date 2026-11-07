"""Модуль содержит логику обновления информации о ключах."""

import asyncio
from typing import TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.hass_dkeys.api import (
    DKeysApiClientError,
    DKeysAuthenticationError,
    DKeysKey,
)

from .const import DOMAIN, LOGGER, UPDATE_INTERVAL

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .api import DKeysApiClient
    from .data import DKeysConfigEntry


class DKeysCoordinator(DataUpdateCoordinator[list[DKeysKey]]):
    """Coordinator for HassVk."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: DKeysConfigEntry,
        api: DKeysApiClient,
    ) -> None:
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=UPDATE_INTERVAL,
            always_update=True,
        )
        self.api = api

    async def _async_update_data(self) -> list[DKeysKey]:
        """Получение ключей с API."""
        try:
            async with asyncio.timeout(10):
                return await self.api.get_keys()
        except DKeysAuthenticationError as err:
            raise ConfigEntryAuthFailed from err
        except DKeysApiClientError as err:
            raise UpdateFailed(retry_after=60) from err
