# Armory

**Peer-to-peer webtools, armed with nostr.** Every tool runs entirely in your
browser and syncs over relays you choose. There is no sign-up, no server of
ours and no tracking, and everything is encrypted before it leaves your device.
Install it as a web app from the landing page.

- **Open it:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/)
- Repository: [derlocke-ng/armory](https://github.com/derlocke-ng/armory), GPL-3.0-or-later
- A distribution of [kiwi-framework](index.md) 0.32.1 (pinned by commit). There
  are no release tags yet.
- In English, German, French, Spanish, Italian, Dutch, Polish and Portuguese.

Armory used to be called weaponized.js.

## The tools

| Tool | What it does |
|---|---|
| [**Loadout**](https://derlocke-ng.github.io/armory/loadout/) | Shared grocery and to-do lists, household inventories and markdown notes across your devices and with whoever you share them with. End-to-end encrypted, with edit or view-only links. Works offline, and your devices put back what relays forget. |
| [**Uplink**](https://derlocke-ng.github.io/armory/uplink/) | Messages and files to friends (NIP-17, sealed on your device), groups that stay until their host closes them, and live rooms anyone with the link can join, gone when they empty. Replies, reactions, edits, pins, on-device search, disappearing messages, and voice and video calls between up to six people. |
| [**Payload**](https://derlocke-ng.github.io/armory/payload/) | A file share: a link that waits, encrypted, on your media servers until you delete it; files to friends and groups in Uplink; or straight from your browser to theirs, stored nowhere. |
| [**Vault**](https://derlocke-ng.github.io/armory/vault/) | A password manager: logins, notes, cards and two-factor codes on every device you sign in on. A generator, a health report (weak, reused, old and, if you turn it on, breached passwords), imports and exports, SSH keys, an SSH certificate authority, an X.509 CA and TLS certificates. Sealed with its own passphrase. No autofill. |
| [**Authenticator**](https://derlocke-ng.github.io/armory/authenticator/) | Two-factor (TOTP) codes for your accounts elsewhere: add one from a QR code, a link or secret, or a Google Authenticator export. Kept in the same sealed vault. |
| [**Calendar**](https://derlocke-ng.github.io/armory/calendar/) | Your calendars from your own Nextcloud or any CalDAV server: the coming days or a month, repeating events, reminders while a page is open. Nothing goes to relays; the login is sealed in your account. Your server must allow Armory's origin (CORS). |
| [**Outpost**](https://derlocke-ng.github.io/armory/outpost/) | Grow reports and grow diaries: entries with photos, week by week, for everyone in Outpost, your friends, a circle or only you. Hashtags, likes and comments. Sealed on your device, photos encrypted. |
| [**Trading Post**](https://derlocke-ng.github.io/armory/tradingpost/) | A hemp marketplace: seeds, cuttings and gear with photos, found by category and by where they ship. "Message seller" opens Uplink. For people with an account (no age check). Sellers have to show up in Outpost first (three posts, each liked by three people) or be approved by a moderator. |
| [**DevBoard**](https://derlocke-ng.github.io/armory/devboard/) | A freelancer noticeboard: post that you are hiring or available, signed with your key, backed by proof of work, voted on, gone when it expires (24 hours to 30 days). Public by design. |
| [**pongjs**](https://derlocke-ng.github.io/armory/pongjs/) | Retro two-player Pong between two browsers. Share a link or QR code or pick an open game, or practise against the computer offline. |

A blog is planned.

Each tool is one of the framework's apps, mounted under Armory's name: Loadout
is `boards`, Uplink `chat`, Outpost `feed`, Trading Post `market`, DevBoard
`notices`, pongjs `pong`.

## One account, every tool

Sign in or create an account on the landing page (username and password, or a
nostr key) and every tool uses it. Lists you made on a device before signing in
are carried over. Without an account, each device uses its own key.

The settings page covers the whole hub: your account and devices, friends and
circles, blocked people, relays, spaces and media servers, notifications, and
encrypted backups.

## Relays and media servers

Armory's default relays are `wss://nos.lol`, `wss://relay.damus.io`,
`wss://nostr.mom` and `wss://relay.primal.net`. Its default media (Blossom)
servers are `nostr.download`, `blossom.yakihonne.com`, `blossom.band` (photos
only) and `blossom.primal.net`. You can pick your own in the settings.

Relays pass data along, but they cannot read what was encrypted first. The
[privacy model](index.md#privacy-model) lists what they can see.

## Moderation

Armory's moderators moderate Outpost, Trading Post and DevBoard. Outpost entries
can be marked 18+ or as an ad by their writer, by two reports, or by a
moderator. Those entries show to people with an account only.

## Your own Armory

Armory is the template for your own hub. Fork it (or use it as a template),
change `distribution.js` and the translations, and publish it. See
[Running your own hub](hubs.md).
