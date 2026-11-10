# Machines : installer, appliquer, mettre à jour

## Cibles { #targets }

| Cible | Ce qui est installé | Support d’installation |
|---|---|---|
| `coreos` | Fedora CoreOS, flux stable | l’ISO live standard, personnalisée avec l’Ignition de l’hôte (Butane `fcos` 1.6.0) ; aucun réseau nécessaire pour l’installation |
| `ucore` | Fedora CoreOS qui se rebase lui-même sur une image `ghcr.io/ublue-os/ucore*` (`ucore-minimal`, `ucore`, `ucore-hci`, avec `-nvidia` / `-zfs`), comme l’exemple d’autorebase de uCore lui-même | comme pour CoreOS, plus les unités d’autorebase |
| `debian` | Debian stable (trixie), amd64 | le netinst standard avec le preseed dans son initrd, si bien qu’il répond dès la première question, et les fichiers de l’hôte sous `/kiwi-server` ; démarrage BIOS et UEFI conservés |

L’utilisateur admin reçoit sudo sans mot de passe partout. SSH n’accepte que les
clés, sauf si vous réglez `ssh_password_auth: true`.

## Supports d’installation { #install-media }

```bash
kiwi-server build fleet.yaml sorbet      # → output/sorbet/sorbet.iso
sudo dd if=output/sorbet/sorbet.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

- Une ISO installe sur `disk:` **sans demander** puis **éteint la machine**
  (`install.on_done: poweroff`, ou `reboot`). Étiquetez vos clés USB.
- Par défaut, les supports ne contiennent **que le système de base** : nom d’hôte,
  réseau, utilisateur admin et clés, politique de mises à jour. Aucun des secrets
  de la stack ne s’y trouve. Le rôle arrive plus tard avec `apply`.
- `--offline` place tout le rôle et ses secrets sur l’ISO, pour une machine que SSH
  ne peut pas atteindre. Quiconque détient cette ISO détient ces secrets.
- L’installateur live affiche les disques (`lsblk`) et fournit un shell avec le mot
  de passe de console et les clés de la fleet.

## Application { #apply }

```bash
kiwi-server apply fleet.yaml papaya                         # par nom, adresse ou adresse de maillage
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25 # la première fois, par adresse
```

`apply` refait le rendu de l’hôte et envoie son script de rôle via SSH vers
`/var/lib/kiwi-server/role.sh`. Il exécute le script en tant que root, puis lie le
disque à ses anneaux Tang et, sur un master, enregistre l’état WireGuard avec les
secrets de la fleet. Sur une machine Debian chiffrée, la première application
remplace la clé d’installation à usage unique. SSH utilise la clé propre à la fleet
et vérifie les clés d’hôte par rapport à `secrets/known_hosts`. `apply` et `status`
trouvent une machine par son nom, son adresse statique, l’adresse publique du
master ou son adresse de maillage, mais uniquement parmi les adresses dont la clé
d’hôte est enregistrée.

Pour un rôle à modules, le script confie la stack à `kiwi-stack` :

1. Il installe ou active podman 4.4+ (sous Debian avec `netavark`,
   `aardvark-dns` et `catatonit`) ou docker, ainsi que l’utilisateur de service.
2. Il charge des modules du noyau et règle des sysctls. Avec Pi-hole,
   aardvark-dns passe sur le port 5533 et l’hôte résout via le Pi-hole de la
   stack. Il fait aussi confiance au maillage dans firewalld.
3. Il refuse une stack rendue à partir d’une autre graine. Il décompresse la stack
   dans `docker_dir`, installe les quadlets dans `/etc/containers/systemd` et les
   unités de l’hôte, et supprime ce qu’avait installé un module qui a été retiré.
4. Il ouvre les ports de la stack dans firewalld ou ufw, si l’un d’eux est actif.
5. Il télécharge chaque image, puis démarre `kiwi-stack.service`
   (→ `kiwi-stack.target`).
6. Il lance `kiwi-stack verify` : chaque conteneur doit tourner, sinon
   l’application échoue et indique quelle étape a échoué.

Appliquer à nouveau le même rendu ne change rien, et un nouveau rendu remplace ce
qui a changé. Une nouvelle application redémarre bien chaque conteneur de la stack.

## Premier démarrage { #first-boot }

`kiwi-role.service` exécute `/var/lib/kiwi-server/role.sh` une fois, après que le
réseau est actif (en attendant jusqu’à 120 secondes le DNS). `role.done` n’est
écrit qu’une fois que chaque conteneur tourne. Un échec laisse
`/var/lib/kiwi-server/role.failed` (l’étape et la commande) et est retenté au
démarrage suivant. Le journal est `/var/log/kiwi-server-role.log`. Sous uCore, le
rôle attend que l’image soit signée.
`sudo bash /var/lib/kiwi-server/role.sh --force` le relance.

## Mises à jour { #updates }

Les mises à jour s’installent en continu. Le **redémarrage** sur celles-ci n’a lieu
que dans votre créneau (`updates.days`, `time`, `length_minutes`, heure locale) :

| Cible | Installe les mises à jour | Redémarre |
|---|---|---|
| `coreos` | Zincati, en continu | uniquement dans le créneau (`strategy = "periodic"`) |
| `ucore` | `rpm-ostreed-automatic.timer` les prépare | `kiwi-staged-reboot.timer` dans le créneau |
| `debian` | unattended-upgrades, chaque jour | `kiwi-reboot-if-required.timer` dans le créneau, quand un redémarrage est nécessaire |

`updates.days: []` signifie n’importe quel jour, et `updates.enabled: false`
désactive le tout. Une machine chiffrée dont l’anneau Tang doit être transmis de
l’extérieur ne redémarre pas d’elle-même.

Les conteneurs ont leur propre calendrier : un `kiwi-stack update` hebdomadaire
(dimanche 00:00) lance `podman auto-update` tant que `auto_update: registry` est
réglé. Un redémarrage quotidien du client VPN à 07:00 donne une adresse de sortie
neuve.

## Sur la machine : `kiwi-stack` { #on-the-machine-kiwi-stack }

```bash
sudo kiwi-stack status          # conteneurs, unités de l’hôte, vérification
sudo kiwi-stack verify          # chaque conteneur tourne-t-il ?
sudo kiwi-stack logs [service]  # depuis le journal
sudo kiwi-stack start | stop | restart
sudo kiwi-stack update          # podman auto-update + prune
sudo kiwi-stack vpn-restart     # le client VPN et chaque conteneur de son espace de noms
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # avec le module backup
sudo kiwi-stack apply DIR       # un bundle de stack, sans script de rôle
```

La stack se trouve dans `docker_dir` (par défaut `/home/user/docker`), et ses
réglages dans `/etc/kiwi-server/stack.env`. Les unités sont `kiwi-stack.service`,
`kiwi-stack-vpn-restart.timer` et `kiwi-stack-update.timer`, plus celles qu’ajoute
un module.

## Ce que produit un rendu { #what-a-render-produces }

`output/<host>/` contient :

| Fichier | Contenu |
|---|---|
| `<host>.role.sh` | le rôle en un seul script : réglages, la stack (intégrée), la commande et la bibliothèque kiwi-stack, et le corps du rôle. Mode 0600 |
| `<host>.stack/` | le bundle de la stack, pour relecture : `docker-compose.yml`, `quadlets/`, configurations des modules, unités de l’hôte et `stack.sh`. `kiwi-stack apply` peut l’installer à la main |
| `<host>.bu`, `<host>.ign` | CoreOS et uCore : Butane et Ignition |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | Debian : le preseed et les fichiers qu’il copie |
| `<host>.iso` | l’installateur sans intervention |
