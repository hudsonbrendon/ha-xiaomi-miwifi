from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.xiaomi_miwifi.const import CONF_PASSWORD, DOMAIN


async def test_user_flow_creates_entry(hass: HomeAssistant, aioclient_mock):
    with patch(
        "custom_components.xiaomi_miwifi.config_flow.MiWiFiClient"
    ) as mock_client, patch(
        "custom_components.xiaomi_miwifi.config_flow.async_get_clientsession",
        MagicMock(),
    ), patch(
        "custom_components.xiaomi_miwifi.async_setup_entry",
        AsyncMock(return_value=True),
    ):
        instance = mock_client.return_value
        instance.async_login = AsyncMock(return_value="tok")
        instance.async_close = AsyncMock()
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        assert result["type"] == FlowResultType.FORM
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_NAME: "Casa",
                CONF_HOST: "192.168.31.1",
                CONF_PASSWORD: "foco2021",
            },
        )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"][CONF_HOST] == "192.168.31.1"


async def test_user_flow_handles_auth_error(hass: HomeAssistant, aioclient_mock):
    from xiaomi_miwifi import MiWiFiAuthError

    with patch(
        "custom_components.xiaomi_miwifi.config_flow.MiWiFiClient"
    ) as mock_client, patch(
        "custom_components.xiaomi_miwifi.config_flow.async_get_clientsession",
        MagicMock(),
    ):
        instance = mock_client.return_value
        instance.async_login = AsyncMock(side_effect=MiWiFiAuthError("bad"))
        instance.async_close = AsyncMock()
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_NAME: "Casa",
                CONF_HOST: "192.168.31.1",
                CONF_PASSWORD: "wrong",
            },
        )
    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "invalid_auth"}


async def test_options_flow_accepts_consider_home_and_excluded_macs(hass):
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from custom_components.xiaomi_miwifi.const import (
        CONF_CONSIDER_HOME,
        CONF_EXCLUDED_MACS,
        CONF_SCAN_INTERVAL,
    )

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_NAME: "Casa", CONF_HOST: "192.168.31.1", CONF_PASSWORD: "p"},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_SCAN_INTERVAL: 30,
            CONF_CONSIDER_HOME: 300,
            CONF_EXCLUDED_MACS: "AA:BB:CC:DD:EE:FF",
        },
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"][CONF_CONSIDER_HOME] == 300
    assert result2["data"][CONF_EXCLUDED_MACS] == "AA:BB:CC:DD:EE:FF"
