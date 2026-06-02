"""Device tracker platform for the Xiaomi MiWiFi integration.

Tracks every client that has ever been seen on the router. Once a MAC has
been observed it keeps its tracker forever: when the device drops off the
network the tracker reports ``not home`` instead of disappearing.
"""
from __future__ import annotations

from homeassistant.components.device_tracker import ScannerEntity, SourceType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from xiaomi_miwifi import ClientDevice

from .const import DOMAIN
from .coordinator import XiaomiMiWiFiCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up trackers for known clients and watch for newly-seen MACs."""
    coordinator: XiaomiMiWiFiCoordinator = hass.data[DOMAIN][entry.entry_id]
    tracked: set[str] = set()

    @callback
    def _add_new_trackers() -> None:
        new_entities: list[MiWiFiDeviceTracker] = []
        for client in coordinator.clients:
            if client.mac in tracked:
                continue
            tracked.add(client.mac)
            new_entities.append(
                MiWiFiDeviceTracker(coordinator, entry, client.mac)
            )
        if new_entities:
            async_add_entities(new_entities)

    _add_new_trackers()
    entry.async_on_unload(coordinator.async_add_listener(_add_new_trackers))


class MiWiFiDeviceTracker(CoordinatorEntity[XiaomiMiWiFiCoordinator], ScannerEntity):
    """A standalone tracker for a single client MAC seen on the router."""

    _attr_has_entity_name = False

    def __init__(
        self,
        coordinator: XiaomiMiWiFiCoordinator,
        entry: ConfigEntry,
        mac: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._mac = mac
        self._unique_id = f"{entry.entry_id}_track_{mac}"
        # Cache last-known label/ip so an offline device keeps its name.
        client = self._client()
        self._last_name = client.name if client else mac
        self._last_ip = client.ip if client else None
        self._attr_name = self._last_name

    def _client(self) -> ClientDevice | None:
        for client in self.coordinator.clients:
            if client.mac == self._mac:
                return client
        return None

    @callback
    def _handle_coordinator_update(self) -> None:
        client = self._client()
        if client is not None:
            if client.name:
                self._last_name = client.name
                self._attr_name = client.name
            if client.ip:
                self._last_ip = client.ip
        super()._handle_coordinator_update()

    @property
    def unique_id(self) -> str:
        # ScannerEntity defaults unique_id to the MAC; override so each tracker
        # is namespaced to the config entry per the integration's convention.
        return self._unique_id

    @property
    def is_connected(self) -> bool:
        client = self._client()
        return client is not None and client.online

    @property
    def source_type(self) -> SourceType:
        return SourceType.ROUTER

    @property
    def ip_address(self) -> str | None:
        client = self._client()
        if client is not None and client.ip:
            return client.ip
        return self._last_ip

    @property
    def mac_address(self) -> str | None:
        return self._mac

    @property
    def hostname(self) -> str | None:
        client = self._client()
        if client is not None and client.name:
            return client.name
        return self._last_name
