# Xiaomi MiWiFi for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Tests](https://github.com/hudsonbrendon/ha-xiaomi-miwifi/actions/workflows/tests.yml/badge.svg)](https://github.com/hudsonbrendon/ha-xiaomi-miwifi/actions/workflows/tests.yml)
[![Validate](https://github.com/hudsonbrendon/ha-xiaomi-miwifi/actions/workflows/validate.yml/badge.svg)](https://github.com/hudsonbrendon/ha-xiaomi-miwifi/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Monitor and control **Xiaomi / MiWiFi routers** in Home Assistant over the local LuCI HTTP API. Mesh-aware: the gateway is the hub and each leaf node appears as a child device. Powered by [`python-xiaomi-miwifi`](https://github.com/hudsonbrendon/python-xiaomi-miwifi).

## Features

- 📊 Sensors: connected devices, per-band client counts, download/upload speed, WAN IP, WAN connected-since, WAN total download/upload, WAN max speeds, WAN type, WAN gateway, 2.4/5 GHz channel, firmware, mesh node count, operating mode, Ethernet ports connected, speed-test download/upload, WAN DNS, port-forwarding rule count, DHCP lease time, timezone
- 🔌 Binary sensors: WAN link, status LED, DMZ, DDNS, IPv6
- 🆕 Firmware update entity (install/latest/changelog)
- 📡 Device tracker: presence for every device seen on the network, with per-client signal, band and traffic attributes, plus `signal_quality` and `last_seen`
- 🔔 Device events + automation triggers: connected, disconnected, and new-device
- 🩺 System Health panel (router count, reachability, firmware, devices, mesh nodes)
- 🛠️ Repairs: firmware-update-available and unsupported-router issues
- 🔑 Reauthentication and reconfigure flows
- ⚙️ Advanced options: consider-home debounce and MAC exclusion list
- 🕸️ One child device per mesh leaf node (model + online + IP)
- 🎚️ Selects: 2.4/5 GHz Wi-Fi channel and signal strength (transmit power)
- 🛠️ Controls: 2.4/5 GHz radio switches, QoS switch, reboot button, run-speed-test button
- 🌍 Country-code diagnostic sensor and a full ~45-model supported-router table (incl. RC06 and RD03)
- ⚙️ Services: `add_dhcp_reservation`, `remove_dhcp_reservation`, `block_device`, `unblock_device`, `luci_request`, `run_speed_test`, `add_port_forward`, `delete_port_forward`, `set_dmz`, `clear_dmz`, `set_ddns`
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
| Speed test download / upload | sensor | last on-device WAN speed test (Mbit/s) |
| WAN DNS | sensor | WAN-side DNS servers, diagnostic |
| Port forwarding rules | sensor | active single-port forward count, diagnostic |
| DHCP lease time | sensor | minutes, diagnostic |
| Timezone | sensor | router timezone, diagnostic |
| Mesh nodes | sensor | leaf count |
| Firmware | update | install/latest/changelog |
| Presence | device_tracker | one per device seen; tracks all seen devices; exposes `signal`, `band`, `download_speed`, `upload_speed`, `download_total`, `upload_total`, `signal_quality`, `last_seen` attributes; honours the consider-home debounce |
| WAN link | binary_sensor | connectivity |
| Status LED | binary_sensor | LED state |
| DMZ | binary_sensor | DMZ enabled, diagnostic |
| DDNS | binary_sensor | DDNS enabled, diagnostic |
| IPv6 | binary_sensor | IPv6 enabled on WAN, diagnostic |
| Mesh node online | binary_sensor | per leaf node connectivity |
| Mesh node IP | sensor | per leaf node, diagnostic |
| 2.4 GHz / 5 GHz channel | select | ⚠️ disruptive (restarts the radio) |
| 2.4 GHz / 5 GHz signal strength | select | max/mid/min, ⚠️ disruptive |
| 2.4 GHz / 5 GHz Wi-Fi | switch | ⚠️ disruptive |
| QoS | switch | smart bandwidth limiting |
| Reboot | button | ⚠️ disruptive |
| Run speed test | button | triggers an on-device WAN speed test |

## Services

- `xiaomi_miwifi.add_dhcp_reservation` — reserve an IP for a MAC.
- `xiaomi_miwifi.remove_dhcp_reservation` — remove a reservation.
- `xiaomi_miwifi.block_device` — block a device from the network by MAC.
- `xiaomi_miwifi.unblock_device` — unblock a previously blocked device by MAC.
- `xiaomi_miwifi.luci_request` — perform a read-only GET to any MiWiFi LuCI API path and return the JSON response (e.g. `api/misystem/router_info`).
- `xiaomi_miwifi.run_speed_test` — trigger an on-device WAN speed test (briefly saturates the link).
- `xiaomi_miwifi.add_port_forward` — add a single-port forwarding rule (ip, name, proto, source_port, dest_port).
- `xiaomi_miwifi.delete_port_forward` — delete a port forwarding rule by its external (source) port.
- `xiaomi_miwifi.set_dmz` — forward all unmatched WAN traffic to a single LAN host.
- `xiaomi_miwifi.clear_dmz` — disable DMZ forwarding.
- `xiaomi_miwifi.set_ddns` — enable or disable dynamic DNS.

## Events & automation triggers

The integration fires bus events as devices come and go, and exposes matching device-automation triggers:

| Event | Trigger | Payload |
|-------|---------|---------|
| `xiaomi_miwifi_device_connected` | A device connected | `mac`, `name`, `ip` |
| `xiaomi_miwifi_device_disconnected` | A device disconnected | `mac` |
| `xiaomi_miwifi_new_device` | A new device joined | `mac`, `name`, `ip` |

## System Health & Repairs

- **System Health** (Settings → System → Repairs → System information) shows router count, reachability, firmware version, connected devices, and mesh nodes.
- **Repairs** raises informational issues when a firmware update is available or when the router model is not in the supported table.

## Reauthentication & reconfigure

- If the router rejects the stored password, Home Assistant starts a **reauthentication** flow to enter the current password.
- The **reconfigure** option (integration ⋮ menu) lets you change the router host and password without removing the entry.

## Options

Open the integration's **Configure** dialog to set:

- **Update interval** (seconds) — polling cadence.
- **Consider-home** (seconds) — how long a device is still reported home after it stops responding.
- **Excluded MACs** — comma-separated MAC addresses to ignore for presence and events.

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
