"""Config flow for the Xiaomi MiWiFi integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from xiaomi_miwifi import MiWiFiAuthError, MiWiFiClient, MiWiFiConnectionError

from .const import (
    CONF_CONSIDER_HOME,
    CONF_EXCLUDED_MACS,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    DEFAULT_CONSIDER_HOME,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class XiaomiMiWiFiConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the Xiaomi MiWiFi config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = MiWiFiClient(
                user_input[CONF_HOST],
                password=user_input[CONF_PASSWORD],
                session=session,
            )
            try:
                await client.async_login()
            except MiWiFiAuthError:
                errors["base"] = "invalid_auth"
            except MiWiFiConnectionError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )
        return self.async_show_form(
            step_id="user", data_schema=USER_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> XiaomiMiWiFiOptionsFlow:
        return XiaomiMiWiFiOptionsFlow(config_entry)


class XiaomiMiWiFiOptionsFlow(OptionsFlow):
    """Handle scan-interval options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        opts = self._entry.options
        current = opts.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        schema = vol.Schema(
            {
                vol.Optional(CONF_SCAN_INTERVAL, default=current): vol.All(
                    int, vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)
                ),
                vol.Optional(
                    CONF_CONSIDER_HOME,
                    default=opts.get(CONF_CONSIDER_HOME, DEFAULT_CONSIDER_HOME),
                ): vol.All(int, vol.Range(min=30, max=1800)),
                vol.Optional(
                    CONF_EXCLUDED_MACS,
                    default=opts.get(CONF_EXCLUDED_MACS, ""),
                ): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
