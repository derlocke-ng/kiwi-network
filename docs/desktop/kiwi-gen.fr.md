# kiwi-gen : Kiwi Key Generator

Un gestionnaire dans le navigateur pour les **clés SSH, les certificats SSH et les
certificats TLS**. Tout est créé et stocké localement dans un coffre chiffré, et
rien n’est envoyé à aucun serveur.

- Dépôt : [derlocke-ng/kiwi-gen](https://github.com/derlocke-ng/kiwi-gen), MIT
- En ligne : [derlocke-ng.github.io/kiwi-gen](https://derlocke-ng.github.io/kiwi-gen/)
- C’est une page web statique, pas une application kiwi-updater. Il n’y a pas de
  tags de version.

Utilisez-le pour les clés SSH de votre fichier fleet, une autorité de certification
pour vos propres services ou des certificats clients, le tout généré hors ligne dans
le navigateur.

## Fonctionnalités { #features }

**Coffre.** Les clés et les certificats sont conservés dans un seul coffre chiffré :
AES-256-GCM, avec la clé dérivée de votre mot de passe maître par PBKDF2-SHA256 à
600 000 itérations. Le coffre est stocké chiffré dans le localStorage du navigateur
et n’est déchiffré qu’en mémoire tant qu’il est déverrouillé. Exportez-le dans un
fichier pour le sauvegarder ou le déplacer. Vous pouvez importer des clés et des
certificats existants (un certificat avec sa clé et sa chaîne devient un seul
élément), fusionner un autre coffre, ajouter des notes, chercher, et voir ce qui
expire bientôt.

**Clés SSH.** Ed25519, ECDSA (P-256/384/521) et RSA (3072/4096), au véritable format
OpenSSH accepté par `ssh`, `ssh-keygen` et `ssh-add`. Les phrases secrètes
facultatives sont chiffrées comme le fait `ssh-keygen` (KDF bcrypt, aes256-ctr), et
l’empreinte SHA256 est affichée.

**Certificats SSH.** Créez une autorité de certification SSH ou chargez-en une, puis
signez des certificats d’utilisateur ou d’hôte. Il vous fournit des lignes
`sshd_config` et `known_hosts` toutes prêtes.

**Certificats TLS.** Créez une autorité de certification racine ou intermédiaire
(ECDSA ou RSA), ou chargez-en une existante. Émettez des certificats serveur (noms
d’hôtes, jokers, IP) ou des certificats clients, et signez des CSR venus d’ailleurs
pour que la clé privée n’ait jamais à venir ici. Il produit des fichiers à chaîne
complète et des paquets `.p12`. Les certificats passent
`openssl verify -x509_strict` et respectent les exigences d’Apple pour les
certificats de serveur TLS.

**Inspection et conversion.** Lire des certificats, des CSR, des clés et des
certificats SSH (PEM ou DER), vérifier qu’une clé correspond à un certificat,
convertir des clés privées entre PKCS#8, PKCS#1 et OpenSSH (en ajoutant ou en
retirant une phrase secrète), et convertir des clés publiques entre SSH et PEM.

## Le lancer { #running-it }

Ouvrez `index.html` dans un navigateur récent (il fonctionne directement depuis le
disque), ou servez le dossier :

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git && cd kiwi-gen
python3 -m http.server 8000      # puis http://localhost:8000
```

WebCrypto ne fonctionne que dans des contextes sécurisés : HTTPS, `localhost` ou
`file://`. Du HTTP simple depuis une autre machine ne fonctionnera pas.

## Comment ça marche { #how-it-works }

Toute la cryptographie utilise l’[API Web Crypto](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API)
du navigateur. L’encodage OpenSSH, X.509, PKCS#8, PKCS#10 et PKCS#12 tient dans un
seul fichier sans dépendance, `kiwi-crypto.js`. Il n’y a pas d’étape de compilation
et rien ne se charge depuis un CDN. Une Content-Security-Policy bloque toutes les
requêtes réseau, si bien que les clés ne peuvent pas quitter la page.

Une page web ne peut pas faire office d’agent SSH. Chargez les clés que vous créez
dans votre `ssh-agent` habituel avec `ssh-add`. Le coffre n’est pas plus sûr que
votre mot de passe maître et votre profil de navigateur. Ed25519 demande un
navigateur à jour (Chrome 137+, Firefox 129+, Safari 17+).
