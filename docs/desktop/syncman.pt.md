# syncman

O syncman mantém pares de pastas sincronizados nos dois sentidos numa máquina
Linux. Seja qual for a pasta do par que recebe um ficheiro novo ou alterado, o
ficheiro é copiado para a outra. O syncman foi feito para jogos guardados, mas
funciona com quaisquer pastas. **A única dependência é o rsync**, e o
inotify-tools é opcional. O syncman é instalado e corre apenas no âmbito de
utilizador, ou seja, na tua própria conta de utilizador.

- Repositório: [derlocke-ng/syncman](https://github.com/derlocke-ng/syncman), GPL-3.0-or-later
- Última versão: **v0.4.1**. Está no [catálogo Kiwi](catalogs.md), âmbito de utilizador.

Descreves o que queres sincronizar numa **tarefa** (job). Uma tarefa é um
ficheiro de texto simples com um par de pastas por linha. O formato não é YAML
e não precisa de aspas, por isso podes escrever tal e qual um caminho com
espaços:

```
# ~/.config/syncman/jobs/game-saves.job
~/Games/SomeGame/saves :: ~/Nextcloud/saves/SomeGame
```

Cada tarefa corre como um serviço de utilizador do systemd chamado
`syncjob@<name>.service`. A cada `INTERVAL`, que por predefinição é de 30
segundos, o serviço executa `rsync -a --update` nos dois sentidos. Quando um
ficheiro existe dos dois lados, o mais recente substitui o mais antigo, e
**nunca nada é apagado**. Se o `inotifywait` estiver instalado, as alterações
são sincronizadas assim que acontecem.

```bash
kiwi install syncman            # ou ./install.sh
syncman add game-saves          # criar e editar uma tarefa
syncman start game-saves        # um serviço em segundo plano que sobrevive a reinícios
syncman list                    # as tarefas e o estado dos respetivos serviços
syncman sync all                # uma única vez, sem serviço
syncman stop all
syncman log game-saves
syncman-panel                   # painel GTK4: um interruptor por tarefa, botões para sincronizar já
```

As definições estão em `~/.config/syncman/syncman.conf`. O ficheiro define o
`INTERVAL` e, opcionalmente, o `JOBS_DIR`. Quando desinstalas o syncman, as
tuas tarefas são mantidas, a não ser que uses `--purge`.
