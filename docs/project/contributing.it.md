# Contribuire

Tutto il progetto Kiwi Network è open source. Questa pagina ti dice dove va
ogni tipo di contributo. Apri issue e pull request nel repository a cui si
riferiscono. I repository sono elencati in
[Repository e stato](status.md).

- **Un’app per il catalogo.** Il catalogo è l’elenco delle app che
  kiwi-updater sa installare. Aggiungi alla tua app un `kiwi.manifest` e un
  `install.sh`, pubblica una release con un tag firmato e apri una pull
  request su [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). Vedi
  [Pubblicare un’app](../desktop/catalogs.md#publishing-an-app).
- **Un modulo.** I moduli si sviluppano in
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). Un modulo è una
  cartella con un `module.yaml` e dei template Jinja. Vedi
  [Scrivere un modulo](../server/modules.md#writing-a-module).
- **Un hub o un’app per un hub.** Fai un fork di
  [Armory](https://github.com/derlocke-ng/armory), crea lo scheletro di un’app
  con `npm run new-app` e aggiungi il tuo hub a
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog). Vedi
  [Gestire il tuo hub](../people/hubs.md).
- **Un provider per kiwi-proxy.** Un provider è un plugin che fornisce a
  kiwi-proxy un tipo di connessione, come Tor o una VPN. Ogni provider offre
  SOCKS5 e nient’altro. Le regole che un provider deve rispettare sono in
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md)
  di kiwi-proxy.
- **Questo sito e questa documentazione** si trovano nel repository
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## Documentare uno strumento Kiwi { #documenting-a-kiwi-tool }

Ogni strumento Kiwi è documentato nel suo repository. Il suo `README.md` è
breve: dice che cos’è lo strumento, come si installa e dove si trova il resto.
La documentazione completa sta nella sua cartella `docs/`. Questo sito mostra
per ogni strumento una pagina di panoramica tradotta e, sotto di essa, le
pagine della cartella `docs/` dello strumento, prese dalla sua ultima release.
Una correzione alla documentazione di uno strumento arriva quindi su questo
sito con la release successiva di quello strumento.

Come si scrivono un README e una cartella `docs/` lo spiega la guida
**kiwi-docs**: il tono, l’organizzazione dei file, come verificare ogni
affermazione sul codice, e uno script che controlla i link e la struttura. Il
codice sorgente della guida si trova in questo repository, in
[plugins/kiwi-docs](https://github.com/derlocke-ng/kiwi-network/tree/main/plugins/kiwi-docs/skills/kiwi-docs).
I repository degli strumenti ne contengono una copia in
`.claude/skills/kiwi-docs/`, così le sessioni di Claude Code in quei repository
la usano da sole. Quali repository questo sito include, e sotto quale pagina
compare ciascuno, è indicato in
[docs-sources.yml](https://github.com/derlocke-ng/kiwi-network/blob/main/docs-sources.yml).

## Questo repository { #this-repository }

Il repository kiwi-network contiene la homepage e questa documentazione:

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
docs/assets/   the logo and app icons (copied from kiwi-icons) and the docs' stylesheet
mkdocs.yml     docs configuration
```

Per vedere un’anteprima della documentazione e della homepage sul tuo
computer, esegui:

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # anteprima dal vivo su http://127.0.0.1:8000
mkdocs build --strict    # fallisce con link e ancore non validi
python -m http.server -d site 8080   # la homepage
```

Ciò che compila la CI contiene anche le pagine degli strumenti. Per compilare
questa versione, esegui:

```bash
python tools/pull-docs.py                      # la documentazione di questo repository più la cartella docs/ di ogni strumento
mkdocs build --strict -f build/mkdocs.yml      # il risultato si trova in build/docs/
```

Quando fai push su `main`, la homepage e la documentazione vengono pubblicate
tramite GitHub Pages.

Mantieni la documentazione **fedele ai repository**. Descrivi ciò che uno
strumento fa oggi, indica come previsto tutto ciò che è previsto, e per i
dettagli rimanda al codice sorgente invece di copiarli.
