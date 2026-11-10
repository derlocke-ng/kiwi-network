---
hide:
  - toc
---

<div class="kiwi-hero" markdown>

![](assets/logo.svg)

<p class="kiwi-motto">Ex fructu arbor agnoscitur</p>

# Kiwi Network

<p class="kiwi-lede">A tua própria rede privada: um master à porta, nodes atrás dele, todas as máquinas tuas. Construída a partir de um só ficheiro, com uma só porta para a Internet.</p>

[Como funciona](network/index.md){ .md-button .md-button--primary }
[Construir uma](server/index.md){ .md-button }

</div>

<div class="kiwi-cards" markdown>

<a href="network/">
<strong>A rede</strong>
<span>Um master, muitos nodes, uma malha WireGuard. Grupos de clientes, uma saída de salto duplo, DNS e certificados próprios.</span>
<em>Como funciona →</em>
</a>

<a href="server/">
<strong>kiwi-server</strong>
<span>O ficheiro fleet, ISOs de instalação, aplicar por SSH, inscrição, cópias de segurança, desbloqueio. CLI e app GTK.</span>
<em>Construir uma rede →</em>
</a>

<a href="server/modules/">
<strong>Módulos</strong>
<span>Todos os 20: WireGuard, Pi-hole, Tor, Nextcloud, Vaultwarden, cópias de segurança, Tang, Immich, Paperless-ngx e mais.</span>
<em>O que um node pode ser →</em>
</a>

<a href="people/">
<strong>Hubs</strong>
<span>kiwi-framework: mercados abertos, feeds, chat e partilha sobre nostr, selados no navegador. O Armory é o primeiro.</span>
<em>Hubs, não plataformas →</em>
</a>

<a href="desktop/">
<strong>O ambiente de trabalho</strong>
<span>O kiwi-updater e as apps para Fedora Atomic: kill switch, saídas seladas para redes de clientes, configuração, sincronização.</span>
<em>Apps a partir do git →</em>
</a>

<a href="project/status/">
<strong>Estado</strong>
<span>Cada repositório, a sua versão e as suas lacunas conhecidas, descritos tal como estão.</span>
<em>Em que ponto estão as coisas →</em>
</a>

</div>

## A ideia { #the-idea }

A Kiwi Network é um ambiente Linux totalmente automatizado para viver e
trabalhar: seguro, sólido e protegido para uma vida online dura. As tuas
máquinas tratam de si próprias.

- **Instalam-se sozinhas.** Uma ISO sem intervenção por máquina, ou diretamente
  num servidor alugado através da API do fornecedor (hoje a netcup, outros
  [planeados](server/roadmap.md#more-hosters-and-network-boot)).
- **Mantêm-se atualizadas sozinhas.** As atualizações instalam-se continuamente,
  e os reinícios esperam pela janela que definires.
- **Fazem as suas próprias cópias de segurança.** Todas as noites, cifradas e
  apenas em modo de acrescento, para nodes de cópias de segurança teus. O
  ficheiro fleet e os seus segredos também têm cópia de segurança.
- **Voltam a pôr-se de pé.** Os discos cifrados desbloqueiam-se através do Tang,
  ou remotamente quando algo corre mal, e uma máquina reconstruída regressa a
  partir do ficheiro fleet e da sua cópia de segurança.

## As máquinas { #the-machines }

| Papel | O que a máquina passa a ser |
|---|---|
| `master` | a porta: WireGuard, uma saída de salto duplo ou direta, Pi-hole, Tor, as páginas de administração e, opcionalmente, um relay nostr e um hub |
| `node` · `gateway` | uma LAN através da VPN, com o Pi-hole como DNS e DHCP, uma estação de transferências e SFTP |
| `node` · `cloud` | Nextcloud com Collabora, e Vaultwarden |
| `node` · `minimal` | o túnel e o nginx, para módulos à tua escolha: cópias de segurança, Tang, Immich, Paperless-ngx, OpenCloud |
| `bare` | apenas o sistema base |

Os masters têm nomes de pratos de fruta (sorbet, crumble, compote) e os nodes
nomes de frutos (papaya, lychee, quince). O master é a única máquina que tem de
estar acessível a partir da Internet e, por omissão, publica uma porta: WireGuard,
UDP 51820.

```bash
kiwi install kiwi-server            # ou a partir de um clone: ./install.sh install
kiwi-server init && $EDITOR fleet.yaml
kiwi-server build fleet.yaml        # uma ISO sem intervenção por máquina
kiwi-server apply fleet.yaml papaya # o papel, por SSH
```
