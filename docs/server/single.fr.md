# Une seule machine, sans fichier fleet

kiwi-server administre tout un ensemble de machines. Si vous voulez seulement
faire tourner une stack sur une seule machine, vous n’en avez pas besoin. Une
stack est l’ensemble des conteneurs et des services que fait tourner une
machine. kiwi-server repose sur deux outils plus petits, que vous pouvez
utiliser séparément :

| Dépôt | Ce que c’est |
|---|---|
| [**kiwi-modules**](https://github.com/derlocke-ng/kiwi-modules) | Les modules et leur générateur. Il lit **le fichier d’une machine et écrit un paquet de stack**, c’est-à-dire un dossier qui contient la configuration générée de la stack de la machine. v0.23.0, GPL-3.0-or-later |
| [**kiwi-stack**](https://github.com/derlocke-ng/kiwi-stack) | La partie qui tourne sur la machine. Elle se compose de la commande `kiwi-stack` et d’une bibliothèque, qui installent un paquet sur une machine CoreOS, uCore ou Debian et le maintiennent en marche. v0.5.0, GPL-3.0-or-later |

Utilisez ces deux outils quand vous voulez une stack sur une machine sans le
reste de kiwi-server : par exemple pour un node que vous configurez à la main,
pour un module que vous êtes en train de développer, ou pour une machine qui
génère sa propre stack. kiwi-server contient une copie de chacun des deux
outils, épinglée sur un tag de version. Le résultat sur la machine est
identique, que vous la configuriez avec kiwi-server ou avec les deux outils, et
les deux méthodes dérivent les mêmes secrets du même seed.

```
machine.yaml ──kiwi-modules render──▶ bundle/ ──copy──▶ sudo kiwi-stack apply bundle/
                                      stack.sh            → podman quadlets (or compose)
                                      docker-compose.yml  → configs, host units, timers
                                      quadlets/  configs  → kiwi-stack.target, verify
```

## Générer la configuration d’une machine { #render-a-machine }

Les commandes ci-dessous installent kiwi-modules, créent un seed et génèrent
un paquet à partir du fichier de machine d’exemple. La dernière ligne copie le
paquet sur la machine et l’y applique.

```bash
git clone https://github.com/derlocke-ng/kiwi-modules && cd kiwi-modules
./install.sh install                       # ~/.local/bin/kiwi-modules
mkdir -p sh3/secrets && head -c 32 /dev/urandom > sh3/secrets/seed
cp examples/sh3.yaml sh3/                  # à modifier : fichiers TLS, configuration WireGuard
kiwi-modules render sh3/sh3.yaml -o sh3/sh3.bundle
scp -r sh3/sh3.bundle sh3:/tmp/ && ssh sh3 sudo kiwi-stack apply /tmp/sh3.bundle
```

kiwi-modules a besoin de Python 3 avec PyYAML et Jinja2.
`kiwi-modules modules -v` liste tous les modules et tous les réglages, et
`kiwi-modules profiles` liste les rôles et leurs presets.

Un fichier de machine décrit une seule machine, comme dans cet exemple :

```yaml
# un node cloud
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
dns_records:                    # les noms du réseau
  - [10.8.0.1, gate.home]
  - [10.8.0.25, cloud.sh3.home]
master_ip: 10.8.0.1
ca_cert: ca.pem                 # reconnue dans les conteneurs et sur l'hôte
seed: secrets/seed              # les mots de passe générés en sont dérivés
```

kiwi-modules n’a pas d’autorité de certification propre. Lorsque vous générez
une machine sans kiwi-server, vous devez donc fournir vous-même les fichiers de
certificat et de clé TLS. Si le fichier de machine ne mentionne aucune
configuration WireGuard, kiwi-modules la cherche dans `secrets/<hostname>.conf`.

## L’installer sur la machine { #put-it-on-the-machine }

Sur la machine, installez kiwi-stack et appliquez le paquet :

```bash
git clone https://github.com/derlocke-ng/kiwi-stack && cd kiwi-stack
sudo ./install.sh install          # /usr/local/bin/kiwi-stack et sa bibliothèque
sudo kiwi-stack apply /tmp/sh3.bundle
kiwi-stack status
```

kiwi-stack a besoin de bash et de systemd. Il lui faut aussi le moteur de
conteneurs indiqué par le réglage `runtime` du paquet : soit podman 4.4+ avec
catatonit, soit docker avec le plugin compose. Sous Debian, kiwi-stack installe
podman lui-même.

`apply` fait avec une stack la même chose qu’un rôle kiwi-server (voir
[Machines](machines.md#apply)), sauf qu’il ne définit ni le nom d’hôte ni le
fuseau horaire. Vous pouvez le relancer autant de fois que vous voulez :
appliquer de nouveau le même paquet ne change rien. Il n’y a pas de retour
arrière. Pour récupérer des données, utilisez `kiwi-stack restore` du module
backup. Pour revenir à une configuration plus ancienne, appliquez un paquet
plus ancien.

Certains noms sur la machine contiennent encore `kiwi-server`, par exemple
`/etc/kiwi-server/stack.env` et `/var/lib/kiwi-server/`. C’est voulu, car ces
noms constituent le contrat entre les deux.
