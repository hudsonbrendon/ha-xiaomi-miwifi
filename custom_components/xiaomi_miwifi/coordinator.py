"""DataUpdateCoordinator for the Xiaomi MiWiFi integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from xiaomi_miwifi import (
    ClientDevice,
    MiWiFiClient,
    MiWiFiConnectionError,
    MiWiFiError,
    MiWiFiStatus,
)

from .const import (
    DEFAULT_CONSIDER_HOME,
    DOMAIN,
    EVENT_DEVICE_CONNECTED,
    EVENT_DEVICE_DISCONNECTED,
    EVENT_NEW_DEVICE,
)

_LOGGER = logging.getLogger(__name__)


class XiaomiMiWiFiCoordinator(DataUpdateCoordinator[MiWiFiStatus]):
    """Polls the MiWiFi router and exposes a MiWiFiStatus to entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: MiWiFiClient,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client
        self.entry_id: str | None = None
        self.clients: list[ClientDevice] = []
        self.channels_24g: list[str] = []
        self.channels_5g: list[str] = []
        self.consider_home: int = DEFAULT_CONSIDER_HOME
        self.excluded_macs: set[str] = set()
        self.last_seen: dict[str, object] = {}
        self._known_online: set[str] = set()
        self._known_macs: set[str] = set()

    async def async_load_channels(self) -> None:
        """Fetch the available channel lists once (they don't change)."""
        try:
            self.channels_24g = await self.client.async_get_available_channels(1)
            self.channels_5g = await self.client.async_get_available_channels(2)
        except MiWiFiError:
            self.channels_24g = []
            self.channels_5g = []

    def _process_device_events(self) -> None:
        from homeassistant.util import dt as dt_util

        now = dt_util.utcnow()
        online_now = {
            c.mac.upper() for c in self.clients
            if c.online and c.mac.upper() not in self.excluded_macs
        }
        for c in self.clients:
            mac = c.mac.upper()
            if mac in self.excluded_macs:
                continue
            payload = {"mac": c.mac, "name": c.name, "ip": c.ip}
            if mac not in self._known_macs:
                self._known_macs.add(mac)
                self.hass.bus.async_fire(EVENT_NEW_DEVICE, payload)
            if c.online and mac not in self._known_online:
                self.hass.bus.async_fire(EVENT_DEVICE_CONNECTED, payload)
            if c.online:
                self.last_seen[mac] = now
        for mac in self._known_online - online_now:
            self.hass.bus.async_fire(EVENT_DEVICE_DISCONNECTED, {"mac": mac})
        self._known_online = online_now

    async def _async_update_data(self) -> MiWiFiStatus:
        try:
            status = await self.client.async_get_status()
        except MiWiFiConnectionError as err:
            _LOGGER.debug("MiWiFi unreachable: %s", err)
            return MiWiFiStatus(online=False)
        try:
            self.clients = await self.client.async_get_clients()
        except MiWiFiConnectionError as err:
            _LOGGER.debug("MiWiFi client list fetch failed: %s", err)
            self.clients = []
        if status.online:
            self._process_device_events()
            if self.entry_id:
                from .repairs import async_check_issues

                async_check_issues(self.hass, self.entry_id, self)
        return status
