from unittest.mock import patch

from homeassistant.const import CONF_HOST
from homeassistant.helpers import device_registry as dr

from custom_components.xiaomi_miwifi.const import DOMAIN
from custom_components.xiaomi_miwifi.discovery import async_correlate_and_discover
from tests.conftest import make_status


def _make_device(hass, entry_id, name):
    reg = dr.async_get(hass)
    return reg.async_get_or_create(
        config_entry_id=entry_id, identifiers={(DOMAIN, entry_id)}, name=name
    )


async def test_correlation_links_configured_leaf(hass):
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    gw = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "192.168.31.1"},
        unique_id="28:d1:27:9f:4c:14",
    )
    leaf = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "192.168.31.215"},
        unique_id="8c:de:f9:93:c5:4c",
    )
    gw.add_to_hass(hass)
    leaf.add_to_hass(hass)
    gw_dev = _make_device(hass, gw.entry_id, "Gateway")
    leaf_dev = _make_device(hass, leaf.entry_id, "Leaf")

    status = make_status(True)  # mode 0, mesh_nodes incl. 192.168.31.215
    flows = []
    with patch(
        "custom_components.xiaomi_miwifi.discovery.discovery_flow.async_create_flow",
        side_effect=lambda *a, **k: flows.append(k.get("data")),
    ):
        async_correlate_and_discover(hass, gw, status)

    reg = dr.async_get(hass)
    assert reg.async_get(leaf_dev.id).via_device_id == gw_dev.id
    # .215 is configured -> not discovered; .156 is not -> discovered
    assert any(d[CONF_HOST] == "192.168.31.156" for d in flows)
    assert not any(d[CONF_HOST] == "192.168.31.215" for d in flows)


async def test_correlation_noop_for_leaf_status(hass):
    from dataclasses import replace

    from pytest_homeassistant_custom_component.common import MockConfigEntry

    leaf = MockConfigEntry(domain=DOMAIN, data={CONF_HOST: "192.168.31.215"})
    leaf.add_to_hass(hass)
    status = replace(make_status(True), mode=3)  # not a gateway
    flows = []
    with patch(
        "custom_components.xiaomi_miwifi.discovery.discovery_flow.async_create_flow",
        side_effect=lambda *a, **k: flows.append(1),
    ):
        async_correlate_and_discover(hass, leaf, status)
    assert flows == []
