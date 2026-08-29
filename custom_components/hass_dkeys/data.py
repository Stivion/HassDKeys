"""Типы данных для интеграции с D-Keys."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .api import DKeysApiClient
    from .coordinator import DKeysCoordinator


type DKeysConfigEntry = ConfigEntry[DKeysData]


@dataclass
class DKeysData:
    """Данные для интеграции D-Keys."""

    api: DKeysApiClient
    coordinator: DKeysCoordinator
