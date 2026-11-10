# Running your own hub

A hub is static files, so hosting one is serving a folder over HTTPS. There are
three ways to run one:

- **Use Armory as it is:** [derlocke-ng.github.io/armory](https://derlocke-ng.github.io/armory/).
- **Make your own distribution:** your name, relays and apps, on any static host.
- **Run the hub container:** for example inside your own Kiwi Network, with your
  own relay, as a private hub that only the mesh can reach.

## Kinds of hub

| Kind | How | Example |
|---|---|---|
| **Public** | Public relays; anyone can open it | Armory |
| **Private** | The hub's relays are locked (`policy.relays: 'locked'`) and pages wait until one of them answers (`requireHub`), with relays inside a VPN | a company hub on a kiwi-node |
| **Semi-public** | A private hub with a public area for chosen apps (the chat, for example) on public relays | |

Every event belongs to one network (the hub's own, the public area, or a
space's) and never crosses to another.

## Your own distribution

Armory is the template (on GitHub, *Use this template* gives you a copy without
its history):

1. Edit **`distribution.js`**: id, name, mark, description, homepage, repository,
   relays, media servers, spaces, apps and mounts. To serve Armory's spaces as
   well, copy their `owner` and `id` from Armory's `hub.json`.
2. Edit **`locales/*.json`**: the title, lead and footer, and one card text per
   mount. English is the fallback.
3. Update **`kiwi.manifest`** and, optionally, add your hub to
   [kiwi-web-catalog](#kiwi-web-catalog).
4. On GitHub: *Settings → Pages → Source: GitHub Actions*, then push.

```bash
npm install
npm run dev                  # the hub with hot reload, http://localhost:5173
npm test
npm run build && npm run serve
npm run relay:nostr          # a local test relay on ws://localhost:7777
npm run new-app -- <id> "<Name>" <icon>   # scaffold a new app
```

Pin kiwi-framework by commit or tag, never by branch. The build checks your
`distribution.js` (for example, a public mount needs public relays and the
other way round).

The stack is TypeScript, React 19 and Vite for everything visible. The data
layer in `shared/` is plain JavaScript with JSDoc types. Tests run in node's test
runner and, for the browser, in Playwright.

## The hub container

Armory is also a container image, `ghcr.io/derlocke-ng/armory`, built from the
framework's `container/Dockerfile` (nginx). At start, its entrypoint writes
`hub.local.json` from `HUB_*` variables, and the page reads it before it
connects. A deployment can choose relays and policy that way, but it cannot add
code. With no variables set, the hub runs as built.

```bash
docker run --rm -p 8080:80 \
  -e HUB_RELAYS=wss://relay.sh3.home \
  -e HUB_RELAYS_LOCKED=true -e HUB_REQUIRE_HUB=true \
  -e HUB_PUBLIC_RELAYS=wss://nos.lol -e HUB_PUBLIC_MOUNTS=uplink \
  ghcr.io/you/your-hub
```

| Variable | Meaning |
|---|---|
| `HUB_RELAYS` | the hub's own relays |
| `HUB_PUBLIC_RELAYS` | the public area's relays (set and empty: no public area) |
| `HUB_DIRECTORY_RELAYS` | where relay lists are published and looked up |
| `HUB_RELAYS_LOCKED` | `true`: people cannot replace the hub's relays |
| `HUB_REQUIRE_HUB` | `true`: pages wait while none of the hub's relays answers |
| `HUB_PUBLIC_MOUNTS` | mounts on the public area, by id |
| `HUB_ACCOUNT_MOUNTS` | mounts that ask for an account |
| `HUB_REQUIRE_ACCOUNT` | `true`: every mount asks for an account |
| `HUB_SPACE_RELAYS` | relays per space: `jobs=wss://…;gems=wss://a,wss://b` |
| `HUB_MODERATORS` | keys that moderate every space the hub defines |
| `HUB_REGISTER_POW` | proof-of-work bits for a new account (members-only relays) |
| `HUB_CALDAV` | a Nextcloud; nginx forwards `/remote.php/dav/` to it, so the calendar needs no CORS |
| `HUB_ICE`, `HUB_ICE_USERNAME`, `HUB_ICE_CREDENTIAL` | STUN/TURN servers for calls and direct transfers. The TURN login is visible in the page, so give it a login for this hub alone |

`HUB_USER_MOUNTS` is read but does nothing yet: following a space the hub does
not ship is still to come.

The hub must be served over HTTPS (WebCrypto needs a secure context) and its
relays over `wss://`. Over plain `http://` (other than localhost) the page says
so and stops.

### On a Kiwi Network

A kiwi-master can carry its own relay and hub: the `nostr-relay` module (strfry
at `relay.<host>`) and the `hub` module (this image, Armory by default, at
`hub.<host>`). They are private by default: reachable from the mesh only, with
the fleet's certificate. A semi-public hub adds `public_relays` and
`public_mounts`. A public one adds `reverse-proxy.public`, which gets Let's
Encrypt certificates. The relay then accepts posts only from the mesh and from
the keys in `write_pubkeys`. See the [module reference](../server/modules.md#people).

## kiwi-web-catalog

[derlocke-ng/kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog)
lists hubs, their apps and the framework, in the same shape as the desktop
catalog: an `apps.list` with one git URL per line (`path=` for an app inside a
hub's repository, `ref=` to pin), and a `kiwi.manifest` in each entry with a
`CATEGORY` of `Framework`, `Hub` or `App`.

Today it lists kiwi-framework, Armory and Armory's ten apps. It is **not** for
`kiwi catalog add`: these entries have no installer. The kiwi-server module
that installs a hub onto a node will read it once that module exists. The
catalog files are public domain (CC0, per its README).

To add your hub: fork, add a line, make sure the repository carries a
`kiwi.manifest`, and open a pull request.

## Not built yet

These come from the framework's own roadmap:

- The blog.
- Moderation approvals (NIP-72 kind 4550).
- Following spaces a hub does not ship.
- NIP-07 and NIP-46 signers.
- A TURN server in the kiwi stack. It is waiting in kiwi-modules; without TURN,
  two phones on mobile data often find no direct path.
