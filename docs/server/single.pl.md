# Jedna maszyna, bez floty

kiwi-server jest zbudowany z dwóch mniejszych narzędzi, których możesz używać
osobno:

| Repozytorium | Co to jest |
|---|---|
| [**kiwi-modules**](https://github.com/derlocke-ng/kiwi-modules) | Moduły i ich renderer: **na wejściu jeden plik maszyny, na wyjściu paczka stacka**. v0.23.0, GPL-3.0-or-later |
| [**kiwi-stack**](https://github.com/derlocke-ng/kiwi-stack) | Strona maszyny: polecenie `kiwi-stack` i biblioteka, które umieszczają paczkę na CoreOS, uCore lub Debianie i utrzymują ją w działaniu. v0.5.0, GPL-3.0-or-later |

Używaj ich, gdy chcesz mieć stack na jednej maszynie bez reszty: node
konfigurowany ręcznie, moduł, który rozwijasz, albo maszynę, która renderuje
własny stack. kiwi-server dołącza oba do repozytorium (vendored), przypięte
tagiem. Maszyna skonfigurowana dowolną z tych dróg wychodzi identyczna, a oba
wyprowadzają te same sekrety z tego samego seeda.

```
machine.yaml ──kiwi-modules render──▶ bundle/ ──copy──▶ sudo kiwi-stack apply bundle/
                                      stack.sh            → podman quadlets (or compose)
                                      docker-compose.yml  → configs, host units, timers
                                      quadlets/  configs  → kiwi-stack.target, verify
```

## Wyrenderuj maszynę { #render-a-machine }

```bash
git clone https://github.com/derlocke-ng/kiwi-modules && cd kiwi-modules
./install.sh install                       # ~/.local/bin/kiwi-modules
mkdir -p sh3/secrets && head -c 32 /dev/urandom > sh3/secrets/seed
cp examples/sh3.yaml sh3/                  # edytuj: pliki TLS, konfiguracja WireGuard
kiwi-modules render sh3/sh3.yaml -o sh3/sh3.bundle
scp -r sh3/sh3.bundle sh3:/tmp/ && ssh sh3 sudo kiwi-stack apply /tmp/sh3.bundle
```

Potrzebuje Pythona 3 z PyYAML i Jinja2. `kiwi-modules modules -v` wypisuje
każdy moduł i ustawienie, a `kiwi-modules profiles` wypisuje role i ich
presety.

```yaml
# node cloud
name: sh3
domain: home
target: ucore
timezone: Europe/Berlin
admin: { user: core }
role: node
node:
  preset: cloud
  cloud: { collabora: true, talk: true }
  reverse-proxy:
    tls_fullchain: secrets/sh3-fullchain.pem
    tls_privkey: secrets/sh3-privkey.pem
dns_records:                    # the network's names
  - [10.8.0.1, gate.home]
  - [10.8.0.25, cloud.sh3.home]
master_ip: 10.8.0.1
ca_cert: ca.pem                 # zaufany wewnątrz kontenerów i na hoście
seed: secrets/seed              # z niego wyprowadzane są wygenerowane hasła
```

kiwi-modules nie ma własnego urzędu certyfikacji, więc samodzielny render
potrzebuje plików certyfikatu i klucza TLS. Konfiguracja WireGuard jest
szukana w `secrets/<hostname>.conf`, gdy plik maszyny żadnej nie wskazuje.

## Umieść to na maszynie { #put-it-on-the-machine }

```bash
git clone https://github.com/derlocke-ng/kiwi-stack && cd kiwi-stack
sudo ./install.sh install          # /usr/local/bin/kiwi-stack i jego biblioteka
sudo kiwi-stack apply /tmp/sh3.bundle
kiwi-stack status
```

Potrzebuje basha i systemd, plus podmana 4.4+ z catatonit (albo dockera z
wtyczką compose), zależnie od `runtime` paczki. Na Debianie sam instaluje
podmana.

`apply` robi to, co rola kiwi-server robi ze stackiem (zobacz
[Maszyny](machines.md#apply)), poza ustawieniem nazwy hosta i strefy czasowej.
Jest powtarzalne: ta sama paczka ponownie niczego nie zmienia. Nie ma
wycofywania zmian. Dane wracają przez `kiwi-stack restore` z modułu backup, a
starsza konfiguracja przez zastosowanie starszej paczki.

Na maszynie nazwy nadal mówią `kiwi-server` (`/etc/kiwi-server/stack.env`,
`/var/lib/kiwi-server/`), celowo: narzędzia Kiwi
opierają się na tych nazwach, więc nie są one zmieniane.
