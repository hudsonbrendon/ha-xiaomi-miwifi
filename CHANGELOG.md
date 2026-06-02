# Changelog

All notable changes to this project are documented here.

## [0.4.0]

### Added

- **Wi-Fi channel selects** for the 2.4 GHz and 5 GHz radios, with the available channels (including `auto`) discovered from the router at setup.
- **Wi-Fi signal-strength (transmit power) selects** for the 2.4 GHz and 5 GHz radios (max/mid/min).
- **QoS switch** to enable or disable the router's smart bandwidth limiting.
- **Country code** diagnostic sensor.
- Expanded the recognized-router support table to the full ~45-model reference set, including the Redmi Router AX6000 (RC06) and Xiaomi Router AX3000T NE (RD03).

### Changed

- Bumped the `python-xiaomi-miwifi` requirement to `0.4.0`.

## [0.3.0]

### Added

- **Per-client telemetry on the device tracker**: each presence tracker now exposes `signal`, `band`, `download_speed`, `upload_speed`, `download_total`, and `upload_total` as state attributes.
- **Operating mode** sensor reporting the router operating mode (router/repeater/access point/mesh), diagnostic.
- **Ethernet ports connected** sensor reporting the number of linked LAN ports, diagnostic.
- **Service** `luci_request` — a read-only GET passthrough to any MiWiFi LuCI API path that returns the JSON response.

### Changed

- Bumped the `python-xiaomi-miwifi` requirement to `0.3.0`.

## [0.2.0]

### Added

- **Firmware update entity** exposing installed version, latest available version, and the ROM changelog as the release summary (replaces the old update-available binary sensor).
- **Device tracker** platform: a presence tracker for every device seen on the network (tracks all seen devices, not just currently online ones).
- **New WAN sensors**: total download/upload (cumulative bytes), max download/upload speed (peak B/s), WAN type, and WAN gateway.
- **Wi-Fi channel sensors** for the 2.4 GHz and 5 GHz radios.
- **Status LED** binary sensor reflecting the router LED state.
- **WAN connected-since** sensor reporting the last WAN connection as a timestamp.
- **Per mesh-node entities**: an "Online" connectivity binary sensor and an IP address sensor for each leaf node.
- **Services** `block_device` and `unblock_device` to block/unblock a device from the network by MAC address.

### Changed

- Bumped the `python-xiaomi-miwifi` requirement to `0.2.0`.

## [0.1.0]

- Initial release.
