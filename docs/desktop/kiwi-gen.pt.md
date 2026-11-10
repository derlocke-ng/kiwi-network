# kiwi-gen: Kiwi Key Generator

Um gestor no navegador para **chaves SSH, certificados SSH e certificados TLS**.
Tudo é criado e guardado localmente num cofre cifrado, e nada é enviado para
nenhum servidor.

- Repositório: [derlocke-ng/kiwi-gen](https://github.com/derlocke-ng/kiwi-gen), MIT
- Ao vivo: [derlocke-ng.github.io/kiwi-gen](https://derlocke-ng.github.io/kiwi-gen/)
- É uma página web estática, não uma app do kiwi-updater. Não há tags de versão.

Usa-o para as chaves SSH do teu ficheiro fleet, para uma CA para os teus próprios
serviços ou para certificados de cliente, tudo gerado offline no navegador.

## Funcionalidades { #features }

**Cofre.** As chaves e os certificados ficam num único cofre cifrado:
AES-256-GCM, com a chave derivada da tua palavra-passe mestra por PBKDF2-SHA256
com 600 000 iterações. O cofre é guardado cifrado no localStorage do navegador e
só é decifrado em memória enquanto está desbloqueado. Exporta-o como ficheiro
para fazeres uma cópia de segurança ou para o moveres. Podes importar chaves e
certificados existentes (um certificado com a sua chave e cadeia passa a ser um
único item), fundir outro cofre, acrescentar notas, pesquisar e ver o que expira
em breve.

**Chaves SSH.** Ed25519, ECDSA (P-256/384/521) e RSA (3072/4096), em formato
OpenSSH verdadeiro, aceite pelo `ssh`, pelo `ssh-keygen` e pelo `ssh-add`. As
frases-senha opcionais são cifradas da mesma forma que o `ssh-keygen` o faz
(bcrypt KDF, aes256-ctr), e a impressão digital SHA256 é mostrada.

**Certificados SSH.** Cria uma CA SSH ou carrega uma, e depois assina certificados
de utilizador ou de anfitrião. Dá-te linhas prontas para `sshd_config` e
`known_hosts`.

**Certificados TLS.** Cria uma CA raiz ou intermédia (ECDSA ou RSA), ou carrega
uma existente. Emite certificados de servidor (nomes de anfitrião, wildcards,
IPs) ou certificados de cliente, e assina CSRs vindos de outro lado, para que a
chave privada nunca tenha de vir para aqui. Produz ficheiros full-chain e pacotes
`.p12`. Os certificados passam no `openssl verify -x509_strict` e cumprem os
requisitos da Apple para certificados de servidor TLS.

**Inspecionar e converter.** Lê certificados, CSRs, chaves e certificados SSH
(PEM ou DER), verifica se uma chave corresponde a um certificado, converte chaves
privadas entre PKCS#8, PKCS#1 e OpenSSH (acrescentando ou removendo uma
frase-senha) e converte chaves públicas entre SSH e PEM.

## Executá-lo { #running-it }

Abre `index.html` num navegador moderno (funciona diretamente a partir do disco),
ou serve a pasta:

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git && cd kiwi-gen
python3 -m http.server 8000      # depois http://localhost:8000
```

A WebCrypto só funciona em contextos seguros: HTTPS, `localhost` ou `file://`.
HTTP simples a partir de outra máquina não funciona.

## Como funciona { #how-it-works }

Toda a criptografia usa a
[Web Crypto API](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API) do
navegador. A codificação OpenSSH, X.509, PKCS#8, PKCS#10 e PKCS#12 está num único
ficheiro sem dependências, `kiwi-crypto.js`. Não há passo de build e nada é
carregado de um CDN. Uma Content-Security-Policy bloqueia todos os pedidos de
rede, por isso as chaves não podem sair da página.

Uma página web não pode funcionar como agente SSH. Carrega as chaves que crias no
teu `ssh-agent` habitual com `ssh-add`. O cofre só é tão seguro quanto a tua
palavra-passe mestra e o teu perfil do navegador. O Ed25519 precisa de um
navegador atual (Chrome 137+, Firefox 129+, Safari 17+).
