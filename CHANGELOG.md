# Changelog

All notable changes to this project are documented here.

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
