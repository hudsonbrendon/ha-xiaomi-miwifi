"""Mesh correlation and peer discovery for Xiaomi MiWiFi.

Only the gateway (router mode 0) knows the mesh topology, so it drives
everything: for each leaf it either links the already-configured device via
`via_device`, or fires an integration_discovery flow so the user can add it.
"""
from __future__ import annotations

from homeassistant.config_entries import SOURCE_INTEGRATION_DISCOVERY, ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import discovery_flow

from xiaomi_miwifi import MiWiFiStatus

from .const import DOMAIN


@callback
def _entry_for_host(hass: HomeAssistant, host: str) -> ConfigEntry | None:
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data.get(CONF_HOST) == host:
            return entry
    return None


@callback
def _router_device(hass: HomeAssistant, entry_id: str) -> dr.DeviceEntry | None:
    reg = dr.async_get(hass)
    devices = dr.async_entries_for_config_entry(reg, entry_id)
    return devices[0] if devices else None


@callback
def async_correlate_and_discover(
    hass: HomeAssistant, entry: ConfigEntry, status: MiWiFiStatus
) -> None:
    """Driven from the gateway entry on every successful refresh."""
    if not status.online or status.mode != 0:
        return  # only the gateway drives the mesh
    reg = dr.async_get(hass)
    gw_device = _router_device(hass, entry.entry_id)
    for node in status.mesh_nodes:
        if not node.ip:
            continue
        peer = _entry_for_host(hass, node.ip)
        if peer is not None:
            leaf_device = _router_device(hass, peer.entry_id)
            if (
                gw_device is not None
                and leaf_device is not None
                and leaf_device.via_device_id != gw_device.id
            ):
                reg.async_update_device(leaf_device.id, via_device_id=gw_device.id)
            continue
        discovery_flow.async_create_flow(
            hass,
            DOMAIN,
            context={"source": SOURCE_INTEGRATION_DISCOVERY},
            data={
                CONF_HOST: node.ip,
                "name": node.name,
                "hardware": node.hardware,
                "parent_mac": status.mac,
            },
        )
