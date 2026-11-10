# Running your own hub

This page explains how to run a hub for your own community. A hub is the
website that a community gets from kiwi-framework: an open marketplace, a
feed, chat and other apps that run in the browser. A hub consists only of
static files, so hosting one means serving a folder of files over HTTPS. There
are three ways to run one:

- **Use Armory as it is.** Armory is the first hub built with the framework,
  and it is open to everyone at
  [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/).
- **Make your own distribution.** A distribution is the framework with your
  own name, relays and choice of apps. You can publish it on any static host.
- **Run the hub container.** For example, you can run it inside your own Kiwi
  Network together with your own relay. The result is a private hub that can
  only be reached from the mesh, which is the private network that joins your
  machines.

## Kinds of hub

| Kind | How | Example |
|---|---|---|
| **Public** | The hub uses public relays, and anyone can open it. | Armory |
| **Private** | People cannot replace the hub's relays (`policy.relays: 'locked'`), and the pages wait until one of these relays answers (`requireHub`). The relays are inside a VPN. | a company hub on its kiwi-master |
| **Semi-public** | A private hub that also has a public area. Chosen apps, for example the chat, use public relays there. | |

A hub's relays form separate networks: the hub's own network, the public area,
and the networks of its spaces. Every event, which is a signed nostr message,
belongs to one of these networks and is never passed to another.

## Your own distribution

Start from Armory, which is the template. On GitHub, *Use this template* gives
you a copy of the repository without its history. Then follow these steps:

1. Edit **`distribution.js`**. This file sets the id, name, mark, description,
   homepage, repository, relays, media servers, spaces, apps and mounts. If
   your hub should serve Armory's spaces as well, copy their `owner` and `id`
   from Armory's `hub.json`.
2. Edit **`locales/*.json`**. These files hold the title, the lead and the
   footer, and one card text for each mount. English is the fallback language.
3. Update **`kiwi.manifest`**. If you like, also add your hub to
   [kiwi-web-catalog](#kiwi-web-catalog).
4. On GitHub, choose *Settings → Pages → Source: GitHub Actions*, and then
   push.

These are the commands you use while you work on a distribution:

```bash
npm install
npm run dev                  # the hub with hot reload, http://localhost:5173
npm test
npm run build && npm run serve
npm run relay:nostr          # a local test relay on ws://localhost:7777
npm run new-app -- <id> "<Name>" <icon>   # scaffold a new app
```

Pin kiwi-framework to a commit or a tag, never to a branch. The build checks
your `distribution.js`. For example, a hub with a public mount must have public
relays, and a hub with public relays must have a public mount.

Everything you see in the browser is written in TypeScript with React 19 and
built with Vite. The data layer in `shared/` is plain JavaScript with JSDoc
types. Tests run in node's test runner, and the tests that need a browser run
in Playwright.

## The hub container

Armory is also available as a container image, `ghcr.io/derlocke-ng/armory`.
The image is built from the framework's `container/Dockerfile` and serves the
hub with nginx. When the container starts, its entrypoint script writes the
file `hub.local.json` from the `HUB_*` variables, and the page reads this file
before it connects. A deployment can choose relays and policy in this way, but
it cannot add code. If no variables are set, the hub runs as it was built.

This example starts a hub with its own locked relay and with one mount on a
public relay:

```bash
docker run --rm -p 8080:80 \
  -e HUB_RELAYS=wss://relay.sh3.home \
  -e HUB_RELAYS_LOCKED=true -e HUB_REQUIRE_HUB=true \
  -e HUB_PUBLIC_RELAYS=wss://nos.lol -e HUB_PUBLIC_MOUNTS=uplink \
  ghcr.io/you/your-hub
```

| Variable | Meaning |
|---|---|
| `HUB_RELAYS` | The hub's own relays. |
| `HUB_PUBLIC_RELAYS` | The public area's relays. If the variable is set but empty, there is no public area. |
| `HUB_DIRECTORY_RELAYS` | The relays where relay lists are published and looked up. |
| `HUB_RELAYS_LOCKED` | With `true`, people cannot replace the hub's relays. |
| `HUB_REQUIRE_HUB` | With `true`, the pages wait as long as none of the hub's relays answers. |
| `HUB_PUBLIC_MOUNTS` | The mounts that use the public area, listed by id. |
| `HUB_ACCOUNT_MOUNTS` | The mounts that ask for an account. |
| `HUB_REQUIRE_ACCOUNT` | With `true`, every mount asks for an account. |
| `HUB_SPACE_RELAYS` | The relays of each space, written as `jobs=wss://…;gems=wss://a,wss://b`. |
| `HUB_MODERATORS` | The keys of the people who moderate every space that the hub defines. |
| `HUB_REGISTER_POW` | The number of proof-of-work bits that a new account needs. This is for relays that accept members only. |
| `HUB_CALDAV` | A Nextcloud server. nginx forwards `/remote.php/dav/` to it, so the calendar needs no CORS. |
| `HUB_ICE`, `HUB_ICE_USERNAME`, `HUB_ICE_CREDENTIAL` | The STUN/TURN servers for calls and direct transfers, which help two browsers connect to each other. The TURN login is visible in the page, so create a TURN login that only this hub uses. |

`HUB_USER_MOUNTS` is read but has no effect yet. It belongs to a feature that
is still to come: following a space that the hub does not include.

The hub must be served over HTTPS, because WebCrypto needs a secure context.
Its relays must be served over `wss://`. If the hub is opened over plain
`http://` on anything other than localhost, the page says so and stops.

### Running a hub on your Kiwi Network { #on-a-kiwi-network }

A kiwi-master is the one server of a Kiwi Network that can be reached from
the Internet. It can run its own relay and its own hub, and two modules do
this. The `nostr-relay` module runs the relay software strfry at
`relay.<host>`. The `hub` module runs this container image, with Armory by
default, at `hub.<host>`.

Both are private by default. They can be reached from the mesh only, and they
use the fleet's certificate. For a semi-public hub, add `public_relays` and
`public_mounts`. For a public hub, add `reverse-proxy.public`, which gets Let's
Encrypt certificates.

The relay of a public hub accepts posts from the mesh. From the Internet it
accepts posts only from members who prove that they hold their key (NIP-42).
Members are the people on the list that the admins (`write_pubkeys`) sign. With
`members: registered`, a member is anyone who has an account on the hub. See
the [module reference](../server/modules.md#people).

## kiwi-web-catalog

[derlocke-ng/kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog)
is a catalog, which is a git repository that lists other repositories. It
lists hubs, their apps and the framework, and it has the same format as the
desktop catalog. The file `apps.list` has one git URL per line. A line can
carry `path=` for an app inside a hub's repository and `ref=` to pin a version.
Each entry contains a `kiwi.manifest` with a `CATEGORY` of `Framework`, `Hub`
or `App`.

Today it lists kiwi-framework, Armory and Armory's ten apps. It is **not**
meant for `kiwi catalog add`. Its entries have no installer, and nothing reads
the catalog automatically yet. According to its README, the catalog files are
in the public domain (CC0).

To add your hub, fork the catalog, add a line, make sure that your repository
contains a `kiwi.manifest`, and open a pull request.

## Not built yet

These items are on the framework's own roadmap and do not exist yet:

- The blog.
- Moderation approvals (NIP-72 kind 4550).
- Following a space that your hub does not include.
- Signing in through a browser extension (NIP-07) or a remote signer (NIP-46).
- A TURN server in the kiwi stack. The work for it is waiting in kiwi-modules.
  Without TURN, two phones on mobile data often cannot find a direct
  connection.
