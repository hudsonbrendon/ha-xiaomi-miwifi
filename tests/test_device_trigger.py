from custom_components.ha_miwifi.device_trigger import (
    TRIGGER_TYPES,
    async_get_triggers,
)


def test_trigger_types():
    assert set(TRIGGER_TYPES) == {
        "device_connected",
        "device_disconnected",
        "new_device",
    }


async def test_async_get_triggers_lists_all_types(hass):
    triggers = await async_get_triggers(hass, "dev123")
    types = {t["type"] for t in triggers}
    assert types == set(TRIGGER_TYPES)
    for t in triggers:
        assert t["domain"] == "ha_miwifi"
        assert t["device_id"] == "dev123"
        assert t["platform"] == "device"
