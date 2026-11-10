# Repositórios e estado

Esta página reúne todos os repositórios do projeto Kiwi Network: o que é cada
um, qual é a última versão e qual é a licença. No fim, enumera o que se sabe
que ainda falta ou ainda não foi testado.

Todos os repositórios estão em [github.com/derlocke-ng](https://github.com/derlocke-ng).
Um repositório conta como «publicado» quando tem uma tag de versão, porque é a
tag de versão que o kiwi-updater instala. As versões indicadas são as de
novembro de 2026.

## A rede { #the-network }

| Repositório | O que é | Versão | Catálogo | Licença |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | constrói e gere a rede: gera ISOs de instalação a partir do ficheiro fleet e aplica a função de cada máquina por SSH | v2.42.0 | sim | GPL-3.0+ |
| [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) | os 20 módulos e o programa que os gera, que transforma o ficheiro de uma máquina num pacote com a sua stack | v0.23.0 | não | GPL-3.0+ |
| [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) | a parte que corre na própria máquina: instala lá um pacote e mantém-no a funcionar | v0.5.0 | não | GPL-3.0+ |
| [mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5) | listas e registos DNS dos proxies SOCKS5 da Mullvad, refeitos de 6 em 6 horas | o ramo `list` | não | MIT (README) |

## Pessoas { #people }

| Repositório | O que é | Versão | Licença |
|---|---|---|---|
| [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework) | o framework com que se constroem hubs comunitários federados sobre nostr | v0.32.1 | GPL-3.0+ |
| [Armory](https://github.com/derlocke-ng/armory) | o primeiro hub feito com o kiwi-framework, com dez ferramentas web peer-to-peer ([ao vivo](https://derlocke-ng.github.io/armory/)) | acompanha o `main` (0.1.0) | GPL-3.0+ |
| [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) | um catálogo de hubs e das suas aplicações | (uma lista) | CC0 (README) |

## O desktop { #the-desktop }

| Repositório | O que é | Versão | Catálogo | Licença |
|---|---|---|---|---|
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | instala e atualiza aplicações a partir de catálogos git | v2.4.0 | sim | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | o catálogo de aplicações Kiwi | (uma lista) | n/a | não indicada |
| [ensconce](https://github.com/derlocke-ng/ensconce) | configura o Bluefin-DX depois de instalado | v2.5.0 | sim | GPL-3.0+ |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | um kill switch de VPN fail-closed para o GNOME: quando a ligação VPN cai, o tráfego fica bloqueado | v0.2.3 | sim | GPL-3.0+ |
| [kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy) | exits SOCKS5 e VPN em Podman rootless, cada um fechado num contentor cuja única rota é essa ligação | v0.7.3 | sim | GPL-3.0+ |
| [kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia) | boxes com distribuições Linux (em contentores) cujo tráfego só chega à Internet através de um exit do kiwi-proxy | v0.2.3 | sim | GPL-3.0+ |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | identidades de navegador isoladas, que se ligam através de exits do kiwi-proxy | v0.7.1 | sim | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | fornecedor para o kiwi-proxy: Tor | v0.3.0 | sim | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | fornecedor para o kiwi-proxy: uma VPN através do gluetun | v0.2.2 | sim | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | fornecedor para o kiwi-proxy: 9proxy | v0.2.0 | sim | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | fornecedor para o kiwi-proxy: Mysterium | v0.5.2 | sim | GPL-3.0+ |
| [gnome-monitor](https://github.com/derlocke-ng/gnome-monitor) | disposições dos ecrãs para o GNOME | v0.3.2 | sim | GPL-3.0+ |
| [syncman](https://github.com/derlocke-ng/syncman) | sincronização de pastas nos dois sentidos, a correr como serviços de utilizador do systemd | v0.4.1 | sim | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering`, `torlink` | v1.2.1 | sim | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | cria chaves e certificados SSH e TLS no navegador, sem ligação à rede ([ao vivo](https://derlocke-ng.github.io/kiwi-gen/)) | página web | não | MIT |
| [kiwi-icons](https://github.com/derlocke-ng/kiwi-icons) | os ícones das aplicações ([pré-visualização](https://derlocke-ng.github.io/kiwi-icons/)) | sem tags | não | não indicada |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | este site e esta documentação | n/a | n/a | AGPL-3.0 |

## Lacunas conhecidas { #known-gaps }

Os próprios repositórios apontam estas lacunas:

- **kiwi-server**: Ficou demonstrado que funciona em hardware real, em
  outubro e novembro de 2026. Nesses testes, os backups de um node foram
  restaurados noutro node, e a MTU do túnel foi afinada, incluindo para ligações
  móveis. Há quatro acrescentos nos ramos `several-servers` do kiwi-server e do
  kiwi-modules que ainda não foram publicados: vários servidores de backups, o
  restauro automático de uma máquina reconstruída, um temporizador para eliminar
  os snapshots antigos e uma verificação de estado que reinicia a ligação ao
  fornecedor de VPN comercial quando esta fica bloqueada. Ainda não ficou
  demonstrado que a federação entre redes funciona. Tudo funciona apenas com
  IPv4, e a ISO de Debian só existe para amd64. O plano de controlo está
  concebido, mas ainda não implementado.
- **kiwi-modules**: Os módulos OpenCloud, Immich e Paperless-ngx estão marcados
  como «para experimentar». Um servidor TURN para chamadas está à espera de ser
  integrado.
- **kiwi-stack**: Não há forma de reverter para uma versão anterior. Só podes
  restaurar os dados e voltar a aplicar um pacote mais antigo.
- **kiwi-framework**: Ainda faltam várias partes: o blogue, a aprovação na
  moderação, seguir espaços que um hub não traz incluídos e os signers
  NIP-07/NIP-46.
- **kiwi-updater**: Está planeado um registo alojado de catálogos de confiança.
  As tags de versão das outras aplicações ainda não são assinadas. É por isso
  que a parte do kiwi-killswitch que corre como root pede uma palavra-passe
  quando é atualizada.
- **kiwi-proxy**: O seu módulo para o kiwi-server ainda não correu em nenhuma
  máquina. Os exits só transportam TCP e IPv4. O módulo de VPN guarda uma única
  configuração por máquina.
- **Módulos de fornecedor**: Os módulos de VPN e de 9proxy ainda não foram
  validados de ponta a ponta com uma conta real. O módulo da Mysterium foi
  validado a 7 de novembro de 2026.
- **kiwi-custodia**: Há partes que ainda têm de ser medidas numa máquina real:
  o tun2socks num gateway rootless e os compositores que não sejam o GNOME.
- **Licenças**: O kiwi-icons, o kiwi-catalog e o mullvad-socks5 não têm ficheiro
  LICENSE, e o kiwi-killswitch só indica a licença no README e no manifest.
