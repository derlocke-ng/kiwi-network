# kiwi-node

A node is where most user-facing services live. Nodes connect to the master via WireGuard.

## Typical services (example)

- Reverse proxy (e.g. NGINX)
- Nextcloud (AIO)
- Vaultwarden
- Optional Portainer

Nodes should be reachable via VPN and/or LAN, but not publicly exposed by default.
