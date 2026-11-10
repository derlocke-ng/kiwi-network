# The framework's apps

kiwi-framework is the software that lets a community run its own hub, and
this page describes the ten apps that come with it. They include an open
marketplace, a community feed, chat and file sharing.

The framework gives its apps plain names such as `market`. A distribution,
which is one particular hub built with the framework, **mounts** the apps it
wants. To mount an app means to use it for one space, which is a community with
its own moderators and relays, and to give it a name of the hub's own. One app
can be mounted many times. A seed bank and a gem store, for example, are the
same `market` code on two spaces. Each has its own moderators and relays, and
they appear as two tiles on one hub.

| App | What it is | Armory mounts it as |
|---|---|---|
| `market` | **An open marketplace** for the community that a mount serves. A listing has photos, a price, and either the places it ships from and to or an offer of pickup. Buyers find listings by category and by their own location. The search uses labels that relays can match but cannot read. A buyer writes to the seller in the chat, where a message about the listing is already drafted. A listing can be reserved, marked as sold, renewed and reported, and it expires after 30 to 90 days. A mount can require that sellers have first been active in a feed or have been approved by a moderator. | Trading Post |
| `feed` | **A community feed.** People post entries with photos and hashtags, and others can like and comment on them. An entry can be for the whole space, for your friends, for one circle (a group of your friends) or only for you. A diary is a series of entries with a cover. Entries can be marked 18+ or as an ad. | Outpost |
| `chat` | **Messages.** You send private messages and files to friends (NIP-17). Groups exist until their host closes them, and live rooms disappear when the last person has left. The chat has replies, reactions, edits, pins, search on the device and disappearing messages. Voice and video calls work between up to six people. | Uplink |
| `notices` | **A noticeboard** for public notes. Each note is signed by its author and requires proof of work, a small computation that makes mass posting costly. Notes can be voted on and reported, and they expire. | DevBoard |
| `boards` | **Shared lists and notes.** These are checklists, inventories with counts and markdown notes. They are end-to-end encrypted, and you share them with links that allow either editing or only viewing. | Loadout |
| `payload` | **File sharing** in three ways: as a link to files that are stored encrypted on your media servers, as files sent to friends and groups, or directly from one browser to another. | Payload |
| `vault` | **A password manager** for logins, notes, cards and two-factor codes. It has a password generator and a health report. It also manages SSH keys, an SSH CA, an X.509 CA and TLS certificates. It is encrypted with a passphrase of its own. | Vault |
| `authenticator` | **Two-factor codes** (TOTP). They are kept in the same encrypted vault as the password manager's entries. | Authenticator |
| `calendar` | **Your calendars** from Nextcloud or any other CalDAV server. Nothing is sent to relays. | Calendar |
| `pong` | **Two-player Pong** between two browsers. | pongjs |

Every hub also has a start page, an account page and a settings page. The
settings cover your account and devices, friends and circles, blocked people,
relays, spaces, media servers and backups. Notifications are not a separate
app. They are part of the hub itself.

## Spaces and mounts

- A **space** is a community with a name and an owner. It has an id, the
  owner's key, a name, moderators, its own relays and a flag that marks it as
  being for adults. It is modelled on nostr's moderated communities (NIP-72),
  so other nostr clients can read it. Every post and listing belongs to exactly
  one space.
- A **mount** is one app used for one space, with its own id, name and icon.
  To add another community's store to your hub, you add one line that defines
  the mount.
- **A link names the app, the space and the item, but never the host.** A hub
  opens such a link with its own mount of that app and space. If the hub has no
  such mount, it tells you whose space this is and offers a way back.
- **Spaces are federated**, which means that a space is not tied to one hub.
  Two hubs can serve the same space. A space's relays carry only that space's
  content.

Three things are planned and not built yet. Hubs will announce themselves with
a signed manifest so that others can find them. Approvals will be added as a
form of moderation. People will be able to follow a space that their hub does
not include.

## Writing an app

This command creates the skeleton of a new app in your distribution:

```bash
npm run new-app -- <id> "<Name>" <icon>
```

The result is a React app that uses the framework's UI kit. It has a shell
(the frame around the app's pages), a home page and a settings page, its texts
in every language, an entry in the app registry and a mount. Apps use only the
framework's public API and never access storage or keys directly.
[Running your own hub](hubs.md) explains how to build and publish a hub.
