"""The Xiaomi MiWiFi integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import format_mac

from xiaomi_miwifi import MiWiFiClient

from .const import (
    CONF_CONSIDER_HOME,
    CONF_EXCLUDED_MACS,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    DEFAULT_CONSIDER_HOME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import XiaomiMiWiFiCoordinator

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.DEVICE_TRACKER,
    Platform.SELECT,
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
SERVICE_RUN_SPEED_TEST = "run_speed_test"
SERVICE_ADD_PORT_FORWARD = "add_port_forward"
SERVICE_DELETE_PORT_FORWARD = "delete_port_forward"
SERVICE_SET_DMZ = "set_dmz"
SERVICE_CLEAR_DMZ = "clear_dmz"
SERVICE_SET_DDNS = "set_ddns"

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
ENTRY_ONLY_SCHEMA = vol.Schema({vol.Required(ATTR_ENTRY_ID): cv.string})
ADD_PORT_FORWARD_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Required("ip"): cv.string,
        vol.Required("name"): cv.string,
        vol.Required("proto"): vol.All(int, vol.Range(min=1, max=3)),
        vol.Required("source_port"): vol.All(int, vol.Range(min=1, max=65535)),
        vol.Required("dest_port"): vol.All(int, vol.Range(min=1, max=65535)),
    }
)
DELETE_PORT_FORWARD_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTRY_ID): cv.string,
        vol.Required("source_port"): vol.All(int, vol.Range(min=1, max=65535)),
    }
)
SET_DMZ_SCHEMA = vol.Schema(
    {vol.Required(ATTR_ENTRY_ID): cv.string, vol.Required("ip"): cv.string}
)
SET_DDNS_SCHEMA = vol.Schema(
    {vol.Required(ATTR_ENTRY_ID): cv.string, vol.Required("enabled"): cv.boolean}
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

    async def _run_speed_test(call: ServiceCall) -> None:
        coord = _coordinator(call)
        await coord.client.async_run_speed_test()
        await coord.async_request_refresh()

    async def _add_port_forward(call: ServiceCall) -> None:
        coord = _coordinator(call)
        if not await coord.client.async_add_port_forward(
            call.data["ip"],
            call.data["name"],
            call.data["proto"],
            call.data["source_port"],
            call.data["dest_port"],
        ):
            raise HomeAssistantError("Failed to add port forward")
        await coord.async_request_refresh()

    async def _delete_port_forward(call: ServiceCall) -> None:
        coord = _coordinator(call)
        if not await coord.client.async_delete_port_forward(call.data["source_port"]):
            raise HomeAssistantError("Failed to delete port forward")
        await coord.async_request_refresh()

    async def _set_dmz(call: ServiceCall) -> None:
        coord = _coordinator(call)
        if not await coord.client.async_set_dmz(call.data["ip"]):
            raise HomeAssistantError("Failed to set DMZ")
        await coord.async_request_refresh()

    async def _clear_dmz(call: ServiceCall) -> None:
        coord = _coordinator(call)
        if not await coord.client.async_clear_dmz():
            raise HomeAssistantError("Failed to clear DMZ")
        await coord.async_request_refresh()

    async def _set_ddns(call: ServiceCall) -> None:
        coord = _coordinator(call)
        if not await coord.client.async_set_ddns(call.data["enabled"]):
            raise HomeAssistantError("Failed to set DDNS")
        await coord.async_request_refresh()

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
    hass.services.async_register(
        DOMAIN, SERVICE_RUN_SPEED_TEST, _run_speed_test, ENTRY_ONLY_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_PORT_FORWARD, _add_port_forward, ADD_PORT_FORWARD_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_PORT_FORWARD,
        _delete_port_forward,
        DELETE_PORT_FORWARD_SCHEMA,
    )
    hass.services.async_register(DOMAIN, SERVICE_SET_DMZ, _set_dmz, SET_DMZ_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_CLEAR_DMZ, _clear_dmz, ENTRY_ONLY_SCHEMA
    )
    hass.services.async_register(DOMAIN, SERVICE_SET_DDNS, _set_ddns, SET_DDNS_SCHEMA)


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
    coordinator.entry_id = entry.entry_id
    coordinator.consider_home = entry.options.get(
        CONF_CONSIDER_HOME, DEFAULT_CONSIDER_HOME
    )
    raw_excl = entry.options.get(CONF_EXCLUDED_MACS, "")
    coordinator.excluded_macs = {
        m.strip().upper() for m in raw_excl.split(",") if m.strip()
    }
    await coordinator.async_config_entry_first_refresh()
    await coordinator.async_load_channels()

    if entry.unique_id is None or "." in (entry.unique_id or ""):
        mac = coordinator.data.mac
        if mac:
            hass.config_entries.async_update_entry(
                entry, unique_id=format_mac(mac)
            )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    _register_services(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    from .discovery import async_correlate_and_discover

    @callback
    def _mesh_update() -> None:
        async_correlate_and_discover(hass, entry, coordinator.data)

    entry.async_on_unload(coordinator.async_add_listener(_mesh_update))
    _mesh_update()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
