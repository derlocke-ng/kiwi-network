# kiwi-fox

kiwi-fox gibt dir einen eigenen Browser für jedes Kundennetz, in dem du
arbeitest, und für jedes Konto, das du verwaltest. Ein Browser-Profil für einen
Kunden erreicht die Weboberflächen dieses Kunden über dessen Verbindung und hat
keinen anderen Weg nach draußen. Eine VPN-Verbindung auf dem Host brauchst du
dafür nicht.

Jedes Profil ist eine dauerhafte Identität. Es hat seinen eigenen Speicher,
führt einen von drei Browsern in einem Rootless-Container von Podman aus (einem
Container, der unter deinem eigenen Benutzer ohne Root-Rechte läuft) und nutzt
meist einen Exit von [kiwi-proxy](kiwi-proxy.md). Ein Exit ist eine Verbindung
zu einem Upstream, die einen Namen hat, etwa der SOCKS5-Proxy eines Kunden. Für
jeden Exit betreibt kiwi-proxy ein Gateway. Das Gateway ist ein Container,
dessen einzige Route zu diesem Upstream führt, und es enthält einen
DNS-Resolver, der Werbedomains blockiert.

- Repository: [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Aktuelles Release: **v0.7.1**. Es steht im [Kiwi-Katalog](../desktop/catalogs.md), Scope user.
- Die Browser, bei kiwi-fox Engines genannt, werden auf deinen Rechner
  heruntergeladen und nie weiterverbreitet. Camoufox (MPL-2.0) wird beim Setup
  geladen. Firefox und Tor Browser werden geladen, wenn du sie anforderst
  (`kiwi-fox engine fetch`), und ihre Signaturen werden geprüft.

| Engine | Was eine Seite sieht |
|---|---|
| **Camoufox** (voreingestellt) | Einen gewöhnlichen Rechner mit Windows 11 und eigener Region, dessen Werte alle zueinander passen. Dieser Fingerprint (die Gesamtheit der Werte, die eine Seite aus einem Browser auslesen kann, um ihn wiederzuerkennen) ist vorgetäuscht und ändert sich nicht |
| **Firefox** | Unverändertes Mozilla Firefox, das nichts vortäuscht. Eine Seite sieht die echten Werte dieses Rechners. Die Verbindung läuft trotzdem über den Exit des Profils |
| **Tor Browser** | Unveränderter Tor Browser, verbunden über einen Exit des Tor-Moduls. Jede Website bekommt ihren eigenen Circuit (ihren eigenen Pfad durch das Tor-Netzwerk), und `.onion`-Namen funktionieren |

kiwi-fox ist für Leute gedacht, die mehrere Konten verwalten, die ihnen
gehören oder die sie betreuen dürfen, und die nicht wollen, dass diese Konten
über den Fingerprint des Browsers oder die IP-Adresse miteinander in
Verbindung gebracht werden.

## Installation { #install }

```bash
kiwi install kiwi-fox      # bringt kiwi-proxy mit; oder ./install.sh install
kiwi-fox setup             # Images, eine Browser-Engine von ~630 MB, DNS-Daten; führt auch das Setup von kiwi-proxy aus
kiwi-fox engine fetch --engine firefox     # oder torbrowser: mit geprüfter Signatur
```

kiwi-fox braucht rootless Podman, kiwi-proxy, Python 3.12+, GTK4 mit
libadwaita und `secret-tool`. Es ist für eine Wayland-Sitzung gemacht. X11
funktioniert auch, schottet aber schwächer ab. Um Firefox und Tor Browser zu
prüfen, werden `gpg`/`gpgv` gebraucht. Mit dem proprietären NVIDIA-Treiber
braucht kiwi-fox außerdem `nvidia-container-toolkit` mit seiner CDI-Spec.

## Bedienung { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # ein Exit, einmal in kiwi-proxy angelegt
kiwi-fox new work --exit client-a     # ein Profil darauf: misst den Exit und erzeugt eine passende Identität
kiwi-fox new plain --no-proxy         # die eigene Verbindung dieses Rechners, nichts abgeriegelt
kiwi-fox list                         # --tag shop, --by-tag
kiwi-fox run work                     # oder über die App
kiwi-fox stop work
kiwi-fox check                        # passt bei jedem Profil noch alles zusammen?
kiwi-fox selfcheck work               # messen, was Seiten sehen, und das Ergebnis prüfen
kiwi-fox-gui                          # "Kiwi Fox" in der Anwendungsübersicht
```

Mit `--desktop-entry` bekommt ein Profil einen eigenen Eintrag in der
Anwendungsübersicht. Mit Tags kannst du Profile gruppieren.

## Profile und Exits { #profiles-and-exits }

Ein Profil besitzt keinen Exit, es verweist nur auf einen, und mehrere Profile
können auf denselben Exit verweisen. Profile am selben Exit teilen sich dessen
Gateway und damit einen Netzwerk-Namespace, eine IP-Adresse nach außen und einen
Satz Tor-Circuits. Identitäten, die sich keinen Exit teilen dürfen, brauchen
verschiedene Exits. Ein Profil, das mit `--no-proxy` angelegt wurde, hat kein
Gateway. Sein Browser-Container hat ein eigenes Netzwerk und nutzt die eigene
Verbindung dieses Rechners. In diesem Fall ist nichts abgeriegelt, sein
Verkehr ist also nicht auf eine einzige Route beschränkt.

Der Browser-Container teilt sich den Netzwerk-Namespace des Gateways. Ihm wird
jede Linux-Capability entzogen außer `SYS_CHROOT`, die die eigene Sandbox von
Firefox braucht. Der Container läuft mit `no-new-privileges`, und die Engine
ist nur lesbar eingebunden.

## Ein Camoufox-Profil { #a-camoufox-profile }

Ein Camoufox-Profil gibt sich als der häufigste Rechner aus, den es gibt, denn
Erkennungssysteme schlagen bei seltenen Werten an. Es meldet einen Bildschirm
mit 1920×1080, genau die Schriften, die jede Installation von Windows 11 hat,
und keine anderen, sowie die echte Grafikkarte dieses Rechners, so benannt, wie
Firefox unter Windows sie benennt. Region, Sprache, Zeitzone und Stimmen für die Sprachausgabe werden
passend zum Exit gesetzt. Mit `kiwi-fox set`, `kiwi-fox webgl` und
`kiwi-fox fonts` kannst du all das nachträglich ändern. Eine Änderung wird nur
gespeichert, wenn das Profil stimmig bleibt, seine Werte also weiterhin
zueinander passen.

## Was es nicht kann { #what-it-does-not-do }

kiwi-fox verspricht nicht, dass ein Profil „nicht erkennbar“ ist. Getrennt
sind Profile in ihrem Speicher, ihrer IP-Adresse und jedem Wert, den die Engine
vortäuschen kann. **Nicht** getrennt sind sie bei Merkmalen, die von
der Hardware stammen und in jedem Browser gleich sind. Die Bilder, die die GPU
tatsächlich zeichnet, und das Zeitverhalten der Hardware kommen vom echten
Rechner und sind deshalb für jedes Profil darauf gleich. Was gemessen wird,
dokumentiert die Datei `docs/detection-notes.md` im Repository.

kiwi-fox automatisiert nichts. Es betreibt keine Bots und legt keine Konten in
großer Zahl an. Es ist ausschließlich zum Surfen von Hand gedacht.
