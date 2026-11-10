# kiwi-gen : Kiwi Key Generator

kiwi-gen est une page web qui crée et gère des **clés SSH, des certificats SSH
et des certificats TLS** dans votre navigateur. Tout est créé sur votre propre
ordinateur et y est conservé dans un coffre chiffré, et rien n’est envoyé à un
serveur.

- Dépôt : [derlocke-ng/kiwi-gen](https://github.com/derlocke-ng/kiwi-gen), MIT
- En ligne : [derlocke-ng.github.io/kiwi-gen](https://derlocke-ng.github.io/kiwi-gen/)
- C’est une page web statique, pas une application kiwi-updater. Il n’y a pas
  de tags de version.

Vous pouvez vous en servir pour créer les clés SSH de votre fichier fleet (le
fichier qui décrit chaque machine de votre Kiwi Network), une autorité de
certification (CA) pour vos propres services, ou des certificats clients. Tout
est généré hors ligne, dans le navigateur.

## Fonctions { #features }

**Coffre.** Les clés et les certificats sont rangés dans un seul coffre
chiffré. Il est chiffré en AES-256-GCM, et la clé de chiffrement est dérivée de
votre mot de passe principal par PBKDF2-SHA256 avec 600 000 itérations. Le
coffre est stocké sous forme chiffrée dans le localStorage du navigateur. Il
n’est déchiffré qu’en mémoire, et seulement tant qu’il est déverrouillé. Pour
le sauvegarder ou le déplacer, exportez-le dans un fichier. Vous pouvez
importer des clés et des certificats existants, et un certificat accompagné de
sa clé et de sa chaîne est rangé comme un seul élément. Vous pouvez aussi
fusionner un autre coffre avec le vôtre, ajouter des notes, faire des
recherches et voir ce qui expire bientôt.

**Clés SSH.** kiwi-gen crée des clés Ed25519, ECDSA (P-256/384/521) et RSA
(3072/4096). Elles sont écrites au vrai format OpenSSH, qu’acceptent `ssh`,
`ssh-keygen` et `ssh-add`. La phrase de passe est facultative. Si vous en
définissez une, la clé est chiffrée de la même façon que le fait `ssh-keygen`
(KDF bcrypt, aes256-ctr). L’empreinte SHA256 de la clé est affichée.

**Certificats SSH.** Vous pouvez créer une CA SSH ou en charger une existante,
puis signer avec elle des certificats d’utilisateur ou d’hôte. kiwi-gen vous
donne les lignes correspondantes pour `sshd_config` et `known_hosts`, prêtes à
l’emploi.

**Certificats TLS.** Vous pouvez créer une CA racine ou une CA intermédiaire
(ECDSA ou RSA), ou en charger une existante. Avec la CA, vous émettez des
certificats serveur pour des noms d’hôte, des wildcards et des adresses IP, ou
des certificats clients. Vous pouvez aussi signer une demande de signature de
certificat (CSR) créée ailleurs : la clé privée n’a alors jamais besoin
d’entrer dans kiwi-gen. kiwi-gen produit des fichiers avec la chaîne complète
et des paquets `.p12`. Les certificats passent `openssl verify -x509_strict`
et respectent les exigences d’Apple pour les certificats de serveur TLS.

**Inspection et conversion.** kiwi-gen lit des certificats, des CSR, des clés
et des certificats SSH au format PEM ou DER. Il peut vérifier qu’une clé
correspond à un certificat. Il convertit les clés privées entre les formats
PKCS#8, PKCS#1 et OpenSSH, et peut au passage ajouter ou retirer une phrase de
passe. Il convertit aussi les clés publiques entre les formats SSH et PEM.

## Le lancer { #running-it }

Ouvrez `index.html` dans un navigateur récent. Cela fonctionne directement
depuis le disque, sans serveur web. Vous pouvez aussi servir le dossier :

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git && cd kiwi-gen
python3 -m http.server 8000      # puis http://localhost:8000
```

Les fonctions WebCrypto du navigateur ne fonctionnent que dans un contexte
sécurisé, c’est-à-dire une page chargée en HTTPS, depuis `localhost` ou depuis
`file://`. Si vous ouvrez la page en simple HTTP depuis une autre machine, elle
ne fonctionnera pas.

## Fonctionnement { #how-it-works }

Toutes les opérations cryptographiques sont faites par la
[Web Crypto API](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API) du
navigateur. Le code qui encode les formats OpenSSH, X.509, PKCS#8, PKCS#10 et
PKCS#12 tient dans un seul fichier, `kiwi-crypto.js`, sans aucune dépendance.
Il n’y a pas d’étape de build, et la page ne charge rien depuis un CDN. Une
Content-Security-Policy bloque toutes les requêtes réseau, si bien que les clés
ne peuvent pas quitter la page.

Une page web ne peut pas servir d’agent SSH. Pour utiliser les clés que vous
créez, chargez-les dans votre `ssh-agent` habituel avec `ssh-add`. Le coffre
n’est pas plus sûr que votre mot de passe principal et votre profil de
navigateur. Ed25519 demande un navigateur récent (Chrome 137+, Firefox 129+,
Safari 17+).
