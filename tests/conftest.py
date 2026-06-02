import pytest

pytest_plugins = ["pytest_homeassistant_custom_component"]

from xiaomi_miwifi import MeshNode, MiWiFiStatus


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


def make_status(online: bool = True) -> MiWiFiStatus:
    return MiWiFiStatus(
        online=online,
        hardware="RM1800",
        firmware_version="1.0.394",
        serial="SN1",
        mac="28:D1:27:9F:4C:14",
        client_count=90,
        mesh_node_count=2,
        clients_24g=69,
        clients_5g=15,
        wan_ip="100.107.54.94",
        wan_gateway="100.107.32.1",
        wan_type="dhcp",
        wan_uptime=90861,
        wan_link=True,
        upload_speed=150,
        download_speed=225,
        update_available=False,
        wan_download_total=123456789,
        wan_upload_total=987654321,
        wan_max_download=11800000,
        wan_max_upload=2400000,
        led_on=True,
        channel_24g=6,
        channel_5g=149,
        encryption_24g="psk2",
        encryption_5g="psk2",
        txpwr_24g="max",
        txpwr_5g="mid",
        country_code="CN",
        qos_on=True,
        rom_changelog="Bug fixes and stability improvements.",
        rom_latest_version="1.0.400",
        mode=0,
        lan_ports=[False, True, False],
        mesh_nodes=[
            MeshNode("Leaf1", "192.168.31.215", "RM1800", "s", 8),
            MeshNode("Leaf2", "192.168.31.156", "RA82", "s", 8),
        ],
    )
