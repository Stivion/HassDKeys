"""Модуль содержит сущность - кнопку."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import DKeysConfigEntry


async def async_setup_entry(
    _: HomeAssistant,
    entry: DKeysConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Настройка Button platform."""
    async_add_entities(
        [
            DKeysButton(
                entry=entry,
                entity_description=ButtonEntityDescription(
                    key="open", translation_key="open", icon="mdi:lock-open"
                ),
            )
        ]
    )


class DKeysButton(ButtonEntity):
    """Кнопка ключа DKeys."""

    def __init__(
        self,
        entry: DKeysConfigEntry,
        entity_description: ButtonEntityDescription,
    ) -> None:
        super().__init__()
        self.entity_description = entity_description
        self._attr_unique_id = f"{entry.entry_id}_{entity_description.key}"
        self._attr_has_entity_name = True
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, "123")},
            name="Имя устройства",
            manufacturer="D-Keys",
            model="Шлагбаум",
        )

    def press(self) -> None:
        """Обработка нажатия на кнопку."""
        LOGGER.info("On Press")
