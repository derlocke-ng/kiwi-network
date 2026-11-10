---
hide:
  - toc
---

<div class="kiwi-hero" markdown>

![](assets/logo.svg)

<p class="kiwi-motto">Ex fructu arbor agnoscitur</p>

# Kiwi Network

<p class="kiwi-lede">Twoja własna prywatna sieć: master przy bramie, node'y za nim, każda maszyna twoja. Zbudowana z jednego pliku, z jednymi drzwiami do Internetu.</p>

[Jak to działa](network/index.md){ .md-button .md-button--primary }
[Zbuduj własną](server/index.md){ .md-button }

</div>

<div class="kiwi-cards" markdown>

<a href="network/">
<strong>Sieć</strong>
<span>Jeden master, wiele node'ów, jedna sieć mesh WireGuard. Grupy klientów, wyjście z podwójnym skokiem, własny DNS i własne certyfikaty.</span>
<em>Jak to działa →</em>
</a>

<a href="server/">
<strong>kiwi-server</strong>
<span>Plik fleet, obrazy ISO instalacyjne, apply przez SSH, rejestracja, kopie zapasowe, odblokowywanie. CLI i aplikacja GTK.</span>
<em>Zbuduj sieć →</em>
</a>

<a href="server/modules/">
<strong>Moduły</strong>
<span>Wszystkie 20: WireGuard, Pi-hole, Tor, Nextcloud, Vaultwarden, kopie zapasowe, Tang, Immich, Paperless-ngx i więcej.</span>
<em>Czym może być node →</em>
</a>

<a href="people/">
<strong>Huby</strong>
<span>kiwi-framework: otwarte rynki, feedy, czat i udostępnianie na nostr, zapieczętowane w przeglądarce. Armory jest pierwszy.</span>
<em>Huby, nie platformy →</em>
</a>

<a href="desktop/">
<strong>Pulpit</strong>
<span>kiwi-updater i aplikacje dla Fedora Atomic: kill switch, zapieczętowane wyjścia dla sieci klientów, konfiguracja, synchronizacja.</span>
<em>Aplikacje z gita →</em>
</a>

<a href="project/status/">
<strong>Stan</strong>
<span>Każde repozytorium, jego wydanie i jego znane braki, opisane takimi, jakie są.</span>
<em>Gdzie jesteśmy →</em>
</a>

</div>

## Idea { #the-idea }

Kiwi Network to w pełni zautomatyzowane środowisko Linux do życia i pracy:
zabezpieczone, solidne i bezpieczne na trudne życie w sieci. Twoje maszyny same
o siebie dbają.

- **Same się instalują.** Nienadzorowany obraz ISO dla każdej maszyny albo
  instalacja prosto na wynajęty serwer przez API dostawcy (dziś netcup, kolejni
  [planowani](server/roadmap.md#more-hosters-and-network-boot)).
- **Same się aktualizują.** Aktualizacje instalują się na bieżąco, a restarty
  czekają na okno, które ustawisz.
- **Same robią swoje kopie zapasowe.** Co noc, zaszyfrowane i w trybie tylko do
  dopisywania, na twoje własne node'y z kopiami zapasowymi. Plik fleet i jego
  sekrety też mają kopie zapasowe.
- **Wracają na nogi.** Zaszyfrowane dyski odblokowują się przez Tang albo zdalnie,
  gdy coś jest nie tak, a odbudowana maszyna wraca z pliku fleet i swojej kopii
  zapasowej.

## Maszyny { #the-machines }

| Rola | Czym staje się maszyna |
|---|---|
| `master` | bramą: WireGuard, wyjście z podwójnym skokiem lub bezpośrednie, Pi-hole, Tor, strony administracyjne, opcjonalnie przekaźnik nostr i hub |
| `node` · `gateway` | LAN-em przez VPN, z Pi-hole jako DNS i DHCP, stacją pobierania i SFTP |
| `node` · `cloud` | Nextcloud z Collabora oraz Vaultwarden |
| `node` · `minimal` | tunelem i nginx dla wybranych przez ciebie modułów: kopie zapasowe, Tang, Immich, Paperless-ngx, OpenCloud |
| `bare` | samym systemem bazowym |

Nazwy masterów pochodzą od deserów i potraw z owoców (sorbet, crumble,
compote), a node'ów od owoców (papaya, lychee, quince). Master jest jedyną
maszyną, która musi być osiągalna z Internetu, i domyślnie publikuje jeden
port: WireGuard, UDP 51820.

```bash
kiwi install kiwi-server            # albo z klona: ./install.sh install
kiwi-server init && $EDITOR fleet.yaml
kiwi-server build fleet.yaml        # nienadzorowany obraz ISO dla każdej maszyny
kiwi-server apply fleet.yaml papaya # rola, przez SSH
```
