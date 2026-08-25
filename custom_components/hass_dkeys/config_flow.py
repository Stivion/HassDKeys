"""Модуль добавляет настройку интеграции через UI."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector
from homeassistant.loader import async_get_loaded_integration

from .const import DOMAIN


class DKeysFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow для интеграции."""

    VERSION = 1
    MINOR_VERSION = 0

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> ConfigFlowResult:
        """Обработка настройки интеграции, вызванной пользователем через UI."""
        _errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        integration = async_get_loaded_integration(self.hass, DOMAIN)

        if integration.documentation is None:
            error_text = f"Integration {DOMAIN} has no documentation URL"
            raise RuntimeError(error_text)

        return self.async_show_form(
            step_id="user",
            description_placeholders={
                "documentation": integration.documentation,
            },
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME,
                        default=(user_input or {}).get(CONF_NAME, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    )
                },
            ),
            errors=_errors,
        )
