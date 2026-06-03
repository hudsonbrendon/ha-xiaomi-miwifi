from homeassistant.helpers import issue_registry as ir

from custom_components.ha_miwifi.repairs import async_check_issues
from tests.conftest import make_status


async def test_firmware_update_issue_created(hass):
    status = make_status(True)
    status.update_available = True
    async_check_issues(hass, "e1", status)
    reg = ir.async_get(hass)
    assert reg.async_get_issue("ha_miwifi", "firmware_update_available_e1")


async def test_firmware_update_issue_deleted_when_no_update(hass):
    status = make_status(True)
    status.update_available = False
    async_check_issues(hass, "e1", status)
    reg = ir.async_get(hass)
    assert reg.async_get_issue("ha_miwifi", "firmware_update_available_e1") is None


async def test_unsupported_router_issue_created(hass):
    status = make_status(True)
    status.hardware = "ZZ9999"
    async_check_issues(hass, "e1", status)
    reg = ir.async_get(hass)
    assert reg.async_get_issue("ha_miwifi", "unsupported_router_e1")


async def test_supported_router_no_issue(hass):
    status = make_status(True)
    status.hardware = "RM1800"
    async_check_issues(hass, "e1", status)
    reg = ir.async_get(hass)
    assert reg.async_get_issue("ha_miwifi", "unsupported_router_e1") is None


async def test_none_status_is_a_noop(hass):
    """Regression: on the first refresh the coordinator data is None;
    async_check_issues must not raise (it used to crash with AttributeError,
    which perpetually failed every coordinator update)."""
    async_check_issues(hass, "e1", None)  # must not raise
