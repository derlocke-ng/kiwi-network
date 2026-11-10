---
hide:
  - toc
---

<div class="kiwi-hero" markdown>

![](assets/logo.svg)

<p class="kiwi-motto">Ex fructu arbor agnoscitur</p>

# Kiwi Network

<p class="kiwi-lede">Otwartoźródłowe środowisko linuksowe, które prowadzisz samodzielnie: twoje serwery, urządzenia i desktop połączone w jedną prywatną sieć. Samo się instaluje, samo się aktualizuje, co noc robi kopię zapasową, a gdy coś się zepsuje, da się je odbudować.</p>

[Jak to działa](network/index.md){ .md-button .md-button--primary }
[Zbuduj własną sieć](server/index.md){ .md-button }

</div>

<div class="kiwi-cards" markdown>

<a href="network/">
<strong>Sieć</strong>
<span>Twoje serwery i urządzenia w jednej prywatnej sieci WireGuard. Z internetu dostępny jest tylko jeden serwer, pozostałe zostają w domu.</span>
<em>Jak to działa →</em>
</a>

<a href="server/">
<strong>kiwi-server</strong>
<span>Narzędzie, którym budujesz sieć i nią zarządzasz: jeden plik dla wszystkich maszyn, automatyczna instalacja, kopie zapasowe i odblokowywanie dysków.</span>
<em>Zbuduj własną sieć →</em>
</a>

<a href="server/modules/">
<strong>Moduły</strong>
<span>20 usług, które może uruchamiać maszyna: od serwera WireGuard i Pi-hole po Nextcloud, Vaultwarden, kopie zapasowe i Immich.</span>
<em>Co może uruchamiać node →</em>
</a>

<a href="people/">
<strong>Huby</strong>
<span>Dzięki kiwi-framework społeczność prowadzi własny hub z otwartym rynkiem, kanałem i czatem, bez żadnej centralnej platformy.</span>
<em>Huby społeczności →</em>
</a>

<a href="desktop/">
<strong>Desktop</strong>
<span>Stacja robocza z Fedorą Atomic i aplikacjami prosto z gita: kill switch dla VPN, odizolowane połączenia z sieciami klientów, konfiguracja systemu i synchronizacja.</span>
<em>Aplikacje na desktop →</em>
</a>

<a href="project/status/">
<strong>Stan projektu</strong>
<span>Wszystkie repozytoria z aktualnym wydaniem i tym, czego jeszcze brakuje.</span>
<em>Aktualny stan →</em>
</a>

</div>

## Pomysł { #the-idea }

Internet bywa bezlitosny, a opieka nad własnymi serwerami to praca bez końca.
Kiwi Network wykonuje ją za ciebie. Opisujesz swoje maszyny w jednym pliku,
a rutynowe zadania wykonują się same. Włamania, awarie dysków i utrata sprzętu
są uwzględnione od samego początku.

- **Automatyczna instalacja.** Każda maszyna instaluje się bez nikogo przy
  klawiaturze: z własnego obrazu instalacyjnego albo bezpośrednio na wynajętym
  serwerze, przez API dostawcy hostingu. Obecnie obsługiwany jest netcup,
  a kolejni dostawcy są
  [planowani](server/roadmap.md#more-hosters-and-network-boot).
- **Automatyczne aktualizacje.** Aktualizacje instalują się same. Maszyna
  uruchamia się ponownie tylko w godzinach, na które pozwolisz.
- **Kopia zapasowa co noc.** Każda maszyna wysyła zaszyfrowaną kopię zapasową
  na twój własny serwer kopii zapasowych. Może tylko dopisywać do swoich kopii,
  ale nie może ich usuwać, więc włamywacz ich nie skasuje. Kopię zapasową mają
  też plik fleet i jego sekrety.
- **Ratunek w razie awarii.** Dyski są zaszyfrowane. Przy starcie maszyny
  odblokowują je same albo odblokowujesz je zdalnie. Maszyna, którą trzeba
  odbudować, dostaje konfigurację z pliku fleet, a dane z kopii zapasowej.

## Maszyny { #the-machines }

Każda maszyna ma rolę. Od roli zależy, czym maszyna zajmuje się w sieci.

| Rola | Co robi maszyna |
|---|---|
| `master` | Jedyna maszyna dostępna z internetu. Działa na niej serwer WireGuard. Ruch wychodzący wysyła przez dostawcę VPN albo bezpośrednio, a do tego udostępnia DNS z Pi-hole, Tor i strony administracyjne. Może też uruchamiać przekaźnik nostr i hub. |
| `node` · `gateway` | Kieruje sieć domową lub biurową przez VPN. Pi-hole jest w niej serwerem DNS i DHCP, a do tego dochodzą stacja pobierania plików i SFTP. |
| `node` · `cloud` | Uruchamia Nextcloud z pakietem Collabora oraz Vaultwarden. |
| `node` · `minimal` | Ma tylko połączenie z siecią i nginx. Moduły dobierasz samodzielnie, na przykład kopie zapasowe, Tang, Immich, Paperless-ngx albo OpenCloud. |
| `bare` | Ma tylko system podstawowy. |

Mastery noszą nazwy potraw z owoców (sorbet, crumble, compote), a node’y nazwy
owoców (papaya, lychee, quince). Master to jedyna maszyna, która musi być
dostępna z internetu. Domyślnie otwarty jest na nim dokładnie jeden port:
WireGuard, UDP 51820.

```bash
kiwi install kiwi-server            # albo z klona: ./install.sh install
kiwi-server init && $EDITOR fleet.yaml
kiwi-server build fleet.yaml        # dla każdej maszyny osobny obraz ISO, który instaluje się bez twojego udziału
kiwi-server apply fleet.yaml papaya # rola, przez SSH
```
