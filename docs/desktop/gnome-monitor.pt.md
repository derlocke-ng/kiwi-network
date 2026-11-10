# gnome-monitor

Guarda e alterna disposições de ecrãs no GNOME (resolução, taxa de atualização
com VRR, posição, escala e ecrã principal por monitor), e **desliga e liga**
monitores individuais quando outro computador os usa. Uma CLI mais um
painel GTK4.

- Repositório: [derlocke-ng/gnome-monitor](https://github.com/derlocke-ng/gnome-monitor), GPL-3.0-or-later
- Versão mais recente: **v0.3.2**. Está no [catálogo Kiwi](catalogs.md), âmbito de utilizador.

Dois computadores, três ecrãs, uma secretária. Quando a outra máquina também
precisa do 4K, desliga-o aqui, trabalha, e volta a ligá-lo. Ele volta para onde
estava, no modo que tinha, como ecrã principal se o era. Ou guarda cada
disposição uma vez e aplica-a com um clique ou um atalho de teclado.

```bash
kiwi install gnome-monitor          # ou ./install.sh
```

```bash
gnome-monitor show                  # o que está ligado, ativo, onde, em que modo, com um mapa
gnome-monitor save desk             # a disposição atual como perfil "desk"
gnome-monitor list                  # perfis; * marca o que está em uso
gnome-monitor apply desk
gnome-monitor off rog               # um ecrã por conector, parte do nome, número ou "main"
gnome-monitor on rog
gnome-monitor only odyssey hp       # exatamente estes ligados, todos os outros desligados
gnome-monitor main odyssey
gnome-monitor mode rog 2560x1440@165
gnome-monitor shortcut desk super+1 # um atalho GNOME que aplica "desk"
gnome-monitor-panel                 # "Gnome Monitor" na grelha de aplicações
```

Fala com a API D-Bus `DisplayConfig` do Mutter, em Wayland e X11, sem root e sem
extensão. Os perfis são JSON em `~/.config/gnome-monitor/profiles/`, e os
monitores são identificados pelo seu EDID. As alterações aplicam-se
discretamente (ou pedem confirmação para serem mantidas, se preferires), e a disposição é reposta
no início de sessão. `--dry-run` pergunta ao Mutter se uma disposição é válida
sem a aplicar.
