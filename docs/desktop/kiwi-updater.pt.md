# kiwi-updater

O kiwi-updater instala aplicações de código aberto no teu computador e
mantém-nas atualizadas. O comando chama-se `kiwi`. Vai buscar as aplicações a
**catálogos git**. Um catálogo é um repositório git com uma lista de
aplicações, e uma aplicação é um repositório git com um ficheiro
`kiwi.manifest` e um script `install.sh`. O kiwi clona a aplicação, faz
checkout da tag de versão mais recente e corre o instalador. A partir daí,
atualiza a aplicação em segundo plano, e atualiza-se a si próprio da mesma
forma.

Não precisas de conta, e não há loja de aplicações nem empresa por trás. Um
catálogo é um repositório que podes ler, de que podes fazer fork e para o qual
podes enviar pull requests. Todas as aplicações Kiwi para o ambiente de
trabalho são instaladas desta forma.

- Repositório: [derlocke-ng/kiwi-updater](https://github.com/derlocke-ng/kiwi-updater), GPL-3.0-or-later
- Última versão: **v2.5.1**
- **`kiwi`** é a ferramenta de linha de comandos. **Kiwi Apps** (`kiwi-gui`) é
  a aplicação gráfica. Nela podes explorar e pesquisar as aplicações,
  instalá-las e ler o instalador de uma aplicação antes de ele correr.

## Onde funciona { #where-it-runs }

O kiwi-updater foi feito para as variantes gráficas do Fedora Atomic e agora
funciona também noutras distribuições Linux. Cada alteração ao kiwi-updater é
testada nestes sistemas, com o conjunto completo de testes e com uma instalação
real:

| Sistema | O que funciona |
|---|---|
| Fedora Silverblue, Bluefin, Fedora, Debian 13, Ubuntu 24.04, Arch, openSUSE Tumbleweed | tudo |
| Alpine | tudo, depois de instaladas as ferramentas GNU |
| Debian 12, Ubuntu 22.04 (testados, mas não em cada alteração) | o `kiwi` e as aplicações de linha de comandos. A libadwaita destes sistemas é demasiado antiga para as aplicações gráficas |

## Instalação { #install }

Este comando instala a parte de utilizador na tua pasta pessoal e a parte de
root para as aplicações que precisam de root. A palavra-passe só te é pedida
uma vez:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash
```

Se não quiseres nada fora da tua pasta pessoal, nem que te peçam alguma vez a
palavra-passe, instala só a parte de utilizador:

```bash
curl -fsSL https://raw.githubusercontent.com/derlocke-ng/kiwi-updater/main/get-kiwi.sh | bash -s -- --minimal
```

O instalador verifica se a versão que vai instalar está assinada com a chave
com que o kiwi-updater assina as suas versões, e recusa qualquer versão que não o
esteja. O catálogo Kiwi fica registado durante a instalação. Depois disso,
podes começar:

```bash
kiwi list                    # todas as aplicações que podes instalar
kiwi install <app>           # instala uma delas
kiwi info --installer <app>  # lê o instalador antes de ele correr
kiwi-gui                     # a aplicação gráfica
```

## Partes de root e versões assinadas { #root-parts-and-signed-releases }

Algumas aplicações precisam de root, por exemplo o kiwi-killswitch, que tem um
daemon de firewall. A parte de root destas aplicações é instalada por uma cópia
do kiwi que pertence ao root, e só a partir de fontes que o próprio root tem
nas suas listas. Instalar ou remover uma aplicação destas pede sempre a tua
palavra-passe. No modo predefinido, uma atualização só corre sem palavra-passe
se a versão estiver assinada com a chave que o root guardou para essa
aplicação.

## A documentação completa { #the-full-documentation }

O kiwi-updater tem a sua documentação no seu próprio repositório:

| Página | O que aborda |
|---|---|
| [Instalação](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/install.md) | sistemas suportados, pacotes para cada distribuição, modos de instalação, desinstalação |
| [Usar o kiwi](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/usage.md) | todos os comandos, a Kiwi Apps, atualizações em segundo plano, definições |
| [Catálogos](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/catalogs.md) | adicionar catálogos, `apps.list`, fixar uma versão, substituir entradas de um catálogo |
| [Segurança](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/security.md) | o que corre como root, quando escreves uma palavra-passe, o que o kiwi verifica |
| [Escrever uma aplicação](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/app-authors.md) | `kiwi.manifest`, `install.sh`, dependências, ícones, versões |
| [Versões assinadas](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/signing.md) | assinar as versões da tua aplicação com o `kiwi-release` |
| [Desenvolvimento](https://github.com/derlocke-ng/kiwi-updater/blob/main/docs/development.md) | testes, CI, publicar uma versão do kiwi-updater |

A partir da próxima versão do kiwi-updater, estas páginas vão aparecer também
aqui, no menu, por baixo de kiwi-updater.

Para publicares a tua própria aplicação, vê [Catálogos e
publicação](catalogs.md).
