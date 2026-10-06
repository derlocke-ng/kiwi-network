# Roadmap

The Kiwi Network has grown from a set of hand-assembled compose stacks into a
tooling-driven ecosystem. Where things stand:

## Done / shipping

- **Reference architectures as code.** [kiwi-server](build/kiwi-server.md)
  renders the `master`, `node-gw` and `node-cloud` roles from one `fleet.yaml`,
  across CoreOS, uCore and Debian, with unattended install ISOs.
- **App distribution.** [kiwi-updater](apps/kiwi-updater.md) +
  [kiwi-catalog](apps/kiwi-catalog.md): install and update open-source apps from
  git catalogs on ostree desktops, including the updater itself.
- **The workstation app suite.** [kiwi-fox](privacy-apps/kiwi-fox.md) and its
  [provider plugins](privacy-apps/plugins.md),
  [kiwi-killswitch](privacy-apps/kiwi-killswitch.md),
  [kiwi-gen](privacy-apps/kiwi-gen.md),
  [kiwi-pentesting](privacy-apps/kiwi-pentesting.md) and the
  [desktop CLI tools](privacy-apps/cli-tools.md).

## In progress

- **End-to-end first-boot validation** of each kiwi-server target on real
  hardware (the generators are tested; the booted stacks are the live v1 setups
  rendered from modules, verified file by file, not yet booted from the new
  pipeline).
- **Provider plugins to real exits** — the VPN, 9proxy and Mysterium plugins are
  wired and unit-tested against the kiwi-fox contract; bringing each tunnel up
  end-to-end needs the respective account/subscription.

## Planned

- **Federation patterns.** Documented reference setups for linking two fleets
  over controlled VPN links, plus fleet-file settings to express a link. See
  [Federation](federation/index.md).
- **A hosted registry of trusted catalogs** (`kiwi catalog browse`), so catalogs
  can be discovered instead of pasted, while staying opt-in.
- **Signature verification** in kiwi-updater (`signer=<fingerprint>`, checked
  with `git verify-tag` before an installer runs).
- **Deployment guides** for SMB and public-office scenarios.
