# The framework's apps

kiwi-framework ships its apps under plain names. A distribution **mounts**
them, on a space and under a name of its own. One app can be mounted many
times: a seed bank and a gem store are the same `market` code on two spaces,
each with its own moderators and relays, as two tiles on one hub.

| App | What it is | Armory mounts it as |
|---|---|---|
| `market` | **An open marketplace** for the community a mount serves. Listings have photos, a price, where they ship from and to, or pickup. Buyers find them by category and by where they are, through search labels that relays can match but not read. Buyers write to the seller in the chat, with a message about the listing already drafted. Listings can be reserved, sold, renewed and reported, and expire after 30 to 90 days. A mount can ask that sellers have shown up in a feed first, or been approved by a moderator | Trading Post |
| `feed` | **A community feed**: entries with photos, hashtags, likes and comments for the space, for friends, for a circle or only for you, plus diaries (a series of entries with a cover). Entries can be marked 18+ or as an ad | Outpost |
| `chat` | **Messages**: private messages and files to friends (NIP-17), groups that stay until their host closes them, live rooms that vanish when they empty, replies, reactions, edits, pins, search on the device, disappearing messages, and voice and video calls between up to six people | Uplink |
| `notices` | **A noticeboard** of signed, public notes with proof of work, votes, reports and an expiry | DevBoard |
| `boards` | **Shared lists and notes**: checklists, inventories with counts and markdown notes, end-to-end encrypted, with edit or view-only links | Loadout |
| `payload` | **File sharing**: a link that waits, encrypted, on your media servers; files to friends and groups; or straight from browser to browser | Payload |
| `vault` | **A password manager**: logins, notes, cards, two-factor codes, a generator and a health report, SSH keys, an SSH CA, an X.509 CA and TLS certificates. Sealed with its own passphrase | Vault |
| `authenticator` | **Two-factor codes** (TOTP), kept in the same sealed vault | Authenticator |
| `calendar` | **Your calendars** from Nextcloud or any CalDAV server. Nothing goes to relays | Calendar |
| `pong` | **Two-player Pong** between browsers | pongjs |

Every hub also has a start page, settings (your account and devices, friends
and circles, blocked people, relays, spaces, media servers, backups) and an
account page. Notifications live in the hub itself.

## Spaces and mounts

- A **space** is a named, owned community: an id, an owner key, a name,
  moderators, its own relays and an adult flag. It is modelled on nostr's
  moderated communities (NIP-72), so other nostr clients can read it. Every
  post and listing belongs to exactly one space.
- A **mount** is app code on a space, with its own id, name and icon. Importing
  another community's store is one mount line.
- **Links name the app, the space and the item, never the host.** A hub opens
  a link with its own mount of that app and space. Without one, it says whose
  space this is and offers the way back.
- **Spaces are federated.** Two hubs can serve the same space, and a space's
  relays carry only its content.

Planned: hubs announcing themselves with a signed manifest so others can find
them, moderation approvals, and people following a space their hub does not
ship.

## Writing an app

```bash
npm run new-app -- <id> "<Name>" <icon>
```

This scaffolds a React app on the framework's UI kit, with a shell, home and
settings pages, strings in every language, a registry entry and a mount. Apps
talk to the framework only through its public API and never touch storage or
keys directly. See [Running your own hub](hubs.md).
