# gnome-monitor

O gnome-monitor guarda a disposição dos teus monitores no GNOME e alterna
entre as disposições guardadas. Uma disposição regista a resolução, a taxa de
atualização (incluindo a taxa de atualização variável, VRR), a posição e a
escala de cada monitor, e qual deles é o ecrã principal. O gnome-monitor
também consegue **desligar e voltar a ligar** um único monitor, o que dá jeito
quando outro computador está ligado ao mesmo monitor e precisa dele. Tem uma
ferramenta de linha de comandos e um painel GTK4.

- Repositório: [derlocke-ng/gnome-monitor](https://github.com/derlocke-ng/gnome-monitor), GPL-3.0-or-later
- Última versão: **v0.3.2**. Está no [catálogo Kiwi](catalogs.md), âmbito de utilizador.

Um caso típico é uma secretária com dois computadores e três ecrãs. Quando o
outro computador também precisa do monitor 4K, desligas esse monitor neste
computador e continuas a trabalhar nos restantes ecrãs. Quando o voltas a
ligar, ele regressa à posição e ao modo que tinha, e volta a ser o ecrã
principal se já o era antes. Também podes guardar cada disposição uma vez
como perfil e aplicá-la com um clique ou com um atalho de teclado.

```bash
kiwi install gnome-monitor          # ou ./install.sh
```

```bash
gnome-monitor show                  # o que está ligado, ativo, onde e em que modo, com um mapa
gnome-monitor save desk             # a disposição atual como perfil "desk"
gnome-monitor list                  # os perfis; * marca o que está em uso
gnome-monitor apply desk
gnome-monitor off rog               # um ecrã, pelo conector, parte do nome, número ou "main"
gnome-monitor on rog
gnome-monitor only odyssey hp       # exatamente estes ligados, todos os outros desligados
gnome-monitor main odyssey
gnome-monitor mode rog 2560x1440@165
gnome-monitor shortcut desk super+1 # um atalho do GNOME que aplica "desk"
gnome-monitor-panel                 # "Gnome Monitor" na grelha de aplicações
```

O gnome-monitor usa a API D-Bus `DisplayConfig` do Mutter, o gestor de janelas
do GNOME. Funciona em Wayland e em X11, e não precisa de permissões de root
nem de nenhuma extensão do GNOME. Os perfis são ficheiros JSON em
`~/.config/gnome-monitor/profiles/`. Cada monitor é reconhecido pelo seu
EDID, os dados de identificação que o próprio monitor comunica. Uma mudança de
disposição é aplicada sem pedido de confirmação. Se preferires, podes ativar
uma opção que pergunta se queres manter a nova disposição. A disposição é
reposta quando inicias sessão. Com `--dry-run`, o gnome-monitor pergunta ao
Mutter se uma disposição é válida, sem a aplicar.
