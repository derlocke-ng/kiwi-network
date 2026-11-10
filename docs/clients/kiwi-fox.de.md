# kiwi-fox

Isolierte Browser-Identitäten in rootless Podman.

Jedes Profil ist eine dauerhafte Identität: eigener Speicher und meist ein Ausgang
von [kiwi-proxy](kiwi-proxy.md) mit seinem versiegelten Gateway und seinem
Resolver mit Werbeblocker, in einem von drei Browsern. Für ein Kundennetz heißt
das: ein Browser, der die Webkonsolen des Kunden über den Ausgang des Kunden
erreicht, und sonst nichts.

- Repository: [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Aktuelles Release: **v0.7.1**. Es steht im [Kiwi-Katalog](../desktop/catalogs.md), Benutzerbereich.
- Die Engines werden heruntergeladen, nie weiterverteilt: Camoufox (MPL-2.0) beim
  Setup, Firefox und Tor Browser auf Anfrage (`kiwi-fox engine fetch`), mit
  geprüfter Signatur.

| Engine | Was eine Seite sieht |
|---|---|
| **Camoufox** (Standard) | eine stimmige, gewöhnliche Windows-11-Maschine mit eigener Region: ein eingefrorener, gefälschter Fingerabdruck |
| **Firefox** | unverändertes Mozilla Firefox, das nichts fälscht: die eigenen Werte dieser Maschine, über denselben versiegelten Ausgang |
| **Tor Browser** | Tor Browser, unverändert, über einen Ausgang des Tor-Moduls, mit einem Circuit pro Website und `.onion`-Namen |

kiwi-fox ist für Leute, die mehrere Konten verwalten, die ihnen gehören oder die sie
betreiben dürfen, und die nicht wollen, dass diese Konten über
Browser-Fingerabdruck oder IP miteinander verknüpft werden.

## Installation { #install }

```bash
kiwi install kiwi-fox      # brings kiwi-proxy along; or ./install.sh install
kiwi-fox setup             # images, a ~630 MB browser engine, DNS data; runs kiwi-proxy's setup too
kiwi-fox engine fetch --engine firefox     # or torbrowser: signature-verified
```

Es braucht rootless Podman und kiwi-proxy, eine Wayland-Sitzung (X11 funktioniert,
mit einer schwächeren Grenze), Python 3.12+, GTK4 + libadwaita, `secret-tool` und
`gpg`/`gpgv`, um Firefox und Tor Browser zu prüfen. Mit dem proprietären
NVIDIA-Treiber braucht es außerdem `nvidia-container-toolkit` mit seiner CDI-Spec.

## Benutzung { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # an exit, defined once, in kiwi-proxy
kiwi-fox new work --exit client-a     # a profile on it: probes it, draws a matching identity
kiwi-fox new plain --no-proxy         # this machine's own connection, nothing sealed
kiwi-fox list                         # --tag shop, --by-tag
kiwi-fox run work                     # or the app
kiwi-fox stop work
kiwi-fox check                        # is every profile still coherent?
kiwi-fox selfcheck work               # measure what pages see, then audit it
kiwi-fox-gui                          # "Kiwi Fox" in the app grid
```

`--desktop-entry` legt ein Profil ins App-Raster, und Tags gruppieren Profile.

## Profile und Ausgänge { #profiles-and-exits }

Ein Profil verweist auf einen Ausgang, und Ausgänge werden geteilt: Profile auf
einem Ausgang teilen sich sein Gateway (ein Namespace, eine Ausgangs-IP, ein Satz
Tor-Circuits). Identitäten, die sich keinen Ausgang teilen dürfen, nehmen
verschiedene Ausgänge. Mit `--no-proxy` gibt es kein Gateway: Der Browser-Container
hat ein eigenes Netzwerk über die Verbindung dieser Maschine, und nichts ist
versiegelt.

Der Browser-Container tritt dem Namespace des Gateways bei, wobei jede Capability
entzogen ist außer `SYS_CHROOT` (die Firefox' eigene Sandbox braucht). Er läuft mit
`no-new-privileges`, und die Engine ist schreibgeschützt eingebunden.

## Ein Camoufox-Profil { #a-camoufox-profile }

Es ist die gewöhnlichste Maschine, die es gibt, denn seltene Werte sind das, was
Detektoren anschlagen lässt: ein Bildschirm mit 1920×1080, die Schriften, die jedes
Windows 11 hat, und keine anderen, und die eigene Grafikkarte dieser Maschine so,
wie Firefox unter Windows sie benennt. Region, Sprache, Zeitzone und Stimmen richten
sich nach dem Ausgang. Alles lässt sich nachträglich ändern (`kiwi-fox set`,
`kiwi-fox webgl`, `kiwi-fox fonts`), und Änderungen werden nur gespeichert, wenn das
Ergebnis stimmig bleibt.

## Was es nicht tut { #what-it-does-not-do }

Es verspricht nicht „unentdeckbar“. Profile sind isoliert, was Speicher, IP und jede
Oberfläche angeht, die die Engine fälschen kann, aber **nicht** gegen
browserübergreifende Kennungen auf Hardware-Ebene: Die Frames, die die GPU
tatsächlich zeichnet, und das Hardware-Timing kommen von der echten Maschine und
sind für jedes Profil darauf gleich. Die Datei `docs/detection-notes.md` im
Repository dokumentiert, was gemessen wird.

Es gibt keine Automatisierung: keine Bots und kein massenhaftes Anlegen von Konten.
Es ist nur für interaktives Surfen gedacht.
