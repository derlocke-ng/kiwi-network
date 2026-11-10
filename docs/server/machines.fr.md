# Machines : installation, apply, mises à jour

Cette page suit une machine depuis son entrée dans le fichier fleet jusqu’à un
système en fonctionnement qui se met à jour tout seul. kiwi-server construit
une image d’installation qui installe le système d’exploitation sans personne
au clavier. Il configure ensuite la machine pour son rôle, par SSH, avec la
commande `apply`. Par la suite, la machine installe elle-même ses mises à jour
et ne redémarre qu’aux heures que vous avez autorisées.

## Systèmes cibles { #targets }

Le système cible (`target`) est le système d’exploitation que kiwi-server
installe sur une machine.

| Système cible | Ce qui est installé | Support d’installation |
|---|---|---|
| `coreos` | Fedora CoreOS, branche stable | L’ISO live officielle, adaptée avec la configuration Ignition de l’hôte (Butane `fcos` 1.6.0). L’installation n’a besoin d’aucune connexion réseau |
| `ucore` | Fedora CoreOS, qui bascule ensuite de lui-même (rebase) vers une image `ghcr.io/ublue-os/ucore*`. Les images disponibles sont `ucore-minimal`, `ucore` et `ucore-hci`, aussi en variantes `-nvidia` / `-zfs`. Le rebase fonctionne comme l’exemple d’autorebase fourni par uCore | Le même que pour CoreOS, avec en plus les unités d’autorebase |
| `debian` | Debian stable (trixie), amd64 | L’image netinst officielle, avec dans son initrd le fichier preseed (qui contient les réponses destinées à l’installateur) : l’installateur a ainsi ses réponses dès la première question. Les fichiers de l’hôte se trouvent sur l’image sous `/kiwi-server`. L’image démarre toujours en BIOS comme en UEFI |

Sur tous les systèmes cibles, l’utilisateur admin peut utiliser sudo sans mot
de passe. SSH n’accepte que les clés, sauf si vous définissez
`ssh_password_auth: true`.

## Supports d’installation { #install-media }

La première commande construit l’image d’installation (ISO) d’un hôte. La
seconde la copie sur une clé USB.

