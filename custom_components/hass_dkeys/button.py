"""Модуль содержит сущность - кнопку для открытия двери."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, KEY_MANUFACTURER, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .api import DKeysKey
    from .data import DKeysConfigEntry


async def async_setup_entry(
    _: HomeAssistant,
    entry: DKeysConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Настройка Button platform."""
    keys = await entry.runtime_data.api.get_keys()
    key_entities = [
        DKeysButton(
            key=key,
            entry=entry,
            entity_description=ButtonEntityDescription(
                key="open", translation_key="open", icon="mdi:lock-open"
            ),
        )
        for key in keys
    ]

    async_add_entities(key_entities)


class DKeysButton(ButtonEntity):
    """Кнопка ключа DKeys."""

    def __init__(
        self,
        key: DKeysKey,
        entry: DKeysConfigEntry,
        entity_description: ButtonEntityDescription,
    ) -> None:
        super().__init__()
        self.entity_description = entity_description
        self.api = entry.runtime_data.api
        self.key = key
        self._attr_unique_id = f"{entry.entry_id}_{entity_description.key}"
        self._attr_has_entity_name = True
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, key.code_key)},
            name=key.nickname,
            manufacturer=KEY_MANUFACTURER,
        )

    async def async_press(self) -> None:
        """Обработка нажатия на кнопку."""
        if not await self.api.open_door(self.key):
            LOGGER.error(
                "Не удалось открыть дверь %s", self.key.nickname, exc_info=True
            )
