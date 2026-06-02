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
    MiWiFiStatus,
)

from .const import DOMAIN

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
        self.clients: list[ClientDevice] = []

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
        return status
