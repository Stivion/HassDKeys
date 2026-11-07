"""Константы."""

from datetime import timedelta
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "hass_dkeys"
KEY_MANUFACTURER = "D-Keys"
UPDATE_INTERVAL = timedelta(seconds=120)

DKEYS_BASE_URL = "https://mde.s-m-d.ru:38257/DKeys_app_3/MAIN.php/"
DKEYS_OS = "android"
DKEYS_LANG = "ru"
DKEYS_APP_VERSION = "5.3.13"
DKEYS_VERSION_OS = "14"
DKEYS_COMMAND_SERVER_NAME = "cmdc"

CONF_PHONE = "phone"
CONF_PHONE_LENGTH = 11
CONF_PIN = "pin"
CONF_PIN_LENGTH = 6
CONF_TOKEN = "token"  # noqa: S105

ERR_INVALID_PHONE_FORMAT = "invalid_phone_format"
ERR_INVALID_PIN_FORMAT = "invalid_pin_format"
ERR_UNKNOWN_AUTHENTICATION_ERROR = "unknown_authentication_error"
