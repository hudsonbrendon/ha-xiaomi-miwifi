from types import SimpleNamespace

from homeassistant.helpers import issue_registry as ir

from custom_components.xiaomi_miwifi.repairs import async_check_issues
from tests.conftest import make_status


async def test_firmware_update_issue_created(hass):
    status = make_status(True)
    status.update_available = True
    coord = SimpleNamespace(
        data=status, client=SimpleNamespace(host="192.168.31.1")
    )
    async_check_issues(hass, "e1", coord)
    reg = ir.async_get(hass)
    assert reg.async_get_issue("xiaomi_miwifi", "firmware_update_available_e1")


async def test_firmware_update_issue_deleted_when_no_update(hass):
    status = make_status(True)
    status.update_available = False
    coord = SimpleNamespace(
        data=status, client=SimpleNamespace(host="192.168.31.1")
    )
    async_check_issues(hass, "e1", coord)
    reg = ir.async_get(hass)
    assert reg.async_get_issue("xiaomi_miwifi", "firmware_update_available_e1") is None


async def test_unsupported_router_issue_created(hass):
    status = make_status(True)
    status.hardware = "ZZ9999"
    coord = SimpleNamespace(
        data=status, client=SimpleNamespace(host="192.168.31.1")
    )
    async_check_issues(hass, "e1", coord)
    reg = ir.async_get(hass)
    assert reg.async_get_issue("xiaomi_miwifi", "unsupported_router_e1")


async def test_supported_router_no_issue(hass):
    status = make_status(True)
    status.hardware = "RM1800"
    coord = SimpleNamespace(
        data=status, client=SimpleNamespace(host="192.168.31.1")
    )
    async_check_issues(hass, "e1", coord)
    reg = ir.async_get(hass)
    assert reg.async_get_issue("xiaomi_miwifi", "unsupported_router_e1") is None
