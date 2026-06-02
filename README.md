# Xiaomi MiWiFi for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Tests](https://github.com/hudsonbrendon/ha-xiaomi-miwifi/actions/workflows/tests.yml/badge.svg)](https://github.com/hudsonbrendon/ha-xiaomi-miwifi/actions/workflows/tests.yml)
[![Validate](https://github.com/hudsonbrendon/ha-xiaomi-miwifi/actions/workflows/validate.yml/badge.svg)](https://github.com/hudsonbrendon/ha-xiaomi-miwifi/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Monitor and control **Xiaomi / MiWiFi routers** in Home Assistant over the local LuCI HTTP API. Mesh-aware: the gateway is the hub and each leaf node appears as a child device. Powered by [`python-xiaomi-miwifi`](https://github.com/hudsonbrendon/python-xiaomi-miwifi).

## Features

- 📊 Sensors: connected devices, per-band client counts, download/upload speed, WAN IP, WAN connected-since, WAN total download/upload, WAN max speeds, WAN type, WAN gateway, 2.4/5 GHz channel, firmware, mesh node count, operating mode, Ethernet ports connected
- 🔌 Binary sensors: WAN link, status LED
- 🆕 Firmware update entity (install/latest/changelog)
- 📡 Device tracker: presence for every device seen on the network, with per-client signal, band and traffic attributes
- 🕸️ One child device per mesh leaf node (model + online + IP)
- 🎚️ Selects: 2.4/5 GHz Wi-Fi channel and signal strength (transmit power)
- 🛠️ Controls: 2.4/5 GHz radio switches, QoS switch, reboot button
- 🌍 Country-code diagnostic sensor and a full ~45-model supported-router table (incl. RC06 and RD03)
- ⚙️ Services: `add_dhcp_reservation`, `remove_dhcp_reservation`, `block_device`, `unblock_device`, `luci_request`
- 🌐 English + Portuguese (pt-BR) translations
- 🎨 Native brand icons (no home-assistant/brands PR required)

## Installation (HACS)

1. HACS → ⋮ → **Custom repositories** → add `https://github.com/hudsonbrendon/ha-xiaomi-miwifi`, category **Integration**.
2. Install **Xiaomi MiWiFi**, restart Home Assistant.
3. **Settings → Devices & Services → Add Integration → Xiaomi MiWiFi**.
4. Enter the router host (e.g. `192.168.31.1`) and admin password.

## Entities

| Entity | Platform | Notes |
|--------|----------|-------|
| Connected devices | sensor | total LAN clients |
| 2.4 GHz / 5 GHz clients | sensor | per-band counts |
| Download / Upload speed | sensor | aggregate B/s |
| WAN IP | sensor | public IP |
| WAN connected since | sensor | timestamp, diagnostic |
| WAN download / upload total | sensor | cumulative bytes |
| WAN max download / upload speed | sensor | peak B/s |
| WAN type | sensor | e.g. `dhcp`, diagnostic |
| WAN gateway | sensor | diagnostic |
| 2.4 GHz / 5 GHz channel | sensor | diagnostic |
| Firmware version | sensor | diagnostic |
| Operating mode | sensor | router/repeater/AP/mesh, diagnostic |
| Ethernet ports connected | sensor | count of linked LAN ports, diagnostic |
| Country code | sensor | regulatory region, diagnostic |
| Mesh nodes | sensor | leaf count |
| Firmware | update | install/latest/changelog |
| Presence | device_tracker | one per device seen; tracks all seen devices; exposes `signal`, `band`, `download_speed`, `upload_speed`, `download_total`, `upload_total` attributes |
| WAN link | binary_sensor | connectivity |
| Status LED | binary_sensor | LED state |
| Mesh node online | binary_sensor | per leaf node connectivity |
| Mesh node IP | sensor | per leaf node, diagnostic |
| 2.4 GHz / 5 GHz channel | select | ⚠️ disruptive (restarts the radio) |
| 2.4 GHz / 5 GHz signal strength | select | max/mid/min, ⚠️ disruptive |
| 2.4 GHz / 5 GHz Wi-Fi | switch | ⚠️ disruptive |
| QoS | switch | smart bandwidth limiting |
| Reboot | button | ⚠️ disruptive |

## Services

- `xiaomi_miwifi.add_dhcp_reservation` — reserve an IP for a MAC.
- `xiaomi_miwifi.remove_dhcp_reservation` — remove a reservation.
- `xiaomi_miwifi.block_device` — block a device from the network by MAC.
- `xiaomi_miwifi.unblock_device` — unblock a previously blocked device by MAC.
- `xiaomi_miwifi.luci_request` — perform a read-only GET to any MiWiFi LuCI API path and return the JSON response (e.g. `api/misystem/router_info`).

## Supported routers

| Hardware | Model |
|----------|-------|
| RM1800 | Xiaomi Router AX1800 |
| RA82 | Xiaomi Router AX3000T |

> Open an issue to add yours.

## Development

```bash
uv venv && uv pip install -r requirements_test.txt
pytest && ruff check .
```

## License

MIT © Hudson Brendon
