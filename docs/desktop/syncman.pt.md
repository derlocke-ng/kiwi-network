# syncman

Sincronização de pastas nos dois sentidos, aos pares, para Linux. Foi feito para
gravações de jogos e funciona com quaisquer pastas. **O rsync é a única
dependência** (o inotify-tools é opcional), e corre apenas no teu âmbito de
utilizador.

- Repositório: [derlocke-ng/syncman](https://github.com/derlocke-ng/syncman), GPL-3.0-or-later
- Versão mais recente: **v0.4.1**. Está no [catálogo Kiwi](catalogs.md), âmbito de utilizador.

Um **job** é um ficheiro de texto simples com um par por linha. Não há YAML nem
aspas, e os espaços nos caminhos funcionam sem mais:

```
# ~/.config/syncman/jobs/game-saves.job
~/Games/SomeGame/saves :: ~/Nextcloud/saves/SomeGame
```

Cada job corre como um serviço de utilizador systemd, `syncjob@<name>.service`. A
cada `INTERVAL` (30 segundos por omissão) corre `rsync -a --update` nos dois
sentidos: o ficheiro mais recente ganha, e **nunca nada é apagado**. Com o
`inotifywait` instalado, as alterações sincronizam de imediato.

```bash
kiwi install syncman            # ou ./install.sh
syncman add game-saves          # cria e edita um job
syncman start game-saves        # um serviço em segundo plano que sobrevive a reinícios
syncman list                    # os jobs e o estado dos seus serviços
syncman sync all                # uma só vez, sem serviço
syncman stop all
syncman log game-saves
syncman-panel                   # painel GTK4: um interruptor por job, botões de sincronizar agora
```

As definições estão em `~/.config/syncman/syncman.conf` (`INTERVAL` e,
opcionalmente, `JOBS_DIR`). Uma desinstalação mantém os teus jobs, a não ser que
passes `--purge`.
