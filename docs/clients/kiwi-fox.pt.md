# kiwi-fox

Identidades de navegador isoladas em Podman sem root.

Cada perfil é uma identidade persistente: o seu próprio armazenamento e,
normalmente, uma saída do [kiwi-proxy](kiwi-proxy.md) com o seu gateway selado e
um resolvedor com bloqueio de anúncios, num de três navegadores. Para uma rede de
cliente, isso significa um navegador que chega às consolas web do cliente
através da saída do cliente, e a mais nada.

- Repositório: [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Versão mais recente: **v0.7.1**. Está no [catálogo Kiwi](../desktop/catalogs.md), âmbito de utilizador.
- Os motores são descarregados, nunca redistribuídos: o Camoufox (MPL-2.0) na
  configuração inicial, o Firefox e o Tor Browser a pedido
  (`kiwi-fox engine fetch`), com a assinatura verificada.

| Motor | O que uma página vê |
|---|---|
| **Camoufox** (por omissão) | uma máquina Windows 11 coerente e comum, com a sua própria região: uma impressão digital congelada e falsificada |
| **Firefox** | o Mozilla Firefox de origem, sem falsificar nada: os valores desta máquina, através da mesma saída selada |
| **Tor Browser** | o Tor Browser, sem modificações, através de uma saída do módulo tor, com um circuito por site e nomes `.onion` |

O kiwi-fox é para quem gere várias contas que são suas ou que está autorizado a
gerir, e que não quer que essas contas fiquem ligadas entre si pela impressão
digital do navegador ou pelo IP.

## Instalar { #install }

```bash
kiwi install kiwi-fox      # traz consigo o kiwi-proxy; ou ./install.sh install
kiwi-fox setup             # imagens, um motor de navegador de ~630 MB, dados DNS; também corre o setup do kiwi-proxy
kiwi-fox engine fetch --engine firefox     # ou torbrowser: com a assinatura verificada
```

Precisa de Podman sem root e do kiwi-proxy, de uma sessão Wayland (o X11
funciona, com uma fronteira mais fraca), de Python 3.12+, GTK4 + libadwaita,
`secret-tool`, e de `gpg`/`gpgv` para verificar o Firefox e o Tor Browser. Com o
driver proprietário da NVIDIA, precisa também do `nvidia-container-toolkit` com a
sua especificação CDI.

## Usar { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # uma saída, definida uma vez, no kiwi-proxy
kiwi-fox new work --exit client-a     # um perfil nela: testa-a e gera uma identidade que lhe corresponde
kiwi-fox new plain --no-proxy         # a ligação desta máquina, nada selado
kiwi-fox list                         # --tag shop, --by-tag
kiwi-fox run work                     # ou a app
kiwi-fox stop work
kiwi-fox check                        # todos os perfis continuam coerentes?
kiwi-fox selfcheck work               # mede o que as páginas veem e depois audita-o
kiwi-fox-gui                          # "Kiwi Fox" na grelha de aplicações
```

`--desktop-entry` põe um perfil na grelha de aplicações, e as etiquetas agrupam
perfis.

## Perfis e saídas { #profiles-and-exits }

Um perfil referencia uma saída, e as saídas são partilhadas: os perfis numa saída
partilham o seu gateway (um namespace, um IP de saída, um conjunto de circuitos
Tor). As identidades que não devem partilhar uma saída usam saídas diferentes.
Com `--no-proxy` não há gateway: o contentor do navegador tem uma rede própria
na ligação desta máquina, e nada fica selado.

O contentor do navegador junta-se ao namespace do gateway com todas as
capabilities retiradas exceto `SYS_CHROOT` (a própria sandbox do Firefox precisa
dela). Corre com `no-new-privileges`, e o motor é montado só de leitura.

## Um perfil Camoufox { #a-camoufox-profile }

É a máquina mais comum que existe, porque são os valores raros que os detetores
assinalam: um ecrã de 1920×1080, os tipos de letra que todos os Windows 11 têm e
mais nenhuns, e a placa gráfica desta máquina tal como o Firefox no Windows a
descreve. A região, a língua, o fuso horário e as vozes seguem a saída. Tudo pode
ser alterado depois (`kiwi-fox set`, `kiwi-fox webgl`, `kiwi-fox fonts`), e as
edições só são guardadas se o resultado continuar coerente.

## O que não faz { #what-it-does-not-do }

Não promete ser «indetetável». Os perfis estão isolados quanto ao armazenamento,
ao IP e a todas as superfícies que o motor consegue falsificar, mas **não**
contra identificadores entre navegadores ao nível do hardware: as imagens que a
GPU de facto desenha e as temporizações do hardware vêm da máquina real e são as
mesmas para todos os perfis nela. O `docs/detection-notes.md` do repositório
documenta o que é medido.

Não há automação: nem bots nem criação de contas em massa. É apenas para
navegação interativa.
