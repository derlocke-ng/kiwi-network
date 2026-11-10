# kiwi-gen: Kiwi Key Generator

O kiwi-gen é uma página web que cria e gere **chaves SSH, certificados SSH e
certificados TLS** no teu navegador. Tudo é criado no teu próprio computador e
guardado lá num cofre cifrado, e nada é enviado para nenhum servidor.

- Repositório: [derlocke-ng/kiwi-gen](https://github.com/derlocke-ng/kiwi-gen), MIT
- Online: [derlocke-ng.github.io/kiwi-gen](https://derlocke-ng.github.io/kiwi-gen/)
- É uma página web estática e não uma aplicação do kiwi-updater. Não tem tags
  de versão.

Podes usá-lo para criar as chaves SSH do teu ficheiro fleet (o ficheiro que
descreve todas as máquinas da tua Kiwi Network), uma autoridade de
certificação (CA) para os teus próprios serviços ou certificados de cliente.
Tudo é gerado no navegador, sem ligação à rede.

## Funcionalidades { #features }

**Cofre.** As chaves e os certificados ficam guardados num único cofre
cifrado. O cofre é cifrado com AES-256-GCM, e a chave de cifragem é derivada
da tua palavra-passe mestra com PBKDF2-SHA256 e 600 000 iterações. Fica
guardado, cifrado, no localStorage do navegador. Só é decifrado em memória, e
só enquanto está desbloqueado. Para fazeres backup do cofre ou o levares para
outro lado, exporta-o como ficheiro. Podes importar chaves e certificados que
já tenhas, e um certificado que venha com a sua chave e a sua cadeia é
guardado como um único item. Também podes juntar outro cofre ao teu,
acrescentar notas, pesquisar e ver o que expira em breve.

**Chaves SSH.** O kiwi-gen cria chaves Ed25519, ECDSA (P-256/384/521) e RSA
(3072/4096). São escritas no verdadeiro formato OpenSSH, que o `ssh`, o
`ssh-keygen` e o `ssh-add` aceitam. A frase-senha é opcional. Se definires
uma, a chave é cifrada da mesma forma que o `ssh-keygen` o faz (bcrypt KDF,
aes256-ctr). É mostrada a impressão digital SHA256 da chave.

**Certificados SSH.** Podes criar uma CA SSH ou carregar uma que já tenhas e
depois assinar com ela certificados de utilizador ou de anfitrião. O kiwi-gen
dá-te as linhas correspondentes para o `sshd_config` e o `known_hosts`,
prontas a usar.

**Certificados TLS.** Podes criar uma CA raiz ou uma CA intermédia (ECDSA ou
RSA), ou carregar uma que já tenhas. Com a CA emites certificados de servidor
para nomes de anfitrião, wildcards e endereços IP, ou certificados de cliente.
Também podes assinar um pedido de assinatura de certificado (CSR) criado
noutro lado, para que a chave privada nunca tenha de entrar no kiwi-gen. O
kiwi-gen produz ficheiros com a cadeia completa (full chain) e pacotes
`.p12`. Os certificados passam no `openssl verify -x509_strict` e cumprem os
requisitos da Apple para certificados de servidor TLS.

**Inspecionar e converter.** O kiwi-gen lê certificados, CSRs, chaves e
certificados SSH em formato PEM ou DER. Consegue verificar se uma chave
corresponde a um certificado. Converte chaves privadas entre os formatos
PKCS#8, PKCS#1 e OpenSSH e, pelo caminho, pode acrescentar ou retirar uma
frase-senha. Também converte chaves públicas entre os formatos SSH e PEM.

## Como usar { #running-it }

Abre o `index.html` num navegador moderno. Funciona diretamente a partir do
disco, sem servidor web. Também podes servir a pasta:

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git && cd kiwi-gen
python3 -m http.server 8000      # depois http://localhost:8000
```

As funções WebCrypto do navegador só funcionam num contexto seguro, ou seja,
numa página carregada por HTTPS, a partir de `localhost` ou de `file://`. Se
abrires a página por HTTP simples a partir de outra máquina, não funciona.

## Como funciona { #how-it-works }

Todas as operações criptográficas são feitas pela
[Web Crypto API](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API) do
navegador. O código que codifica os formatos OpenSSH, X.509, PKCS#8, PKCS#10 e
PKCS#12 está num único ficheiro sem dependências, `kiwi-crypto.js`. Não há
passo de compilação, e a página não carrega nada de nenhuma CDN. Uma
Content-Security-Policy bloqueia todos os pedidos de rede, por isso as chaves
não podem sair da página.

Uma página web não pode funcionar como agente SSH. Para usares as chaves que
crias, carrega-as no teu `ssh-agent` habitual com o `ssh-add`. O cofre só é
tão seguro quanto a tua palavra-passe mestra e o teu perfil do navegador. O
Ed25519 precisa de um navegador recente (Chrome 137+, Firefox 129+,
Safari 17+).
