# Xiaomi MiWiFi for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Tests](https://github.com/hudsonbrendon/ha-xiaomi-miwifi/actions/workflows/tests.yml/badge.svg)](https://github.com/hudsonbrendon/ha-xiaomi-miwifi/actions/workflows/tests.yml)
[![Validate](https://github.com/hudsonbrendon/ha-xiaomi-miwifi/actions/workflows/validate.yml/badge.svg)](https://github.com/hudsonbrendon/ha-xiaomi-miwifi/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Monitor and control **Xiaomi / MiWiFi routers** in Home Assistant over the local LuCI HTTP API. Mesh-aware: the gateway is the hub and each leaf node appears as a child device. Powered by [`python-xiaomi-miwifi`](https://github.com/hudsonbrendon/python-xiaomi-miwifi).

## Features

- 📊 Sensors: connected devices, per-band client counts, download/upload speed, WAN IP, WAN uptime, firmware, mesh node count
- 🔌 Binary sensors: WAN link, firmware-update-available
- 🕸️ One child device per mesh leaf node (model + presence)
- 🛠️ Controls: 2.4/5 GHz radio switches, reboot button
- ⚙️ Services: `add_dhcp_reservation`, `remove_dhcp_reservation`
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
| WAN uptime | sensor | diagnostic |
| Firmware version | sensor | diagnostic |
| Mesh nodes | sensor | leaf count |
| WAN link | binary_sensor | connectivity |
| Firmware update available | binary_sensor | update |
| 2.4 GHz / 5 GHz Wi-Fi | switch | ⚠️ disruptive |
| Reboot | button | ⚠️ disruptive |

## Services

- `xiaomi_miwifi.add_dhcp_reservation` — reserve an IP for a MAC.
- `xiaomi_miwifi.remove_dhcp_reservation` — remove a reservation.

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
