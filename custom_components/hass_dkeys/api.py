"""API клиент для D-Keys."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .const import (
    DKEYS_APP_VERSION,
    DKEYS_BASE_URL,
    DKEYS_COMMAND_SERVER_NAME,
    DKEYS_LANG,
    DKEYS_OS,
    DKEYS_VERSION_OS,
    LOGGER,
)

if TYPE_CHECKING:
    from aiohttp import ClientResponse, ClientSession


@dataclass(frozen=True)
class DKeysBaseResponse:
    """Базовый ответ от DKeys API."""

    data: Any
    critical: str
    error: bool
    message: str
    warning: str


@dataclass
class DKeysRegPhoneResponse:
    """Ответ на запрос 'regPhone'."""

    def __init__(self, data: dict) -> None:
        self.result = data["result"]


@dataclass
class DKeysSendPinResponse:
    """Ответ на запрос 'sendPin'."""

    def __init__(self, data: dict) -> None:
        self.phone_number = data["PhoneNumber"]
        self.token = data["Token"]


@dataclass
class DKeysGetServersReponse:
    """Ответ на запрос 'getServers'."""

    def __init__(self, data: list) -> None:
        self.servers = (
            DKeysServer(server=s["server"], domain=s["domen"]) for s in data
        )


@dataclass(frozen=True)
class DKeysServer:
    """Сервер."""

    server: str
    domain: str


@dataclass
class DKeysGetKeyResponse:
    """Ответ на запрос 'getKey'."""

    def __init__(self, data: list) -> None:
        self.keys = (
            DKeysKey(
                address=k["Address"],
                color=k["Color"],
                icon=k["Icon"],
                link=k["Link"],
                nickname=k["Nickname"],
                type_key=k["TypeKey"],
                code_key=k["codeKey"],
                code_mp=k["codeMP"],
                crc=k["crc"],
                expiration_date=k["expirationDate"],
                index_number=k["indexNumber"],
                is_master_key=k["isMasterKey"],
                max_count_forwards=k["maxCountForwards"],
                options_available=k["options_available"],
                options_exist=k["options_exist"],
                promo=k["promo"],
                room_number=k["roomNumber"],
                special_access=k["specialAccess"],
            )
            for k in data
        )


@dataclass(frozen=True)
class DKeysKey:
    """Ключ."""

    address: str
    color: str
    icon: str
    link: str
    nickname: str
    type_key: str
    code_key: str
    code_mp: str
    crc: str
    expiration_date: str
    index_number: str
    is_master_key: str
    max_count_forwards: str
    options_available: list[str]
    options_exist: list[str]
    promo: list[str]
    room_number: str
    special_access: str


@dataclass(frozen=True)
class DKeysGetDataOptionResponse:
    """Ответ на запрос 'getDataOption'."""

    options: dict


@dataclass
class DKeysMqttDataOption:
    """Опции для MQTT."""

    def __init__(self, data: dict) -> None:
        self.open_command = data["openCommand"]
        self.topic_command = data["topicCommand"]
        self.uid = self.topic_command.split("/", 1)[1]


class DKeysApiClientError(Exception):
    """Базовая ошибка с D-Keys API."""

    def __init__(
        self, critical: str, message: str, warning: str, *args: object
    ) -> None:
        super().__init__(*args)
        self.critical = critical
        self.message = message
        self.warning = warning


class DKeysAuthenticationError(DKeysApiClientError):
    """Ошибка аутентификации, critical=12."""


class DKeysBlockedError(DKeysApiClientError):
    """Ключи заблокированны, critical=13."""


class DKeysApiClient:
    """API клиент для D-Keys."""

    def __init__(self, phone: str, token: str, session: ClientSession) -> None:
        self.common_body = {
            "os": DKEYS_OS,
            "lang": DKEYS_LANG,
            "version": DKEYS_APP_VERSION,
            "versionOS": DKEYS_VERSION_OS,
            "mobile": phone,
        }
        self.token = token
        self.session = session

    async def request_phone_authentication(self) -> bool:
        """Запрашивает аутентификацию через звонок на номер телефона."""
        response = await self.__request("regPhone")
        response_data = DKeysRegPhoneResponse(response.data)
        result = response_data.result
        return result == "OK"

    async def confirm_authentication(self, pin: str) -> str:
        """
        Завершает аутентификацию.

        Параметры:
        pin: Последние 6 цифр номер, с которого поступил звонок

        Возвращает: Токен пользователя

        """
        response = await self.__request("sendPin", otp=pin)
        response_data = DKeysSendPinResponse(response.data)
        self.token = response_data.token
        return self.token

    async def get_keys(self) -> list[DKeysKey]:
        """Возвращает список доступных ключей."""
        response = await self.__request("getKey", token=self.token)
        return list(DKeysGetKeyResponse(response.data).keys)

    async def open_door(self, key: DKeysKey) -> bool:
        """Открывает дверь указанным ключем."""
        command_server = await self.__get_command_server()
        key_data_options = await self.__get_key_data_options(key, "mqtt")
        mqtt_option = DKeysMqttDataOption(key_data_options.options["mqtt"])
        return await self.__trigger_key(command_server.domain, mqtt_option)

    async def __request(self, action: str, **kwargs: str) -> DKeysBaseResponse:
        body = {**self.common_body, "action": action, **kwargs}
        async with self.session.post(url=DKEYS_BASE_URL, data=body) as response:
            raw_response_body = await response.json(content_type="text/html")
            response_body = self.__parse_response_body(raw_response_body)
            self.__validate_response(response, response_body)
            return response_body

    async def __json_request(
        self, url: str, action: str, **kwargs: str
    ) -> DKeysBaseResponse:
        body = {**self.common_body, "action": action, **kwargs}
        url = f"{url.rstrip('/')}/{action}"
        async with self.session.post(url=url, json=body) as response:
            raw_response_body = await response.json()
            response_body = self.__parse_response_body(raw_response_body)
            self.__validate_response(response, response_body)
            return response_body

    def __validate_response(
        self, response: ClientResponse, response_body: DKeysBaseResponse
    ) -> None:
        self.__check_for_errors(response_body)
        self.__check_for_critical(response_body)
        if response.status in (401, 403):
            raise DKeysAuthenticationError(
                critical=response_body.critical,
                message=response_body.message,
                warning=response_body.warning,
            )
        response.raise_for_status()

    def __parse_response_body(self, raw_response: dict) -> DKeysBaseResponse:
        return DKeysBaseResponse(
            data=raw_response["DATA"],
            error=raw_response.get("error") or False,
            message=raw_response.get("message") or "",
            warning=raw_response.get("warning") or "",
            critical=raw_response.get("critical") or "",
        )

    def __check_for_errors(self, response_body: DKeysBaseResponse) -> None:
        if response_body.error:
            raise DKeysApiClientError(
                critical=response_body.critical,
                message=response_body.message,
                warning=response_body.warning,
            )

        if response_body.message:
            LOGGER.info(response_body.message)

        if response_body.warning:
            LOGGER.warning(response_body.warning)

    def __check_for_critical(self, response_body: DKeysBaseResponse) -> None:
        critical = response_body.critical or ""
        if critical == "12":
            # Ошибка токена, нужна повторная авторизация
            raise DKeysAuthenticationError(
                critical=response_body.critical,
                message=response_body.message,
                warning=response_body.warning,
            )
        if critical == "13":
            # Ключи заблокированны
            raise DKeysBlockedError(
                critical=response_body.critical,
                message=response_body.message,
                warning=response_body.warning,
            )

    async def __get_servers(self) -> DKeysGetServersReponse:
        """Возвращает список доменов для всех типов запросов к D-Keys API."""
        response = await self.__request("getServers", token=self.token)
        return DKeysGetServersReponse(response.data)

    async def __get_command_server(self) -> DKeysServer:
        """Возвращает адрес сервера для выполнения команд."""
        response = await self.__get_servers()
        server = next(
            (s for s in response.servers if s.server == DKEYS_COMMAND_SERVER_NAME),
            None,
        )
        if server is None:
            msg = "В списке серверов нет сервера для выполнения команд."
            raise RuntimeError(msg)
        return server

    async def __get_key_data_options(
        self, key: DKeysKey, option: str
    ) -> DKeysGetDataOptionResponse:
        """Возвращает опции конкретного ключа."""
        response = await self.__request(
            "getDataOption", option=option, codeKey=key.code_key, token=self.token
        )
        return DKeysGetDataOptionResponse(response.data)

    async def __trigger_key(self, url: str, options: DKeysMqttDataOption) -> bool:
        """Открывает/закрывает указанный ключ."""
        response = await self.__json_request(
            url=url,
            action="openDoor",
            token=self.token,
            topic=options.topic_command,
            command=options.open_command,
            uid=options.uid,
        )
        return response.data == "OK"
