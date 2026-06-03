"""Repair issues for the Xiaomi MiWiFi integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import issue_registry as ir
from xiaomi_miwifi import SUPPORTED_ROUTERS

from .const import DOMAIN


@callback
def async_check_issues(hass: HomeAssistant, entry_id: str, coordinator) -> None:
    """Create or clear repair issues based on the latest router status."""
    data = coordinator.data

    fw_id = f"firmware_update_available_{entry_id}"
    if data.update_available:
        ir.async_create_issue(
            hass,
            DOMAIN,
            fw_id,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key="firmware_update_available",
            translation_placeholders={"version": data.rom_latest_version or "?"},
        )
    else:
        ir.async_delete_issue(hass, DOMAIN, fw_id)

    hw = (data.hardware or "").upper()
    unsup_id = f"unsupported_router_{entry_id}"
    if hw and hw not in SUPPORTED_ROUTERS:
        ir.async_create_issue(
            hass,
            DOMAIN,
            unsup_id,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key="unsupported_router",
            translation_placeholders={"hardware": hw},
        )
    else:
        ir.async_delete_issue(hass, DOMAIN, unsup_id)
