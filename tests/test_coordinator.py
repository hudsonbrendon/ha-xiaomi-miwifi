from unittest.mock import AsyncMock

from homeassistant.core import HomeAssistant

from custom_components.xiaomi_miwifi.coordinator import (
    XiaomiMiWiFiCoordinator,
)
from tests.conftest import make_status


async def test_coordinator_returns_status(hass: HomeAssistant):
    client = AsyncMock()
    client.async_get_status.return_value = make_status(True)
    client.async_get_clients.return_value = []
    coordinator = XiaomiMiWiFiCoordinator(hass, client, 30)
    await coordinator.async_refresh()
    assert coordinator.data.online is True
    assert coordinator.data.client_count == 90


async def test_coordinator_offline_is_not_fatal(hass: HomeAssistant):
    from xiaomi_miwifi import MiWiFiConnectionError

    client = AsyncMock()
    client.async_get_status.side_effect = MiWiFiConnectionError("down")
    coordinator = XiaomiMiWiFiCoordinator(hass, client, 30)
    await coordinator.async_refresh()
    assert coordinator.data.online is False
