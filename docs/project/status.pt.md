# Repositórios e estado

Todos os repositórios vivem em [github.com/derlocke-ng](https://github.com/derlocke-ng).
«Lançado» significa uma tag de versão, que é o que o kiwi-updater instala. As
versões referem-se a novembro de 2026.

## A rede { #the-network }

| Repositório | O que é | Versão | Catálogo | Licença |
|---|---|---|---|---|
| [kiwi-server](https://github.com/derlocke-ng/kiwi-server) | construir e gerir a rede: ficheiro fleet → ISOs de instalação → aplicar por SSH | v2.42.0 | sim | GPL-3.0+ |
| [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules) | os 20 módulos e o seu renderizador: um ficheiro de máquina → um pacote de stack | v0.23.0 | não | GPL-3.0+ |
| [kiwi-stack](https://github.com/derlocke-ng/kiwi-stack) | o lado da máquina: põe um pacote numa máquina e mantém-no a correr | v0.5.0 | não | GPL-3.0+ |
| [mullvad-socks5](https://github.com/derlocke-ng/mullvad-socks5) | os proxies SOCKS5 da Mullvad como listas e registos DNS, reconstruídos a cada 6 horas | o ramo `list` | não | MIT (README) |

## Pessoas { #people }

| Repositório | O que é | Versão | Licença |
|---|---|---|---|
| [kiwi-framework](https://github.com/derlocke-ng/kiwi-framework) | o motor de hubs comunitários federados sobre nostr | v0.32.1 | GPL-3.0+ |
| [Armory](https://github.com/derlocke-ng/armory) | o primeiro hub: dez ferramentas web peer-to-peer ([ao vivo](https://derlocke-ng.github.io/armory/)) | segue `main` (0.1.0) | GPL-3.0+ |
| [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog) | um catálogo de hubs e das suas apps | (uma lista) | CC0 (README) |

## O ambiente de trabalho { #the-desktop }

| Repositório | O que é | Versão | Catálogo | Licença |
|---|---|---|---|---|
| [kiwi-updater](https://github.com/derlocke-ng/kiwi-updater) | instala e atualiza apps a partir de catálogos git | v2.4.0 | sim | GPL-3.0+ |
| [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog) | o catálogo de apps Kiwi | (uma lista) | n/a | nenhuma indicada |
| [ensconce](https://github.com/derlocke-ng/ensconce) | configuração pós-instalação para o Bluefin-DX | v2.5.0 | sim | GPL-3.0+ |
| [kiwi-killswitch](https://github.com/derlocke-ng/kiwi-killswitch) | kill switch de VPN fail-closed para o GNOME | v0.2.3 | sim | GPL-3.0+ |
| [kiwi-proxy](https://github.com/derlocke-ng/kiwi-proxy) | saídas SOCKS5/VPN seladas em Podman sem root | v0.7.3 | sim | GPL-3.0+ |
| [kiwi-custodia](https://github.com/derlocke-ng/kiwi-custodia) | distro boxes cujo tráfego só sai através de uma saída | v0.2.3 | sim | GPL-3.0+ |
| [kiwi-fox](https://github.com/derlocke-ng/kiwi-fox) | identidades de navegador isoladas em saídas do kiwi-proxy | v0.7.1 | sim | GPL-3.0+ |
| [kiwi-plugin-tor](https://github.com/derlocke-ng/kiwi-plugin-tor) | fornecedor do kiwi-proxy: Tor | v0.3.0 | sim | GPL-3.0+ |
| [kiwi-plugin-vpn](https://github.com/derlocke-ng/kiwi-plugin-vpn) | fornecedor do kiwi-proxy: uma VPN através do gluetun | v0.2.2 | sim | GPL-3.0+ |
| [kiwi-plugin-9proxy](https://github.com/derlocke-ng/kiwi-plugin-9proxy) | fornecedor do kiwi-proxy: 9proxy | v0.2.0 | sim | GPL-3.0+ |
| [kiwi-plugin-myst](https://github.com/derlocke-ng/kiwi-plugin-myst) | fornecedor do kiwi-proxy: Mysterium | v0.5.2 | sim | GPL-3.0+ |
| [gnome-monitor](https://github.com/derlocke-ng/gnome-monitor) | disposições de ecrãs para o GNOME | v0.3.2 | sim | GPL-3.0+ |
| [syncman](https://github.com/derlocke-ng/syncman) | sincronização de pastas nos dois sentidos como serviços de utilizador | v0.4.1 | sim | GPL-3.0+ |
| [kiwi-cli-tools-desktop](https://github.com/derlocke-ng/kiwi-cli-tools-desktop) | `pweb`, `select-server`, `tethering`, `torlink` | v1.2.1 | sim | GPL-3.0+ |
| [kiwi-gen](https://github.com/derlocke-ng/kiwi-gen) | chaves e certificados SSH e TLS, offline no navegador ([ao vivo](https://derlocke-ng.github.io/kiwi-gen/)) | página web | não | MIT |
| [kiwi-icons](https://github.com/derlocke-ng/kiwi-icons) | os ícones das apps ([pré-visualização](https://derlocke-ng.github.io/kiwi-icons/)) | sem tags | não | nenhuma indicada |
| [kiwi-network](https://github.com/derlocke-ng/kiwi-network) | este site e esta documentação | n/a | n/a | AGPL-3.0 |

## Lacunas conhecidas { #known-gaps }

Segundo os próprios repositórios:

- **kiwi-server**: comprovado em hardware em outubro–novembro de 2026, com
  cópias de segurança de nodes restauradas entre nodes e o MTU do túnel afinado,
  incluindo caminhos móveis. Vários servidores de cópias de segurança, o restauro
  automático de uma máquina reconstruída, um temporizador de limpeza e uma
  verificação de saúde para uma saída comercial bloqueada estão nos ramos
  `several-servers` do kiwi-server e do kiwi-modules, ainda não lançados. A
  federação entre redes ainda não está comprovada. Só IPv4, e a ISO Debian é só
  amd64. O plano de controlo está projetado, não construído.
- **kiwi-modules**: OpenCloud, Immich e Paperless-ngx estão «para experimentar».
  Um servidor TURN para chamadas está à espera de ser integrado.
- **kiwi-stack**: não há reversão para além de restaurar dados e voltar a aplicar
  um pacote mais antigo.
- **kiwi-framework**: o blogue, as aprovações de moderação, seguir espaços que um
  hub não traz e os signers NIP-07/NIP-46 ainda estão por vir.
- **kiwi-updater**: está planeado um registo alojado de catálogos de confiança. As
  tags de versão das outras apps ainda não são assinadas, por isso a metade root
  do kiwi-killswitch pede uma palavra-passe para se atualizar.
- **kiwi-proxy**: o seu módulo kiwi-server ainda não correu numa máquina. As
  saídas são só TCP e IPv4. O módulo VPN guarda uma configuração por máquina.
- **Módulos de fornecedores**: a VPN e o 9proxy não estão validados de ponta a
  ponta com uma conta real; o Mysterium está (7 de novembro de 2026).
- **kiwi-custodia**: algumas partes ainda têm de ser medidas numa máquina real
  (tun2socks num gateway sem root, compositores que não sejam GNOME).
- **Licenças**: o kiwi-icons, o kiwi-catalog e o mullvad-socks5 não têm ficheiro
  LICENSE, e o kiwi-killswitch só indica a sua licença no README e no manifesto.
