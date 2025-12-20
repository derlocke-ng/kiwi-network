# kiwi-master

The master is the public-facing entry point. It should expose **only** what is needed.

## Typical services (example)

- WireGuard server (`wg-easy`)
- VPN client (`gluetun`) for upstream privacy/double-hop
- DNS (`pihole`) for network-wide resolution and filtering
- Optional Tor proxy
- Optional Portainer for management
