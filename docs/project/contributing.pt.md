# Contribuir

Tudo no projeto Kiwi Network é software de código aberto. Esta página diz-te
para onde vai cada tipo de contribuição. Abre os issues e os pull requests no
repositório a que dizem respeito. A lista dos repositórios está em
[Repositórios e estado](status.md).

- **Uma aplicação para o catálogo.** O catálogo é a lista das aplicações que o
  kiwi-updater consegue instalar. Junta um `kiwi.manifest` e um `install.sh` à
  tua aplicação, publica-a com uma tag assinada e abre um pull request no
  [kiwi-catalog](https://github.com/derlocke-ng/kiwi-catalog). Vê
  [Publicar uma aplicação](../desktop/catalogs.md#publishing-an-app).
- **Um módulo.** Os módulos são desenvolvidos no
  [kiwi-modules](https://github.com/derlocke-ng/kiwi-modules). Um módulo é uma
  pasta com um `module.yaml` e modelos Jinja. Vê
  [Escrever um módulo](../server/modules.md#writing-a-module).
- **Um hub ou uma aplicação para um hub.** Faz um fork do
  [Armory](https://github.com/derlocke-ng/armory), cria o esqueleto de uma
  aplicação com `npm run new-app` e acrescenta o teu hub ao
  [kiwi-web-catalog](https://github.com/derlocke-ng/kiwi-web-catalog). Vê
  [O teu próprio hub](../people/hubs.md).
- **Um fornecedor para o kiwi-proxy.** Um fornecedor é um plugin que dá ao
  kiwi-proxy um tipo de ligação, como o Tor ou uma VPN. Todos os fornecedores
  disponibilizam SOCKS5 e mais nada. O contrato que um fornecedor tem de
  cumprir está no ficheiro
  [docs/plugin-system.md](https://github.com/derlocke-ng/kiwi-proxy/blob/main/docs/plugin-system.md)
  do kiwi-proxy.
- **Este site e esta documentação** estão no repositório
  [kiwi-network](https://github.com/derlocke-ng/kiwi-network).

## Este repositório { #this-repository }

O repositório kiwi-network contém a página inicial e esta documentação:

```
site/          the homepage: plain HTML, CSS and JS, served at kiwi-network.eu
site/icons/    the app icons it uses: mostly from kiwi-icons, some from the apps' own repos
docs/          this documentation (MkDocs Material), served at kiwi-network.eu/docs/
mkdocs.yml     docs configuration
```

Para veres a documentação e a página inicial no teu próprio computador, executa:

```bash
python -m pip install mkdocs-material mkdocs-static-i18n
mkdocs serve             # pré-visualização em direto em http://127.0.0.1:8000
mkdocs build --strict    # o que a CI constrói: falha se houver ligações ou âncoras partidas
python -m http.server -d site 8080   # a página inicial
```

Quando fazes push para `main`, a página inicial e a documentação são publicadas
através do GitHub Pages.

Por favor, mantém a documentação **fiel aos repositórios**. Descreve o que cada
ferramenta faz hoje, assinala como planeado tudo o que ainda só está planeado
e, para os pormenores, remete para o código-fonte em vez de os copiares.
