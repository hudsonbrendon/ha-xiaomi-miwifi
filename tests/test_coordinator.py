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


async def test_coordinator_loads_available_channels(hass: HomeAssistant):
    from custom_components.xiaomi_miwifi.coordinator import (
        XiaomiMiWiFiCoordinator,
    )
    from tests.conftest import make_status

    client = AsyncMock()
    client.async_get_status.return_value = make_status(True)
    client.async_get_clients.return_value = []
    client.async_get_available_channels.side_effect = (
        lambda idx: ["0", "1", "6", "11"] if idx == 1 else ["0", "36", "149"]
    )
    coordinator = XiaomiMiWiFiCoordinator(hass, client, 30)
    await coordinator.async_load_channels()
    assert coordinator.channels_24g == ["0", "1", "6", "11"]
    assert coordinator.channels_5g == ["0", "36", "149"]


async def test_coordinator_load_channels_swallows_error(hass: HomeAssistant):
    from xiaomi_miwifi import MiWiFiError

    client = AsyncMock()
    client.async_get_available_channels.side_effect = MiWiFiError("x")
    coordinator = XiaomiMiWiFiCoordinator(hass, client, 30)
    await coordinator.async_load_channels()
    assert coordinator.channels_24g == []
    assert coordinator.channels_5g == []


async def test_coordinator_offline_is_not_fatal(hass: HomeAssistant):
    from xiaomi_miwifi import MiWiFiConnectionError

    client = AsyncMock()
    client.async_get_status.side_effect = MiWiFiConnectionError("down")
    coordinator = XiaomiMiWiFiCoordinator(hass, client, 30)
    await coordinator.async_refresh()
    assert coordinator.data.online is False
