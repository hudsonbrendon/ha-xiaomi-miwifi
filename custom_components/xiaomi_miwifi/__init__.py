"""The Xiaomi MiWiFi integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from xiaomi_miwifi import MiWiFiClient

from .const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import XiaomiMiWiFiCoordinator

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.DEVICE_TRACKER,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.UPDATE,
]

ATTR_ENTRY_ID = "entry_id"

SERVICE_ADD_RESERVATION = "add_dhcp_reservation"
SERVICE_REMOVE_RESERVATION = "remove_dhcp_reservation"
SERVICE_BLOCK_DEVICE = "block_device"
SERVICE_UNBLOCK_DEVICE = "unblock_device"
SERVICE_LUCI_REQUEST = "luci_request"

ADD_RESERVATION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Required("mac"): cv.string,
        vol.Required("ip"): cv.string,
        vol.Required("name"): cv.string,
    }
)
REMOVE_RESERVATION_SCHEMA = vol.Schema(
    {vol.Required(ATTR_ENTRY_ID): cv.string, vol.Required("mac"): cv.string}
)
BLOCK_DEVICE_SCHEMA = vol.Schema(
    {vol.Required(ATTR_ENTRY_ID): cv.string, vol.Required("mac"): cv.string}
)
UNBLOCK_DEVICE_SCHEMA = vol.Schema(
    {vol.Required(ATTR_ENTRY_ID): cv.string, vol.Required("mac"): cv.string}
)
LUCI_REQUEST_SCHEMA = vol.Schema(
    {vol.Required(ATTR_ENTRY_ID): cv.string, vol.Required("path"): cv.string}
)


def _register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_ADD_RESERVATION):
        return

    def _coordinator(call: ServiceCall) -> XiaomiMiWiFiCoordinator:
        entry_id = call.data[ATTR_ENTRY_ID]
        if entry_id not in hass.data.get(DOMAIN, {}):
            raise ServiceValidationError(f"Config entry '{entry_id}' not found")
        return hass.data[DOMAIN][entry_id]

    async def _add_reservation(call: ServiceCall) -> None:
        coord = _coordinator(call)
        if not await coord.client.async_add_dhcp_reservation(
            call.data["mac"], call.data["ip"], call.data["name"]
        ):
            raise HomeAssistantError("Failed to add the DHCP reservation")
        await coord.async_request_refresh()

    async def _remove_reservation(call: ServiceCall) -> None:
        coord = _coordinator(call)
        if not await coord.client.async_remove_dhcp_reservation(call.data["mac"]):
            raise HomeAssistantError("Failed to remove the DHCP reservation")
        await coord.async_request_refresh()

    async def _block_device(call: ServiceCall) -> None:
        coord = _coordinator(call)
        if not await coord.client.async_block_device(call.data["mac"]):
            raise HomeAssistantError("Failed to block the device")
        await coord.async_request_refresh()

    async def _unblock_device(call: ServiceCall) -> None:
        coord = _coordinator(call)
        if not await coord.client.async_unblock_device(call.data["mac"]):
            raise HomeAssistantError("Failed to unblock the device")
        await coord.async_request_refresh()

    async def _luci_request(call: ServiceCall) -> dict:
        coord = _coordinator(call)
        return await coord.client.async_luci_request(call.data["path"])

    hass.services.async_register(
        DOMAIN, SERVICE_ADD_RESERVATION, _add_reservation, ADD_RESERVATION_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_RESERVATION,
        _remove_reservation,
        REMOVE_RESERVATION_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_BLOCK_DEVICE, _block_device, BLOCK_DEVICE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_UNBLOCK_DEVICE, _unblock_device, UNBLOCK_DEVICE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_LUCI_REQUEST,
        _luci_request,
        LUCI_REQUEST_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Xiaomi MiWiFi from a config entry."""
    session = async_get_clientsession(hass)
    client = MiWiFiClient(
        entry.data[CONF_HOST],
        password=entry.data[CONF_PASSWORD],
        session=session,
    )
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    coordinator = XiaomiMiWiFiCoordinator(hass, client, scan_interval)
    await coordinator.async_config_entry_first_refresh()
    await coordinator.async_load_channels()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    _register_services(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
