from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from custom_components.xiaomi_miwifi import (
    DOMAIN,
    SERVICE_BLOCK_DEVICE,
    SERVICE_UNBLOCK_DEVICE,
    _register_services,
)


def _make_coordinator() -> SimpleNamespace:
    return SimpleNamespace(
        client=AsyncMock(),
        async_request_refresh=AsyncMock(),
    )


async def _call(hass, service: str, mac: str = "AA:BB:CC:DD:EE:FF") -> None:
    await hass.services.async_call(
        DOMAIN,
        service,
        {"entry_id": "e1", "mac": mac},
        blocking=True,
    )


async def test_block_device_calls_client(hass):
    coord = _make_coordinator()
    coord.client.async_block_device.return_value = True
    hass.data[DOMAIN] = {"e1": coord}
    _register_services(hass)

    await _call(hass, SERVICE_BLOCK_DEVICE)

    coord.client.async_block_device.assert_awaited_once_with("AA:BB:CC:DD:EE:FF")
    coord.async_request_refresh.assert_awaited_once()


async def test_block_device_raises_on_false(hass):
    coord = _make_coordinator()
    coord.client.async_block_device.return_value = False
    hass.data[DOMAIN] = {"e1": coord}
    _register_services(hass)

    with pytest.raises(HomeAssistantError):
        await _call(hass, SERVICE_BLOCK_DEVICE)


async def test_unblock_device_calls_client(hass):
    coord = _make_coordinator()
    coord.client.async_unblock_device.return_value = True
    hass.data[DOMAIN] = {"e1": coord}
    _register_services(hass)

    await _call(hass, SERVICE_UNBLOCK_DEVICE)

    coord.client.async_unblock_device.assert_awaited_once_with("AA:BB:CC:DD:EE:FF")
    coord.async_request_refresh.assert_awaited_once()


async def test_unblock_device_raises_on_false(hass):
    coord = _make_coordinator()
    coord.client.async_unblock_device.return_value = False
    hass.data[DOMAIN] = {"e1": coord}
    _register_services(hass)

    with pytest.raises(HomeAssistantError):
        await _call(hass, SERVICE_UNBLOCK_DEVICE)


async def test_block_device_unknown_entry_raises(hass):
    coord = _make_coordinator()
    coord.client.async_block_device.return_value = True
    hass.data[DOMAIN] = {"e1": coord}
    _register_services(hass)

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_BLOCK_DEVICE,
            {"entry_id": "nope", "mac": "AA:BB:CC:DD:EE:FF"},
            blocking=True,
        )
