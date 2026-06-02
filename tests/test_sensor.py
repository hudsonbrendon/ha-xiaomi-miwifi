from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.xiaomi_miwifi.binary_sensor import (
    BINARY_SENSOR_DESCRIPTIONS,
)
from custom_components.xiaomi_miwifi.button import MiWiFiRebootButton
from custom_components.xiaomi_miwifi.sensor import (
    SENSOR_DESCRIPTIONS,
    MiWiFiMeshNodeStatusSensor,
)
from custom_components.xiaomi_miwifi.switch import (
    RADIO_SWITCHES,
    MiWiFiRadioSwitch,
)
from tests.conftest import make_status


def test_sensor_descriptions_cover_expected_keys():
    keys = {d.key for d in SENSOR_DESCRIPTIONS}
    assert keys == {
        "client_count",
        "clients_24g",
        "clients_5g",
        "mesh_node_count",
        "download_speed",
        "upload_speed",
        "wan_ip",
        "wan_uptime",
        "firmware_version",
    }


def test_sensor_value_fns_read_status():
    status = make_status(True)
    by_key = {d.key: d for d in SENSOR_DESCRIPTIONS}
    assert by_key["client_count"].value_fn(status) == 90
    assert by_key["download_speed"].value_fn(status) == 225
    assert by_key["wan_ip"].value_fn(status) == "100.107.54.94"
    assert by_key["mesh_node_count"].value_fn(status) == 2


def test_binary_sensor_descriptions():
    by_key = {d.key: d for d in BINARY_SENSOR_DESCRIPTIONS}
    assert set(by_key) == {"wan_link", "update_available"}
    status = make_status(True)
    assert by_key["wan_link"].value_fn(status) is True
    assert by_key["update_available"].value_fn(status) is False


def test_radio_switch_catalog():
    by_key = {s["key"]: s for s in RADIO_SWITCHES}
    assert set(by_key) == {"wifi_5g", "wifi_24g"}
    assert by_key["wifi_5g"]["ifname"] == "wl0"
    assert by_key["wifi_24g"]["ifname"] == "wl1"


async def test_reboot_button_calls_client(hass):
    coordinator = SimpleNamespace(
        client=AsyncMock(), data=make_status(True),
        async_request_refresh=AsyncMock(),
        last_update_success=True,
    )
    coordinator.client.async_reboot.return_value = True
    entry = SimpleNamespace(entry_id="e1", title="Casa")
    button = MiWiFiRebootButton(coordinator, entry)
    await button.async_press()
    coordinator.client.async_reboot.assert_awaited_once()


async def test_reboot_button_raises_on_failure(hass):
    coordinator = SimpleNamespace(
        client=AsyncMock(), data=make_status(True),
        async_request_refresh=AsyncMock(),
        last_update_success=True,
    )
    coordinator.client.async_reboot = AsyncMock(return_value=False)
    entry = SimpleNamespace(entry_id="e1", title="Casa")
    button = MiWiFiRebootButton(coordinator, entry)
    with pytest.raises(HomeAssistantError):
        await button.async_press()


async def test_radio_switch_turn_off_raises_on_failure(hass):
    coordinator = SimpleNamespace(
        client=AsyncMock(), data=make_status(True),
        async_request_refresh=AsyncMock(),
        last_update_success=True,
    )
    coordinator.client.async_set_wifi_enabled = AsyncMock(return_value=False)
    entry = SimpleNamespace(entry_id="e1", title="Casa")
    switch = MiWiFiRadioSwitch(coordinator, entry, RADIO_SWITCHES[0])
    assert switch._attr_is_on is True
    with pytest.raises(HomeAssistantError):
        await switch.async_turn_off()
    assert switch._attr_is_on is True


async def test_mesh_node_sensor_reports_online_and_model(hass):
    status = make_status(True)
    coordinator = SimpleNamespace(data=status, last_update_success=True)
    entry = SimpleNamespace(entry_id="e1", title="Casa")
    node = status.mesh_nodes[1]  # RA82 leaf
    sensor = MiWiFiMeshNodeStatusSensor(coordinator, entry, node)
    assert sensor.native_value == "Xiaomi Router AX3000T"
    assert sensor._attr_unique_id == "e1_node_192.168.31.156_model"
