"""Модуль добавляет настройку интеграции через UI."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from custom_components.hass_dkeys.api import DKeysApiClient, DKeysApiClientError

from .const import (
    CONF_PHONE,
    CONF_PHONE_LENGTH,
    CONF_PIN,
    CONF_PIN_LENGTH,
    CONF_TOKEN,
    DOMAIN,
    ERR_INVALID_PHONE_FORMAT,
    ERR_INVALID_PIN_FORMAT,
    ERR_UNKNOWN_AUTHENTICATION_ERROR,
)


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
            phone = user_input[CONF_PHONE]
            if not self.__validate_phone_number(phone):
                _errors[CONF_PHONE] = ERR_INVALID_PHONE_FORMAT

            if not _errors:
                api = DKeysApiClient(
                    phone, "", async_get_clientsession(self.hass, verify_ssl=False)
                )
                try:
                    if await api.request_phone_authentication():
                        self.phone = phone
                        self.api = api
                        return await self.async_step_verify(user_input)

                    _errors["base"] = ERR_UNKNOWN_AUTHENTICATION_ERROR
                except DKeysApiClientError as err:
                    _errors["base"] = err.message

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
                        CONF_PHONE,
                        default=(user_input or {}).get(CONF_PHONE, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEL)
                    )
                },
            ),
            errors=_errors,
        )

    async def async_step_verify(self, user_input: dict) -> ConfigFlowResult:
        """Обработка подтверждения аутентификации в D-Keys."""
        _errors = {}
        pin = user_input.get(CONF_PIN)
        if pin is not None:
            if not self.__validate_pin(pin):
                _errors[CONF_PIN] = ERR_INVALID_PIN_FORMAT

            if not _errors:
                try:
                    token = await self.api.confirm_authentication(pin)

                    return self.async_create_entry(
                        title=self.phone,
                        data={
                            CONF_PHONE: self.phone,
                            CONF_TOKEN: token,
                        },
                    )
                except DKeysApiClientError as err:
                    _errors["base"] = err.message

        return self.async_show_form(
            step_id="verify",
            description_placeholders={CONF_PHONE: self.phone},
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PIN,
                        default=(user_input or {}).get(CONF_PIN, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                    )
                }
            ),
            errors=_errors,
        )

    @staticmethod
    def __validate_phone_number(phone: str) -> bool:
        return not (
            len(phone) != CONF_PHONE_LENGTH
            or not phone.isdigit()
            or not phone.startswith("7")
        )

    @staticmethod
    def __validate_pin(pin: str) -> bool:
        return len(pin) == CONF_PIN_LENGTH and pin.isdigit()
