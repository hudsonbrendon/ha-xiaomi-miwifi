"""System Health for Xiaomi MiWiFi."""
from __future__ import annotations

from homeassistant.components import system_health
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN


@callback
def async_register(
    hass: HomeAssistant, register: system_health.SystemHealthRegistration
) -> None:
    """Register the system health callback."""
    register.async_register_info(_system_health_info)


async def _system_health_info(hass: HomeAssistant) -> dict:
    coordinators = list(hass.data.get(DOMAIN, {}).values())
    if not coordinators:
        return {"routers": 0}
    coord = coordinators[0]
    data = coord.data
    return {
        "routers": len(coordinators),
        "reachable": coord.last_update_success and data.online,
        "firmware": data.firmware_version,
        "devices": data.client_count,
        "mesh_nodes": data.mesh_node_count,
    }
