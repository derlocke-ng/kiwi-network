# Une machine, sans fleet

kiwi-server est construit à partir de deux outils plus petits, et vous pouvez les
utiliser seuls :

| Dépôt | Ce que c’est |
|---|---|
| [**kiwi-modules**](https://github.com/derlocke-ng/kiwi-modules) | Les modules et leur moteur de rendu : **un fichier de machine en entrée, un bundle de stack en sortie**. v0.23.0, GPL-3.0-or-later |
| [**kiwi-stack**](https://github.com/derlocke-ng/kiwi-stack) | Le côté machine : la commande et la bibliothèque `kiwi-stack` qui installent un bundle sur CoreOS, uCore ou Debian et le maintiennent en marche. v0.5.0, GPL-3.0-or-later |

Utilisez-les quand vous voulez une stack sur une machine sans le reste : un node que
vous configurez à la main, un module que vous développez, ou une machine qui fait
elle-même le rendu de sa stack. kiwi-server embarque les deux, épinglés par tag.
Une machine configurée de l’une ou l’autre façon finit identique, et les deux
dérivent les mêmes secrets de la même graine.

```
machine.yaml ──kiwi-modules render──▶ bundle/ ──copy──▶ sudo kiwi-stack apply bundle/
                                      stack.sh            → podman quadlets (or compose)
                                      docker-compose.yml  → configs, host units, timers
                                      quadlets/  configs  → kiwi-stack.target, verify
```

## Faire le rendu d’une machine { #render-a-machine }

```bash
git clone https://github.com/derlocke-ng/kiwi-modules && cd kiwi-modules
./install.sh install                       # ~/.local/bin/kiwi-modules
mkdir -p sh3/secrets && head -c 32 /dev/urandom > sh3/secrets/seed
cp examples/sh3.yaml sh3/                  # à modifier : fichiers TLS, la configuration WireGuard
kiwi-modules render sh3/sh3.yaml -o sh3/sh3.bundle
scp -r sh3/sh3.bundle sh3:/tmp/ && ssh sh3 sudo kiwi-stack apply /tmp/sh3.bundle
```

Il faut Python 3 avec PyYAML et Jinja2. `kiwi-modules modules -v` liste chaque
module et chaque réglage, et `kiwi-modules profiles` liste les rôles et leurs
presets.

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
dns_records:                    # the network's names
  - [10.8.0.1, gate.home]
  - [10.8.0.25, cloud.sh3.home]
master_ip: 10.8.0.1
ca_cert: ca.pem                 # reconnue dans les conteneurs et sur l’hôte
seed: secrets/seed              # les mots de passe générés en dérivent
```

kiwi-modules n’a pas d’autorité de certification propre, donc un rendu autonome a
besoin des fichiers de certificat et de clé TLS. La configuration WireGuard est
trouvée dans `secrets/<hostname>.conf` quand le fichier de machine n’en nomme
aucune.

## L’installer sur la machine { #put-it-on-the-machine }

```bash
git clone https://github.com/derlocke-ng/kiwi-stack && cd kiwi-stack
sudo ./install.sh install          # /usr/local/bin/kiwi-stack et sa bibliothèque
sudo kiwi-stack apply /tmp/sh3.bundle
kiwi-stack status
```

Il faut bash et systemd, plus podman 4.4+ avec catatonit (ou docker avec le plugin
compose), selon le `runtime` du bundle. Sous Debian, il installe podman lui-même.

`apply` fait ce que fait un rôle kiwi-server avec une stack (voir
[Machines](machines.md#apply)), sauf régler le nom d’hôte et le fuseau horaire. Il
est répétable : le même bundle une seconde fois ne change rien. Il n’y a pas de
retour arrière. Les données reviennent avec `kiwi-stack restore` depuis le module
de sauvegarde, et une configuration plus ancienne en appliquant un bundle plus
ancien.

Sur la machine, les noms disent toujours `kiwi-server`
(`/etc/kiwi-server/stack.env`, `/var/lib/kiwi-server/`), à dessein : ils sont le
contrat entre les deux.
