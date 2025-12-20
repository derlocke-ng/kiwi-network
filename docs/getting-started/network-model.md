# Network Model

Kiwi Network is designed so that internal services are not exposed to the Internet.

## High-level flow

- Public Internet → `kiwi-master` WireGuard UDP port
- VPN tunnel → `kiwi-node` services (Nextcloud, Vaultwarden, etc.)

## Why it matters

This model is well-suited for regulated environments because your attack surface stays small: one hardened entry point, private services behind the tunnel.
