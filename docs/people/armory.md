# Armory

Armory is the first hub built with kiwi-framework, the software that lets any
community run its own hub. In the framework's terms Armory is a
**distribution**: the framework together with a name, default relays and a
chosen set of apps. Armory includes all ten of the framework's apps and gives
them names of its own. Its marketplace and its feed are set up for hemp
growers. That subject is the choice of this one hub and not of the framework,
and another community would use the same apps for its own subject. You can use
Armory as it is, or copy it as the template for your own hub.

Every tool runs entirely in your browser. The tools synchronise through
relays, which are servers that store your data and pass it on, and you choose
which relays to use. You do not need to sign up, the project runs no server of
its own for Armory, and nothing tracks you. Everything is encrypted before it
leaves your device. You can install Armory as a web app from its landing page.

- **Open it:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/)
- The repository is [derlocke-ng/armory](https://github.com/derlocke-ng/armory),
  and the license is GPL-3.0-or-later.
- Armory is a distribution of [kiwi-framework](index.md) 0.32.1, which it pins
  by commit. Armory itself has no release tags yet.
- It is available in English, German, French, Spanish, Italian, Dutch, Polish
  and Portuguese.

Armory used to be called weaponized.js.

## The tools

| Tool | What it does |
|---|---|
| [**Loadout**](https://derlocke-ng.github.io/armory/loadout/) | Shared grocery and to-do lists, household inventories and markdown notes. They are kept the same on all your devices and for the people you share them with. Everything is end-to-end encrypted, and you share a list with a link that allows either editing or only viewing. Loadout works offline, and your devices send back to the relays whatever the relays have lost. |
| [**Uplink**](https://derlocke-ng.github.io/armory/uplink/) | Messages and files to friends (NIP-17, encrypted on your device). Groups exist until their host closes them. Live rooms can be joined by anyone who has the link, and they disappear when the last person has left. Uplink has replies, reactions, edits, pins, search on your device and disappearing messages. Voice and video calls work between up to six people. |
| [**Payload**](https://derlocke-ng.github.io/armory/payload/) | File sharing in three ways. You can create a link to files that stay encrypted on your media servers until you delete them. You can send files to friends and groups in Uplink. Or you can send files directly from your browser to another person's browser, and then they are stored nowhere. |
| [**Vault**](https://derlocke-ng.github.io/armory/vault/) | A password manager for logins, notes, cards and two-factor codes, available on every device where you sign in. It has a password generator and a health report. The report finds weak, reused and old passwords and, if you turn that check on, breached passwords. Vault imports and exports entries. It also manages SSH keys, an SSH certificate authority, an X.509 CA and TLS certificates. It is encrypted with a passphrase of its own. It does not fill in passwords on websites for you. |
| [**Authenticator**](https://derlocke-ng.github.io/armory/authenticator/) | Two-factor (TOTP) codes for your accounts on other services. You add an account from a QR code, from a link or secret, or from a Google Authenticator export. The codes are kept in the same encrypted vault that Vault uses. |
| [**Calendar**](https://derlocke-ng.github.io/armory/calendar/) | Your calendars from your own Nextcloud or any other CalDAV server. It shows the coming days or a month, handles repeating events and reminds you of events while a page is open. Nothing is sent to relays, and the login for your server is stored encrypted in your account. Your server must allow requests from Armory's origin (CORS). |
| [**Outpost**](https://derlocke-ng.github.io/armory/outpost/) | Armory's feed, used for grow reports and grow diaries. You post entries with photos, week by week. Each entry can be for everyone in Outpost, for your friends, for one circle of friends or only for you. Entries can have hashtags, likes and comments. Entries are encrypted on your device, and so are the photos. |
| [**Trading Post**](https://derlocke-ng.github.io/armory/tradingpost/) | Armory's marketplace, used for hemp: seeds, cuttings and gear. Listings have photos, and buyers find them by category and by where they ship. Choosing "Message seller" opens Uplink. You need an account to use Trading Post, and there is no age check. Before someone can sell, they must have posted in Outpost (three posts, each liked by three people) or have been approved by a moderator. |
| [**DevBoard**](https://derlocke-ng.github.io/armory/devboard/) | A noticeboard for freelancers. You post a note that says you are hiring or that you are available. Each note is signed with your key and requires proof of work, a small computation that makes mass posting costly. Others can vote on a note. A note disappears when it expires, which is 24 hours to 30 days after it was posted. All notes are public by design. |
| [**pongjs**](https://derlocke-ng.github.io/armory/pongjs/) | Retro Pong for two players in two browsers. To start a game, share a link or a QR code, or pick one of the open games. You can also practise against the computer offline. |

A blog is planned.

Each tool is one of the framework's apps under a name that Armory gave it.
Loadout is the framework's `boards` app, Uplink is `chat`, Outpost is `feed`,
Trading Post is `market`, DevBoard is `notices` and pongjs is `pong`.

## One account, every tool

You sign in or create an account on the landing page, either with a username
and password or with a nostr key. Every tool then uses that account. Lists
that you made on a device before you signed in are carried over into the
account. If you do not use an account, each device works with its own key.

The settings page applies to the whole hub. It covers your account and devices,
friends and circles, blocked people, relays, spaces and media servers,
notifications, and encrypted backups.

## Relays and media servers

Armory's default relays are `wss://nos.lol`, `wss://relay.damus.io`,
`wss://nostr.mom` and `wss://relay.primal.net`. Media servers store the files
you upload, and they use a protocol called Blossom. Armory's default media
servers are `nostr.download`, `blossom.yakihonne.com`, `blossom.band` (which
accepts photos only) and `blossom.primal.net`. You can choose your own relays
and media servers in the settings.

Relays store data and pass it on, but they cannot read anything that was
encrypted before it was sent. The [privacy model](index.md#privacy-model) lists
what relays can see.

## Moderation

Armory's moderators are responsible for Outpost, Trading Post and DevBoard. An
Outpost entry can be marked as 18+ or as an ad. The author can set the mark, a
moderator can set it, and two reports also set it. Marked entries are shown
only to people who have an account.

## Your own Armory

Armory is also the template for your own hub. Fork the repository or use it as
a template, change `distribution.js` and the translations, and publish the
result. [Running your own hub](hubs.md) describes the steps.
