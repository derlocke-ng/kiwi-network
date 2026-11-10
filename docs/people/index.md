# Hubs, not platforms

**kiwi-framework** is software that lets any community run its own
**hub**. A hub is a website with a set of apps for the community's members: an
open marketplace, a feed, chat, file sharing, shared lists, a password manager
and a calendar. Anyone can run a hub for any community, and the community then
does not depend on a central platform that holds everyone's accounts and data.

The apps run entirely in the browser. They synchronise through
[nostr](https://nostr.com) relays, which are servers that store signed messages
and pass them on, and the community chooses which relays its hub uses. There is
no account server and no backend between the browser and the relays, and
everything private is encrypted on the device before it is sent. The other
parts of Kiwi Network connect your machines. Hubs connect people.
[The framework's apps](apps.md) describes each app.

Armory is the first hub that was built with the framework. It is one example,
and it is also the template that other communities copy to build their own hub.

The software is in three repositories:

| Repository | What it is |
|---|---|
| [**kiwi-framework**](https://github.com/derlocke-ng/kiwi-framework) | The general software that every hub is built from. It contains identity and accounts, relays and synchronisation, friends and sharing, moderation, the design kit, the hub's pages and ten apps. You cannot open the framework by itself as a website. A distribution turns it into a hub. The current version is v0.32.1, and the license is GPL-3.0-or-later. |
| [**Armory**](armory.md) | The first **distribution**, which means a hub built with the framework. It adds a name, default relays and all ten apps, each under a name of Armory's own. It is the template to fork for your own hub. The license is GPL-3.0-or-later. **Live:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/) |
| [**kiwi-web-catalog**](hubs.md#kiwi-web-catalog) | A catalog, which is a git repository that lists hubs and their apps. It has the same format as the desktop [kiwi-catalog](../desktop/catalogs.md). |

## How it fits together

The diagram shows how the framework becomes a hub in your browser, and which
servers the browser then talks to.

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

## The terms used here { #the-words }

- **Hub**: the website that a community uses. A hub is what you get when you
  build a distribution. It consists only of static files, so hosting one means
  serving a folder of files. Every hub has a start page, a settings page and an
  account page.
- **Distribution**: the framework together with the choices that make one
  particular hub. These are a name and look, default relays, and a chosen set
  of apps on chosen spaces. When you fork a distribution, everything you change
  is in one file, `distribution.js`, and in its translations.
- **App**: a folder with a manifest file. It can be added to any distribution.
  Apps use only the framework's public API and never access storage or keys
  directly.
- **Space**: a community that has a name, an owner, its own moderators and, if
  it wants them, its own relays. It is modelled on nostr's moderated
  communities (NIP-72). Another hub can serve the same space by naming the
  space's address.
- **Mount**: one app used for one space. Each mount has its own name, its own
  route (its address within the hub) and its own icon. One app can be mounted
  many times. For example, Armory's *Trading Post* is the framework's `market`
  app mounted on Armory's `tradingpost` space.

Two people who use hubs from different distributions can be friends, share
things and chat exactly as if they used the same hub. This works because a
person's identity and data are nostr events, which are signed messages stored
on relays, and they do not belong to a hub.

## Accounts and keys

- The first time you open a hub on a device, the browser creates a key for
  that device and stores it.
- An **account** is a username and a password. It is built on ordinary nostr
  events, and there is no registry of accounts. Your password is stretched with
  scrypt, a function that is deliberately slow to compute, and the result
  unlocks your key. Nobody can take over or overwrite an account without the
  password. There is **no password reset**.
- You can also sign in with a nostr key that you already have, given as `nsec`,
  hex or `ncryptsec`. Signing in through a browser extension (NIP-07) or a
  remote signer (NIP-46) is planned but not built.
- One account works in all of the hub's apps and on every device where you
  sign in.

## Privacy model

**What is encrypted.** The browser encrypts content before it sends it
anywhere. It uses AES-256-GCM with keys derived by HKDF. Private messages are
NIP-17 messages inside NIP-59 gift wraps. A gift wrap is a second layer of
encryption, so that a relay sees only that some key received a wrapped message.
Every file is encrypted with its own random AES-256-GCM key before it is
uploaded to a media server. Photos are re-encoded first, which removes the
metadata that cameras add. The Vault is encrypted with a passphrase of its own
(scrypt + AES-256-GCM). Calls are sent directly from browser to browser and are
encrypted by WebRTC.

**Local first.** Everything you write is saved in the browser's own database
first and is then sent to the relays. The apps read from that database on the
device, so they also work offline. When a device reconnects, it sends the relay
any data that the relay no longer has. Data is therefore only lost if every
device that held it is gone *and* there is no backup.

**What others can see.** The repositories state the limits themselves:

- Relays see metadata. They see who writes to which addresses, when, how much,
  and from which IP address. Use a VPN or Tor if that matters to you.
- A space's key is not a secret. It only keeps a community's posts from being
  openly readable. Relays can see likes, reports and who commented on what.
- DevBoard notes and moderation reports are public by design.
- Your key is kept in the browser's storage. All GitHub Pages sites of one
  account share one origin, and browsers separate the storage of websites by
  origin. A hub on its own domain or subdomain is therefore the stronger setup.
- In a direct file transfer or a call, the two browsers learn each other's IP
  address, and the STUN servers that help them connect see both addresses too.
  By default these are Google's and Cloudflare's STUN servers. A hub can set
  its own.
- "No server of ours" means that the apps do not depend on any server run by
  the project. The apps still use relays, media servers and, for the calendar,
  a CalDAV server. You or your hub choose which ones.

## Moderation

Moderation has three layers. The first is your own block list, which is
encrypted so that only you can read it. The second is reports, which are public
and signed. The third is the policy of each relay.

Every space has moderators. When a moderator reports a post, the post is
collapsed at once. Otherwise a post is collapsed after three reports from
people who are not blocked. A post can be marked as 18+ or as an ad, and marked
posts are shown only to people who have an account.

## Read on

- [Armory and its apps](armory.md)
- [Running your own hub](hubs.md)
- The framework's own [architecture](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/architecture.md)
  and [wire protocol](https://github.com/derlocke-ng/kiwi-framework/blob/main/docs/protocol.md)
