# Hubs, not platforms

The network connects your machines. **Hubs** connect people. A hub is a set of
web apps (an open marketplace, a feed, chat, file sharing, shared lists, a
password manager, a calendar) that run entirely in the browser and sync over
[nostr](https://nostr.com) relays the community chooses. There is no account
server and no backend in the middle, and everything private is encrypted on the
device before it leaves. Anyone can run a hub for any community. See
[the framework's apps](apps.md).

Three repositories make this up:

| Repository | What it is |
|---|---|
| [**kiwi-framework**](https://github.com/derlocke-ng/kiwi-framework) | The engine: identity and accounts, relays and sync, people and sharing, moderation, the design kit, the hub pages and ten apps. It ships nothing a user opens by itself. v0.32.1, GPL-3.0-or-later |
| [**Armory**](armory.md) | The first **distribution**: a hub built with the framework, with a name, default relays and all ten apps mounted under its own names. The template to fork for your own. GPL-3.0-or-later. **Live:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) |
| [**kiwi-web-catalog**](hubs.md#kiwi-web-catalog) | A git catalog of hubs and their apps, the same shape as the desktop [kiwi-catalog](../desktop/catalogs.md) |

## How it fits together

```
kiwi-framework  (engine: shared data layer, React UI, hub pages, apps)
      │  pinned by commit or tag
      ▼
a distribution  (Armory: distribution.js + locales/ + app overlays)
      │  build → static files
      ▼
any static host (GitHub Pages)  or  the hub container (nginx + HUB_* settings)
      │  HTTPS
      ▼
┌──────────────── your browser: all the logic and all the crypto ────────────────┐
│  wss://   nostr relays: the hub's own, a public area, one network per space    │
│  https:// Blossom media servers: encrypted files, addressed by their SHA-256   │
│  WebRTC   browser to browser: direct file transfers, calls, pong               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## The words

- **Hub**: what a distribution produces. Static files, so hosting one is
  serving a folder. Every hub has a start page, settings and an account page.
- **Distribution**: a hub built on the framework, with a name and look,
  default relays, and a chosen set of apps on chosen spaces. Everything a fork
  changes lives in one file, `distribution.js`, plus its translations.
- **App**: a folder with a manifest that plugs into any distribution. Apps only
  talk to the framework's public API and never touch storage or keys directly.
- **Space**: a named, owned community with its own moderators and, optionally,
  its own relays (modelled on NIP-72 moderated communities). Another hub can
  serve the same space by naming its address.
- **Mount**: app code on a space, with its own name, route and icon. One app can
  be mounted many times. Armory's *Trading Post* is the framework's `market` app
  mounted on Armory's `tradingpost` space.

Two people on different distributions are friends, share and chat exactly as
on one, because identity and data are nostr events, not the hub's.

## Accounts and keys

- Every device gets a key on its first visit, kept in the browser.
- An **account** is a username and password, built on plain nostr events
  without any registry: the password is stretched with scrypt and unlocks your
  key. Nobody can take or overwrite an account without the password. There is
  **no password reset**.
- You can also sign in with an existing nostr key (`nsec`, hex or `ncryptsec`).
  Browser-extension and remote signers (NIP-07, NIP-46) are planned, not built.
- One account works across all the hub's apps and every device you sign in on.

## Privacy model

**What is encrypted.** Content is sealed in the browser before it goes
anywhere: AES-256-GCM with keys derived by HKDF. Private messages are NIP-17
messages in NIP-59 gift wraps. Files get a random AES-256-GCM key each before
they go to a media server, and photos are re-encoded, which drops camera
metadata. The Vault is sealed with its own passphrase (scrypt + AES-256-GCM).
Calls go browser to browser, encrypted by WebRTC.

**Local first.** Every write goes to the browser's own database first, then to
the relays. Reads come from the device, so the apps work offline. When a device
reconnects it puts back what a relay forgot: data is only lost if every device
that held it is gone *and* there is no backup.

**What others can see.** The repositories are explicit about the limits:

- Relays see metadata: who writes to which addresses, when, how much, and from
  which IP address. Use a VPN or Tor if that matters.
- A space's key is not a secret. It keeps a community's posts off plain view.
  Likes, reports and who commented on what are visible to relays.
- DevBoard notes and moderation reports are public by design.
- Your key lives in the browser's storage. All GitHub Pages sites of one account
  share an origin, so a hub on its own (sub)domain is the stronger setup.
- Direct transfers and calls reveal the two browsers' IP addresses to each other
  and to the STUN servers (Google's and Cloudflare's by default; a hub can set
  its own).
- "No server of ours" means none in the critical path. The apps still use the
  relays, media servers and, for the calendar, the CalDAV server that you or
  your hub choose.

## Moderation

Three layers: your own block list (encrypted, only you can read it), reports
(public, signed), and the relays' own policy. A space has moderators. A
moderator's report folds a post at once. Otherwise it takes three reports from
people who are not blocked. Posts can be marked 18+ or as an ad, and
those show to people with an account only.

## Read on

- [Armory and its apps](armory.md)
- [Running your own hub](hubs.md)
- The framework's own [architecture](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/architecture.md)
  and [wire protocol](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/protocol.md)
