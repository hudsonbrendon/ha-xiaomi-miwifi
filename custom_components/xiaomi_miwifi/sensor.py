"""Sensor platform for the Xiaomi MiWiFi integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfDataRate, UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from xiaomi_miwifi import MiWiFiStatus

from .const import DOMAIN
from .coordinator import XiaomiMiWiFiCoordinator
from .entity import XiaomiMiWiFiEntity
from .mesh_entity import XiaomiMeshNodeEntity


@dataclass(frozen=True, kw_only=True)
class MiWiFiSensorDescription(SensorEntityDescription):
    """Sensor description with a value extractor."""

    value_fn: Callable[[MiWiFiStatus], object]


SENSOR_DESCRIPTIONS: tuple[MiWiFiSensorDescription, ...] = (
    MiWiFiSensorDescription(
        key="client_count",
        translation_key="client_count",
        icon="mdi:devices",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.client_count,
    ),
    MiWiFiSensorDescription(
        key="clients_24g",
        translation_key="clients_24g",
        icon="mdi:wifi",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.clients_24g,
    ),
    MiWiFiSensorDescription(
        key="clients_5g",
        translation_key="clients_5g",
        icon="mdi:wifi",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.clients_5g,
    ),
    MiWiFiSensorDescription(
        key="mesh_node_count",
        translation_key="mesh_node_count",
        icon="mdi:access-point-network",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.mesh_node_count,
    ),
    MiWiFiSensorDescription(
        key="download_speed",
        translation_key="download_speed",
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:download",
        value_fn=lambda s: s.download_speed,
    ),
    MiWiFiSensorDescription(
        key="upload_speed",
        translation_key="upload_speed",
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:upload",
        value_fn=lambda s: s.upload_speed,
    ),
    MiWiFiSensorDescription(
        key="wan_ip",
        translation_key="wan_ip",
        icon="mdi:ip-network",
        value_fn=lambda s: s.wan_ip,
    ),
    MiWiFiSensorDescription(
        key="wan_download_total",
        translation_key="wan_download_total",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:download-network",
        value_fn=lambda s: s.wan_download_total,
    ),
    MiWiFiSensorDescription(
        key="wan_upload_total",
        translation_key="wan_upload_total",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:upload-network",
        value_fn=lambda s: s.wan_upload_total,
    ),
    MiWiFiSensorDescription(
        key="wan_max_download",
        translation_key="wan_max_download",
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        icon="mdi:download",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.wan_max_download,
    ),
    MiWiFiSensorDescription(
        key="wan_max_upload",
        translation_key="wan_max_upload",
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        icon="mdi:upload",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.wan_max_upload,
    ),
    MiWiFiSensorDescription(
        key="wan_type",
        translation_key="wan_type",
        icon="mdi:wan",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.wan_type,
    ),
    MiWiFiSensorDescription(
        key="wan_gateway",
        translation_key="wan_gateway",
        icon="mdi:router-network",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.wan_gateway,
    ),
    MiWiFiSensorDescription(
        key="channel_24g",
        translation_key="channel_24g",
        icon="mdi:wifi",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.channel_24g,
    ),
    MiWiFiSensorDescription(
        key="channel_5g",
        translation_key="channel_5g",
        icon="mdi:wifi",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.channel_5g,
    ),
    MiWiFiSensorDescription(
        key="firmware_version",
        translation_key="firmware_version",
        icon="mdi:chip",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.firmware_version,
    ),
    MiWiFiSensorDescription(
        key="mode",
        translation_key="mode",
        icon="mdi:router-wireless-settings",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.mode_name,
    ),
    MiWiFiSensorDescription(
        key="ethernet_ports",
        translation_key="ethernet_ports",
        icon="mdi:ethernet",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda s: s.lan_ports_active,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: XiaomiMiWiFiCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = [
        MiWiFiSensor(coordinator, entry, desc) for desc in SENSOR_DESCRIPTIONS
    ]
    entities.append(MiWiFiUptimeSensor(coordinator, entry))
    for node in coordinator.data.mesh_nodes:
        entities.append(MiWiFiMeshNodeStatusSensor(coordinator, entry, node))
        entities.append(MiWiFiMeshNodeIpSensor(coordinator, entry, node))
    async_add_entities(entities)


class MiWiFiSensor(XiaomiMiWiFiEntity, SensorEntity):
    """A single MiWiFi gateway sensor."""

    entity_description: MiWiFiSensorDescription

    def __init__(
        self,
        coordinator: XiaomiMiWiFiCoordinator,
        entry: ConfigEntry,
        description: MiWiFiSensorDescription,
    ) -> None:
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> object:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data.online


class MiWiFiUptimeSensor(XiaomiMiWiFiEntity, SensorEntity):
    """Reports the WAN last-boot timestamp (now - wan_uptime)."""

    _attr_translation_key = "wan_uptime"
    _attr_icon = "mdi:timer-outline"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: XiaomiMiWiFiCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_wan_uptime"

    @property
    def native_value(self) -> datetime | None:
        uptime = self.coordinator.data.wan_uptime
        if not uptime:
            return None
        raw = dt_util.utcnow() - timedelta(seconds=uptime)
        return raw.replace(second=0, microsecond=0)

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data.online


class MiWiFiMeshNodeIpSensor(XiaomiMeshNodeEntity, SensorEntity):
    """Reports the IP address of a mesh leaf node."""

    _attr_translation_key = "mesh_node_ip"
    _attr_icon = "mdi:ip-network"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry, node) -> None:
        super().__init__(coordinator, entry, node)
        self._attr_unique_id = f"{entry.entry_id}_node_{node.ip}_ip"

    @property
    def native_value(self) -> str | None:
        node = self._current_node()
        return node.ip if node else None

    @property
    def available(self) -> bool:
        return super().available and self._current_node() is not None


class MiWiFiMeshNodeStatusSensor(XiaomiMeshNodeEntity, SensorEntity):
    """Reports the model name of a mesh leaf node (presence = available)."""

    _attr_translation_key = "mesh_node_model"
    _attr_icon = "mdi:router-network"

    def __init__(self, coordinator, entry, node) -> None:
        super().__init__(coordinator, entry, node)
        self._attr_unique_id = f"{entry.entry_id}_node_{node.ip}_model"

    @property
    def native_value(self) -> str | None:
        node = self._current_node()
        return node.model if node else None

    @property
    def available(self) -> bool:
        return super().available and self._current_node() is not None