```bash
kiwi-server build fleet.yaml sorbet      # → output/sorbet/sorbet.iso
sudo dd if=output/sorbet/sorbet.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

- L’ISO s’installe sur le disque indiqué dans `disk:` **sans rien demander**,
  ce qui efface ce disque. Une fois l’installation terminée, elle **éteint la
  machine** (`install.on_done: poweroff`, ou `reboot` pour la redémarrer à la
  place). Étiquetez vos clés USB.
- Par défaut, le support d’installation ne contient **que le système de
  base** : le nom d’hôte, les réglages réseau, l’utilisateur admin avec ses
  clés SSH et la politique de mises à jour. Il ne contient aucun des secrets de
  la stack. La machine reçoit son rôle plus tard, lorsque vous lancez `apply`.
- Avec `--offline`, tout le rôle et ses secrets sont placés sur l’ISO. Cette
  option est destinée à une machine qui n’est pas joignable par SSH. Quiconque
  possède cette ISO possède aussi ces secrets.
- L’installateur live liste les disques de la machine (`lsblk`) et propose un
  shell, qui accepte le mot de passe console et les clés SSH définis dans le
  fichier fleet.

## Apply { #apply }

`apply` configure une machine pour son rôle, par SSH.

```bash
kiwi-server apply fleet.yaml papaya                         # par nom, adresse ou adresse mesh
kiwi-server apply fleet.yaml papaya --ssh core@192.168.1.25 # la première fois, par adresse
```

`apply` commence par générer de nouveau les fichiers de l’hôte à partir du
fichier fleet. Il copie ensuite par SSH le script de rôle
de l’hôte vers `/var/lib/kiwi-server/role.sh`. Le script de rôle est le script
qui configure la machine pour son rôle, et `apply` l’exécute en root. Ensuite,
`apply` lie le disque à ses anneaux Tang, des serveurs qui permettent à
une machine chiffrée de déverrouiller son disque au démarrage. Sur un master,
il sauvegarde aussi l’état de WireGuard avec les secrets du réseau. Sur une
machine Debian chiffrée, le premier `apply` remplace la clé à usage unique qui a
servi à l’installation.

La connexion SSH utilise la clé propre au réseau et compare la clé d’hôte de
la machine à `secrets/known_hosts`. `apply` et `status` peuvent joindre une
machine par son nom, par son adresse statique, par l’adresse publique du
master ou par son adresse mesh, c’est-à-dire l’adresse de la machine dans le
réseau WireGuard privé. Ils n’utilisent qu’une adresse dont la clé d’hôte est
déjà enregistrée.

Pour un rôle construit à partir de modules, le script de rôle transmet la
stack à `kiwi-stack`. La stack est l’ensemble des conteneurs que la machine
fait tourner pour ses modules. `kiwi-stack` effectue alors les étapes
suivantes :

1. Il installe ou active podman 4.4+ ou docker, et s’assure que l’utilisateur
   de service existe. Sous Debian, podman est installé avec `netavark`,
   `aardvark-dns` et `catatonit`.
2. Il charge des modules du noyau et définit des sysctls. Si la stack contient
   Pi-hole, l’aardvark-dns de podman est déplacé sur le port 5533, et l’hôte
   lui-même résout les noms par le Pi-hole de la stack. Il ajoute aussi le mesh
   aux réseaux auxquels firewalld fait confiance.
3. Il refuse une stack générée avec un autre seed. Le seed est le secret à
   partir duquel sont générés les mots de passe du réseau. Sinon, il décompresse
   la stack dans `docker_dir`. Il installe les quadlets, c’est-à-dire les
   unités systemd des conteneurs, dans `/etc/containers/systemd`, ainsi que
   les unités de l’hôte. Il supprime aussi tout ce qu’avait installé un module
   qui ne fait plus partie de la stack.
4. Il ouvre les ports de la stack dans firewalld ou ufw, si l’un des deux est
   actif.
5. Il télécharge toutes les images de conteneurs, puis démarre
   `kiwi-stack.service`, qui démarre `kiwi-stack.target`.
6. Il lance `kiwi-stack verify`, qui vérifie que chaque conteneur tourne. Si
   l’un d’eux ne tourne pas, l’`apply` échoue et indique l’étape en cause.

Si vous appliquez de nouveau la même configuration générée, rien ne change sur
la machine. Si vous appliquez une nouvelle configuration générée, elle remplace
ce qui a changé. Notez que chaque `apply` redémarre tous les conteneurs de la
stack, même quand rien n’a changé.

## Premier démarrage { #first-boot }

Au premier démarrage, `kiwi-role.service` exécute une fois le script de rôle
`/var/lib/kiwi-server/role.sh`. Ce service démarre une fois le réseau en
place et attend jusqu’à 120 secondes que le DNS réponde. Le fichier `role.done` indique que le rôle
est terminé, et il n’est écrit que lorsque tous les conteneurs tournent. Si le
script échoue, il laisse le fichier `/var/lib/kiwi-server/role.failed`, qui
indique l’étape et la commande qui ont échoué, et le script est relancé au
démarrage suivant. Le journal se trouve dans `/var/log/kiwi-server-role.log`.
Sous uCore, le script de rôle attend que la machine tourne sur l’image uCore
signée. Pour relancer le script à la main, utilisez
`sudo bash /var/lib/kiwi-server/role.sh --force`.

## Mises à jour { #updates }

Les machines installent en continu les mises à jour de leur système
d’exploitation. Le **redémarrage** qui active ces mises à jour n’a lieu que
pendant la fenêtre de maintenance que vous fixez avec `updates.days`, `time` et
`length_minutes`, en heure locale.

| Système cible | Installation des mises à jour | Redémarrage |
|---|---|---|
| `coreos` | Zincati, en continu | uniquement dans la fenêtre (`strategy = "periodic"`) |
| `ucore` | `rpm-ostreed-automatic.timer` les télécharge et les prépare (staging) | `kiwi-staged-reboot.timer`, dans la fenêtre |
| `debian` | unattended-upgrades, chaque jour | `kiwi-reboot-if-required.timer`, dans la fenêtre, si une mise à jour exige un redémarrage |

`updates.days: []` autorise le redémarrage n’importe quel jour, et
`updates.enabled: false` désactive les mises à jour et les redémarrages. Une
machine chiffrée ne redémarre pas d’elle-même si elle a besoin d’un anneau Tang
que quelqu’un doit lui relayer à la main. Sinon, elle resterait bloquée au
démarrage jusqu’à ce que quelqu’un la déverrouille.

Les conteneurs sont mis à jour selon leur propre calendrier. Une fois par
semaine, le dimanche à 00:00, `kiwi-stack update` lance `podman auto-update`, à
condition que `auto_update: registry` soit défini. Le client VPN est redémarré
chaque jour à 07:00, ce qui lui donne une nouvelle adresse de sortie. L’adresse
de sortie est l’adresse publique que voient les sites web lorsque le trafic
sort du VPN.

## Sur la machine : `kiwi-stack` { #on-the-machine-kiwi-stack }

`kiwi-stack` est la commande à lancer sur la machine elle-même pour examiner
la stack et la piloter.

```bash
sudo kiwi-stack status          # conteneurs, unités de l'hôte, vérification
sudo kiwi-stack verify          # tous les conteneurs tournent-ils ?
sudo kiwi-stack logs [service]  # depuis le journal
sudo kiwi-stack start | stop | restart
sudo kiwi-stack update          # podman auto-update + prune
sudo kiwi-stack vpn-restart     # le client VPN et tous les conteneurs de son namespace
sudo kiwi-stack backup | snapshots | restore [--at TIME] MODULE...   # avec le module backup
sudo kiwi-stack apply DIR       # un paquet de stack, sans script de rôle
```

Les fichiers de la stack se trouvent dans `docker_dir` (par défaut
`/home/user/docker`), et ses réglages dans `/etc/kiwi-server/stack.env`. Les
unités systemd sont `kiwi-stack.service`, `kiwi-stack-vpn-restart.timer` et
`kiwi-stack-update.timer`, plus les unités qu’un module ajoute.

## Ce que produit la génération { #what-a-render-produces }

La configuration générée est ce que kiwi-server produit pour un hôte à partir
du fichier fleet. Elle est écrite dans `output/<host>/`, qui contient alors les
fichiers suivants.

| Fichier | Contenu |
|---|---|
| `<host>.role.sh` | Le rôle sous forme d’un script unique. Il contient les réglages, la stack intégrée, la commande et la bibliothèque kiwi-stack, et le corps du rôle. Le fichier a les droits 0600 |
| `<host>.stack/` | Le paquet de la stack, pour que vous puissiez l’examiner. Il contient `docker-compose.yml`, `quadlets/`, les fichiers de configuration des modules, les unités de l’hôte et `stack.sh`. Vous pouvez aussi l’installer à la main avec `kiwi-stack apply` |
| `<host>.bu`, `<host>.ign` | Sous CoreOS et uCore, la configuration Butane et Ignition |
| `<host>.preseed.cfg`, `<host>.kiwi-server/` | Sous Debian, le fichier preseed et les fichiers qu’il copie sur la machine |
| `<host>.iso` | L’image d’installation, qui s’installe sans personne au clavier |
