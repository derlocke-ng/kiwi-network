# Kiwi Network

Own your infrastructure.

Kiwi Network helps private individuals, SMBs, and public offices run a modern open-source infrastructure with a minimal attack surface:

- Public Internet: **only the WireGuard entry point**
- Private network: everything else (**services live behind the VPN**)

## Components

### kiwi-master

Public entry point: WireGuard + network services.

- wg-easy (WireGuard server)
- gluetun (upstream VPN / double-hop)
- pihole (DNS)
- optional Tor proxy

### kiwi-node

Private services: reachable over VPN and/or locally.

- Nextcloud (AIO)
- Vaultwarden
- Reverse proxy (NGINX)
- Docker services

### kiwi-workstation

Daily driver OS for users/operators.

- Fedora Silverblue / Bluefin DX
- easy onboarding
- safe defaults

## Federation (planned)

Connect multiple Kiwi Networks (e.g. Company A and B) to collaborate securely.
The goal: easier Nextcloud federation and controlled sharing, without exposing internal services publicly.

## Links

- Documentation: https://kiwi-network.eu/docs/
- GitHub: https://github.com/derlocke-ng/kiwi-network
