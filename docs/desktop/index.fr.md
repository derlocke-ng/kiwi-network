# Le bureau

Les outils de bureau Kiwi sont conçus pour les **bureaux Fedora Atomic** : Fedora
Silverblue et [Bluefin](https://projectbluefin.io/) (Bluefin-DX en particulier). Ce
sont des systèmes à base d’images, avec un `/usr` immuable et un retour arrière
facile. Il n’y a pas d’image Kiwi spéciale : vous installez une image standard et
ajoutez trois couches par-dessus.

1. **[kiwi-updater](kiwi-updater.md)** installe et met à jour des applications
   depuis des catalogues git : tout dans votre répertoire personnel, plus une partie
   appartenant à root uniquement pour les applications qui en ont besoin. Il se met
   aussi à jour lui-même.
2. **[ensconce](ensconce.md)** configure un Bluefin-DX fraîchement installé à partir
   de simples fichiers de listes : paquets, Flatpaks, extensions GNOME,
   synchronisation Nextcloud, SSH, réglages sysctl et d’alimentation, l’écran de
   connexion et vos applications Kiwi. `--export` clone une machine.
3. **Les applications**, depuis le [catalogue Kiwi](catalogs.md) :

| Application | Ce qu’elle fait |
|---|---|
| [kiwi-killswitch](kiwi-killswitch.md) | Un kill switch VPN pour GNOME qui se ferme en cas de panne |
| [Réseaux clients](../clients/index.md) : kiwi-proxy, kiwi-custodia, kiwi-fox | Une sortie scellée par point d’accès VPN ou SOCKS, et des box de distributions et des navigateurs qui vivent à l’intérieur |
| [kiwi-server](../server/index.md) | Construire et faire tourner votre propre réseau |
| [gnome-monitor](gnome-monitor.md) | Enregistrer et changer de disposition d’écrans ; éteindre et rallumer des moniteurs un par un |
| [syncman](syncman.md) | Synchronisation bidirectionnelle de dossiers (sauvegardes de jeux et plus) en services utilisateur |
| [kiwi-cli-tools-desktop](cli-tools.md) | `pweb`, `select-server`, `tethering`, `torlink` |

Aussi ici : [kiwi-gen](kiwi-gen.md), un gestionnaire de clés et de certificats qui
tourne hors ligne dans le navigateur.

## Depuis une installation neuve { #from-a-fresh-install }

```bash
# 1. kiwi-updater : portée utilisateur et système, une seule demande de mot de passe ; le catalogue Kiwi est inclus
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
kiwi list

# 2. configurer la machine
kiwi install ensconce
ensconce --init && $EDITOR "$(ensconce --config-dir)"/settings.sh
ensconce

# 3. les applications voulues (ou listez-les dans le kiwi-apps.list d’ensconce)
kiwi install kiwi-killswitch
kiwi install kiwi-custodia && kiwi-custodia setup
```

**Kiwi Apps** (`kiwi-gui`) dans la grille d’applications fait la même chose en un
clic.

## Rejoindre votre réseau { #joining-your-network }

Un poste de bureau rejoint le maillage comme n’importe quel autre appareil :
`kiwi-server enroll fleet.yaml
laptop --group devices` écrit une configuration WireGuard, que vous importez dans
les Paramètres de GNOME. Importez l’autorité de certification de la fleet
(`kiwiCA.pem`) pour que ses noms HTTPS soient reconnus. ensconce installe chaque
`.pem` de son répertoire `certs/` pour tout le système.

[kiwi-killswitch](kiwi-killswitch.md) maintient ensuite la machine fermée en cas de
panne autour de cette connexion. Son réglage *trusted kiwi-nodes* permet à un node
gateway de votre LAN de remplacer le tunnel à la maison.
