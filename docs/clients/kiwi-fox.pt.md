# kiwi-fox

O kiwi-fox dá-te um navegador separado para cada rede de cliente em que
trabalhas e para cada conta que geres. O perfil que usas para um cliente
chega às consolas web dele através da ligação desse cliente e não tem mais
nenhum caminho para fora. Para isso, não precisas de nenhuma ligação VPN no
anfitrião.

Cada perfil é uma identidade persistente. Tem o seu próprio armazenamento,
corre um de três navegadores num contentor Podman rootless (um contentor que
corre como o teu próprio utilizador, sem permissões de root) e normalmente
usa um exit do [kiwi-proxy](kiwi-proxy.md). Um exit é uma ligação a um
upstream, guardada com um nome, como o proxy SOCKS5 de um cliente. Para cada
exit, o kiwi-proxy corre um gateway. O gateway é um contentor cuja única rota
leva a esse upstream, e inclui um resolvedor DNS que bloqueia domínios de
publicidade.

- Repositório: [derlocke-ng/kiwi-fox](https://github.com/derlocke-ng/kiwi-fox), GPL-3.0-or-later
- Última versão: **v0.7.1**. Está no [catálogo Kiwi](../desktop/catalogs.md), âmbito de utilizador.
- Os navegadores, a que o kiwi-fox chama motores, são descarregados para a tua
  máquina e nunca redistribuídos. O Camoufox (MPL-2.0) é descarregado durante
  a preparação inicial. O Firefox e o Tor Browser são descarregados quando os
  pedes (`kiwi-fox engine fetch`), e as assinaturas deles são verificadas.

| Motor | O que uma página vê |
|---|---|
| **Camoufox** (predefinição) | Uma máquina Windows 11 comum, com a sua própria região, em que todos os valores batem certo uns com os outros. Esta impressão digital (o conjunto de valores que uma página consegue ler de um navegador para o voltar a reconhecer) é falsificada e não muda |
| **Firefox** | O Mozilla Firefox sem alterações, que não falsifica nada. Uma página vê os valores reais desta máquina. A ligação continua a passar pelo exit do perfil |
| **Tor Browser** | O Tor Browser sem alterações, ligado através de um exit do módulo tor. Cada site tem o seu próprio circuito (o seu próprio caminho pela rede Tor), e os nomes `.onion` funcionam |

O kiwi-fox é para quem gere várias contas que lhe pertencem ou que está
autorizado a gerir, e não quer que essas contas fiquem associadas umas às
outras pela impressão digital do navegador ou pelo endereço IP.

## Instalação { #install }

```bash
kiwi install kiwi-fox      # traz o kiwi-proxy consigo; ou ./install.sh install
kiwi-fox setup             # imagens, um motor de navegador de ~630 MB, dados de DNS; corre também o setup do kiwi-proxy
kiwi-fox engine fetch --engine firefox     # ou torbrowser: com verificação de assinatura
```

O kiwi-fox precisa do Podman rootless, do kiwi-proxy, do Python 3.12+, do GTK4
com libadwaita e do `secret-tool`. Foi feito para uma sessão Wayland. O X11
também funciona, mas aí o isolamento é mais fraco. Para verificar o Firefox e
o Tor Browser, são necessários o `gpg`/`gpgv`. Com o controlador proprietário
da NVIDIA, o kiwi-fox precisa também do `nvidia-container-toolkit` com a
respetiva especificação CDI.

## Utilização { #use }

```bash
kiwi-proxy add client-a socks5://user:pass@host:1080   # um exit, definido uma vez, no kiwi-proxy
kiwi-fox new work --exit client-a     # um perfil nesse exit: testa-o e gera uma identidade que lhe corresponda
kiwi-fox new plain --no-proxy         # a ligação desta máquina, nada selado
kiwi-fox list                         # --tag shop, --by-tag
kiwi-fox run work                     # ou a aplicação gráfica
kiwi-fox stop work
kiwi-fox check                        # todos os perfis continuam coerentes?
kiwi-fox selfcheck work               # medir o que as páginas veem e depois verificar o resultado
kiwi-fox-gui                          # "Kiwi Fox" na grelha de aplicações
```

Com `--desktop-entry`, um perfil recebe uma entrada própria na grelha de
aplicações. As etiquetas permitem agrupar perfis.

## Perfis e exits { #profiles-and-exits }

Um perfil não tem um exit só seu. Limita-se a apontar para um, e vários
perfis podem apontar para o mesmo exit. Os perfis no mesmo exit partilham o gateway dele
e, com ele, um namespace de rede, o endereço IP com que aparecem na Internet e
um conjunto de circuitos Tor. Identidades que não podem partilhar um exit
precisam de exits diferentes. Um perfil criado com `--no-proxy` não tem
gateway. O contentor do navegador tem uma rede própria e usa a ligação desta
máquina. Nesse caso nada fica selado, ou seja, o tráfego não fica restrito a
uma única rota.

O contentor do navegador entra no namespace de rede do gateway. São-lhe
retiradas todas as capabilities do Linux, exceto `SYS_CHROOT`, de que a
própria sandbox do Firefox precisa. O contentor corre com
`no-new-privileges`, e o motor é montado só de leitura.

## Um perfil Camoufox { #a-camoufox-profile }

Um perfil Camoufox faz-se passar pela máquina mais comum que existe, porque os
sistemas de deteção assinalam os valores raros. Indica um ecrã de 1920×1080,
as fontes que todas as instalações do Windows 11 têm e nenhuma outra, e a
placa gráfica real desta máquina, com o nome que o Firefox no Windows lhe dá.
A região, a língua, o fuso horário e as vozes são escolhidos de acordo com o
exit. Podes alterar tudo isto mais tarde com `kiwi-fox set`, `kiwi-fox webgl`
e `kiwi-fox fonts`. Uma alteração só é guardada se o perfil continuar
coerente, ou seja, se os valores continuarem a bater certo uns com os outros.

## O que não faz { #what-it-does-not-do }

O kiwi-fox não promete que um perfil seja «indetetável». Os perfis estão
separados uns dos outros no armazenamento, no endereço IP e em todos os
valores que o motor consegue falsificar. **Não** estão separados nos
identificadores que vêm do hardware e que são iguais em todos os navegadores.
As imagens que a GPU desenha de facto e os tempos do hardware vêm da máquina
real, por isso são iguais em todos os perfis dessa máquina. O que foi medido
está documentado no ficheiro `docs/detection-notes.md` do repositório.

O kiwi-fox não tem automação. Não corre bots nem cria contas em massa. Foi
feito apenas para navegação interativa.
