"""Модуль содержит сущность - сенсор с кодом открытия двери."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, KEY_MANUFACTURER
from .coordinator import DKeysCoordinator

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
    """Настройка Sensor platform."""
    keys = await entry.runtime_data.api.get_keys()
    sensor_entities = [
        DKeysSensor(
            key=key,
            entry=entry,
            entity_description=SensorEntityDescription(
                key="access_code", translation_key="access_code", icon="mdi:onepassword"
            ),
        )
        for key in keys
        if key.special_access
    ]

    async_add_entities(sensor_entities)


class DKeysSensor(CoordinatorEntity[DKeysCoordinator], SensorEntity):
    """Код открытия двери DKeys."""

    def __init__(
        self,
        key: DKeysKey,
        entry: DKeysConfigEntry,
        entity_description: SensorEntityDescription,
    ) -> None:
        super().__init__(entry.runtime_data.coordinator)
        self.entity_description = entity_description
        self.key = key
        self._attr_unique_id = f"{entry.entry_id}_{entity_description.key}"
        self._attr_has_entity_name = True
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, key.code_key)},
            name=key.nickname,
            manufacturer=KEY_MANUFACTURER,
        )

    @property
    def native_value(self) -> str | None:
        """Возвращает код доступа ключа."""
        for key in self.coordinator.data:
            if self.key.code_key == key.code_key:
                self.key = key
                break
        return self.key.special_access
