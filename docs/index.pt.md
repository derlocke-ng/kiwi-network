---
hide:
  - toc
---

<div class="kiwi-hero" markdown>

![](assets/logo.svg)

<p class="kiwi-motto">Ex fructu arbor agnoscitur</p>

# Kiwi Network

<p class="kiwi-lede">Um ambiente Linux de código aberto, gerido por ti: os teus servidores, os teus dispositivos e o teu computador de trabalho, todos numa única rede privada. Instala-se sozinho, mantém-se atualizado, faz um backup todas as noites e pode ser reconstruído quando alguma coisa se avaria.</p>

[Como funciona](network/index.md){ .md-button .md-button--primary }
[Criar a tua rede](server/index.md){ .md-button }

</div>

<div class="kiwi-cards" markdown>

<a href="network/">
<strong>A rede</strong>
<span>Os teus servidores e dispositivos numa única rede WireGuard privada. Só um servidor está acessível a partir da Internet, os restantes ficam em casa.</span>
<em>Como funciona →</em>
</a>

<a href="server/">
<strong>kiwi-server</strong>
<span>A ferramenta que constrói e gere a rede: um único ficheiro para todas as máquinas, instalação automática, backups e desbloqueio dos discos.</span>
<em>Criar uma rede →</em>
</a>

<a href="server/modules/">
<strong>Módulos</strong>
<span>Os 20 serviços que uma máquina pode correr, do WireGuard e do Pi-hole ao Nextcloud, ao Vaultwarden, aos backups e ao Immich.</span>
<em>O que um node pode correr →</em>
</a>

<a href="people/">
<strong>Hubs</strong>
<span>Com o kiwi-framework, uma comunidade gere o seu próprio hub, com um mercado aberto, um feed e um chat, sem depender de uma plataforma central.</span>
<em>Hubs de comunidades →</em>
</a>

<a href="desktop/">
<strong>O ambiente de trabalho</strong>
<span>Um posto de trabalho com Fedora Atomic e aplicações instaladas a partir do git: um kill switch para a VPN, ligações isoladas para as redes dos clientes, configuração do sistema e sincronização.</span>
<em>Aplicações para o ambiente de trabalho →</em>
</a>

<a href="project/status/">
<strong>Estado</strong>
<span>Todos os repositórios, com a versão atual de cada um e o que ainda falta.</span>
<em>Ponto da situação →</em>
</a>

</div>

## A ideia { #the-idea }

A Internet é uma selva, e manter os teus próprios servidores é um trabalho que
nunca acaba. A Kiwi Network faz esse trabalho por ti. Descreves as tuas
máquinas num único ficheiro, e as tarefas de rotina passam a correr sozinhas.
Intrusões, discos avariados e máquinas perdidas estão previstos desde o início.

- **Instalação automática.** Cada máquina é instalada sem ninguém ao teclado: a
  partir da sua própria imagem de instalação ou, num servidor alugado,
  diretamente através da API do fornecedor de alojamento. Hoje funciona com o
  netcup, e estão [planeados](server/roadmap.md#more-hosters-and-network-boot)
  outros fornecedores.
- **Atualizações automáticas.** As atualizações são instaladas sozinhas. Uma
  máquina só reinicia nas horas que tiveres autorizado.
- **Um backup todas as noites.** Cada máquina envia um backup cifrado para um
  servidor de backups que é teu. Pode acrescentar aos seus backups, mas não os
  pode apagar, por isso um intruso também não os consegue destruir. Também se
  faz backup do ficheiro fleet e dos respetivos segredos.
- **Recuperação quando é preciso.** Os discos são cifrados. As máquinas
  desbloqueiam-nos sozinhas quando arrancam, ou desbloqueia-los tu à
  distância. Se for preciso reconstruir uma máquina, a configuração vem do
  ficheiro fleet e os dados vêm do backup.

## As máquinas { #the-machines }

Cada máquina tem uma função, que define o que ela faz na rede.

| Função | O que a máquina faz |
|---|---|
| `master` | É a única máquina acessível a partir da Internet. Corre o servidor WireGuard, envia o tráfego de saída através de um fornecedor de VPN ou diretamente, e disponibiliza o DNS com Pi-hole, o Tor e as páginas de administração. Também pode correr um relay nostr e um hub. |
| `node` · `gateway` | Faz passar uma rede doméstica ou de escritório pela VPN, com o Pi-hole como servidor DNS e DHCP, um gestor de transferências e SFTP. |
| `node` · `cloud` | Corre o Nextcloud com o Collabora, e ainda o Vaultwarden. |
| `node` · `minimal` | Tem apenas a ligação à rede e o nginx. Os módulos acrescentas tu, por exemplo backups, Tang, Immich, Paperless-ngx ou OpenCloud. |
| `bare` | Tem apenas o sistema base. |

Os masters têm nomes de sobremesas de fruta (sorbet, crumble, compote) e os
nodes têm nomes de frutas (papaya, lychee, quince). O master é a única máquina
que precisa de estar acessível a partir da Internet. Por predefinição, tem uma
única porta aberta: a do WireGuard, UDP 51820.

```bash
kiwi install kiwi-server            # ou a partir de um clone: ./install.sh install
kiwi-server init && $EDITOR fleet.yaml
kiwi-server build fleet.yaml        # uma ISO por máquina, que se instala sem intervenção
kiwi-server apply fleet.yaml papaya # a função, por SSH
```
