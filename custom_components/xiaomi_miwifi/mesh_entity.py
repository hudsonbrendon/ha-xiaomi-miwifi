"""Base entity for Xiaomi MiWiFi mesh leaf nodes (child devices)."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from xiaomi_miwifi import MeshNode

from .const import DOMAIN, MANUFACTURER
from .coordinator import XiaomiMiWiFiCoordinator


class XiaomiMeshNodeEntity(CoordinatorEntity[XiaomiMiWiFiCoordinator]):
    """Common device info for a single mesh leaf node."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: XiaomiMiWiFiCoordinator,
        entry: ConfigEntry,
        node: MeshNode,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._node_ip = node.ip
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_{node.ip}")},
            name=node.name,
            manufacturer=MANUFACTURER,
            model=node.model,
            via_device=(DOMAIN, entry.entry_id),
            configuration_url=f"http://{node.ip}",
        )

    def _current_node(self) -> MeshNode | None:
        for node in self.coordinator.data.mesh_nodes:
            if node.ip == self._node_ip:
                return node
        return None
