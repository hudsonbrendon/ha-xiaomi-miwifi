"""Reboot button for the MiWiFi integration (disruptive, exposed)."""
from __future__ import annotations

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import XiaomiMiWiFiCoordinator
from .entity import XiaomiMiWiFiEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: XiaomiMiWiFiCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            MiWiFiRebootButton(coordinator, entry),
            MiWiFiSpeedTestButton(coordinator, entry),
        ]
    )


class MiWiFiRebootButton(XiaomiMiWiFiEntity, ButtonEntity):
    _attr_translation_key = "reboot"
    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: XiaomiMiWiFiCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_reboot"

    async def async_press(self) -> None:
        if not await self.coordinator.client.async_reboot():
            raise HomeAssistantError("Failed to reboot the router")


class MiWiFiSpeedTestButton(XiaomiMiWiFiEntity, ButtonEntity):
    """Triggers a WAN speed test on the router (briefly saturates the link)."""

    _attr_translation_key = "speed_test"
    _attr_icon = "mdi:speedometer"

    def __init__(
        self,
        coordinator: XiaomiMiWiFiCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_speed_test"

    async def async_press(self) -> None:
        await self.coordinator.client.async_run_speed_test()
        await self.coordinator.async_request_refresh()
