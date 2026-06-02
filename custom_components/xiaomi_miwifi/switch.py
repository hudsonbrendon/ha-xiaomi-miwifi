"""Radio on/off switches for the Xiaomi MiWiFi integration.

These toggle physical radios — disruptive by design. Exposed per the
integration's full-control goal; never exercised against the live network
in tests.
"""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import XiaomiMiWiFiCoordinator
from .entity import XiaomiMiWiFiEntity

RADIO_SWITCHES: tuple[dict, ...] = (
    {"key": "wifi_5g", "ifname": "wl0", "translation_key": "wifi_5g"},
    {"key": "wifi_24g", "ifname": "wl1", "translation_key": "wifi_24g"},
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: XiaomiMiWiFiCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        MiWiFiRadioSwitch(coordinator, entry, spec) for spec in RADIO_SWITCHES
    )


class MiWiFiRadioSwitch(XiaomiMiWiFiEntity, SwitchEntity):
    """Enable/disable one radio. State is optimistic (no read-back endpoint)."""

    _attr_icon = "mdi:wifi"

    def __init__(
        self,
        coordinator: XiaomiMiWiFiCoordinator,
        entry: ConfigEntry,
        spec: dict,
    ) -> None:
        super().__init__(coordinator, entry)
        self._ifname = spec["ifname"]
        self._attr_translation_key = spec["translation_key"]
        self._attr_unique_id = f"{entry.entry_id}_{spec['key']}"
        self._attr_is_on = True

    async def async_turn_on(self, **kwargs: object) -> None:
        if not await self.coordinator.client.async_set_wifi_enabled(
            self._ifname, True
        ):
            raise HomeAssistantError(f"Failed to enable radio {self._ifname}")
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: object) -> None:
        if not await self.coordinator.client.async_set_wifi_enabled(
            self._ifname, False
        ):
            raise HomeAssistantError(f"Failed to disable radio {self._ifname}")
        self._attr_is_on = False
        self.async_write_ha_state()
