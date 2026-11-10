---
hide:
  - toc
---

<div class="kiwi-hero" markdown>

![](assets/logo.svg)

<p class="kiwi-motto">Ex fructu arbor agnoscitur</p>

# Kiwi Network

<p class="kiwi-lede">Un environnement Linux open source que vous faites tourner vous-même : vos serveurs, vos appareils et votre poste de travail, réunis dans un seul réseau privé. Il s’installe tout seul, se tient à jour, fait une sauvegarde chaque nuit et peut être reconstruit quand quelque chose casse.</p>

[Comment ça marche](network/index.md){ .md-button .md-button--primary }
[Mettre en place un réseau](server/index.md){ .md-button }

</div>

<div class="kiwi-cards" markdown>

<a href="network/">
<strong>Le réseau</strong>
<span>Vos serveurs et vos appareils dans un seul réseau WireGuard privé. Un seul serveur est accessible depuis Internet, les autres restent chez vous.</span>
<em>Comment ça marche →</em>
</a>

<a href="server/">
<strong>kiwi-server</strong>
<span>L’outil avec lequel vous construisez et faites tourner le réseau : un seul fichier pour toutes les machines, l’installation automatique, les sauvegardes et le déverrouillage des disques.</span>
<em>Mettre en place un réseau →</em>
</a>

<a href="server/modules/">
<strong>Modules</strong>
<span>Les 20 services qu’une machine peut faire tourner, de WireGuard et Pi-hole à Nextcloud, Vaultwarden, les sauvegardes et Immich.</span>
<em>Ce qu’un node peut faire tourner →</em>
</a>

<a href="people/">
<strong>Hubs</strong>
<span>Avec kiwi-framework, une communauté fait tourner son propre hub, avec un marché ouvert, un fil et une messagerie, sans plateforme centrale.</span>
<em>Les hubs de communauté →</em>
</a>

<a href="desktop/">
<strong>Le poste de travail</strong>
<span>Un poste de travail Fedora Atomic dont les applications viennent de git : un kill switch pour le VPN, des connexions isolées pour les réseaux de vos clients, la configuration du poste et la synchronisation.</span>
<em>Les applications du poste →</em>
</a>

<a href="project/status/">
<strong>État du projet</strong>
<span>Tous les dépôts, avec leur version actuelle et ce qui manque encore.</span>
<em>Où en est le projet →</em>
</a>

</div>

## L’idée { #the-idea }

Internet est un milieu hostile, et s’occuper de ses propres serveurs est un
travail qui ne s’arrête jamais. Kiwi Network s’en charge à votre place. Vous
décrivez vos machines dans un seul fichier, le fichier fleet (`fleet.yaml`), et
les tâches courantes se font toutes seules. Les intrusions, les disques en
panne et les machines perdues sont prévus dès le départ.

- **Installation automatique.** Chaque machine est installée sans personne au
  clavier : à partir de sa propre image d’installation, ou directement sur un
  serveur loué, par l’API de l’hébergeur. netcup est pris en charge
  aujourd’hui, et d’autres hébergeurs sont
  [prévus](server/roadmap.md#more-hosters-and-network-boot).
- **Mises à jour automatiques.** Les mises à jour s’installent toutes seules.
  Une machine ne redémarre que pendant les heures que vous avez autorisées.
- **Une sauvegarde chaque nuit.** Chaque machine envoie une sauvegarde chiffrée
  à un serveur de sauvegarde qui vous appartient. Elle peut ajouter à ses
  sauvegardes, mais ne peut rien y supprimer. Un intrus ne peut donc pas les
  effacer. Le fichier fleet et ses secrets sont sauvegardés eux aussi.
- **La restauration, le jour où il le faut.** Les disques sont chiffrés. Au
  démarrage, les machines les déverrouillent toutes seules, ou bien vous les
  déverrouillez à distance. Une machine qu’il faut reconstruire retrouve sa
  configuration dans le fichier fleet et ses données dans la sauvegarde.

## Les machines { #the-machines }

Chaque machine a un rôle, et ce rôle détermine ce qu’elle fait dans le réseau.

| Rôle | Ce que fait la machine |
|---|---|
| `master` | La seule machine accessible depuis Internet. Elle fait tourner le serveur WireGuard, envoie le trafic sortant vers Internet par un fournisseur VPN ou directement, et fournit le DNS avec Pi-hole, Tor et les pages d’administration. Elle peut aussi héberger un relais nostr et un hub. |
| `node` · `gateway` | Fait passer un réseau domestique ou de bureau par le VPN, avec Pi-hole comme serveur DNS et DHCP, une station de téléchargement et SFTP. |
| `node` · `cloud` | Fait tourner Nextcloud avec Collabora, ainsi que Vaultwarden. |
| `node` · `minimal` | N’a que la connexion au réseau et nginx. Vous y ajoutez les modules que vous voulez, par exemple les sauvegardes, Tang, Immich, Paperless-ngx ou OpenCloud. |
| `bare` | Ne contient que le système de base. |

Les masters portent des noms de préparations à base de fruits (sorbet, crumble,
compote), et les nodes des noms de fruits (papaya, lychee, quince). Le master
est la seule machine qui doit être accessible depuis Internet. Par défaut, un
seul port y est ouvert : celui de WireGuard, UDP 51820.

```bash
kiwi install kiwi-server            # ou depuis un clone : ./install.sh install
kiwi-server init && $EDITOR fleet.yaml
kiwi-server build fleet.yaml        # une ISO par machine, qui s’installe sans intervention
kiwi-server apply fleet.yaml papaya # le rôle, par SSH
```
