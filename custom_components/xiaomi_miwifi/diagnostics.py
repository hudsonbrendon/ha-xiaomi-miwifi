"""Diagnostics for the Xiaomi MiWiFi integration."""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_PASSWORD, DOMAIN
from .coordinator import XiaomiMiWiFiCoordinator

TO_REDACT = {CONF_PASSWORD, "serial", "mac", "wan_ip", "wan_gateway"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    coordinator: XiaomiMiWiFiCoordinator = hass.data[DOMAIN][entry.entry_id]
    status = asdict(coordinator.data)
    return {
        "entry": async_redact_data(dict(entry.data), TO_REDACT),
        "status": async_redact_data(status, TO_REDACT),
        "client_count": len(coordinator.clients),
    }
