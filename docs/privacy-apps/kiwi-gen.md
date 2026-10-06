# kiwi-gen — Kiwi Key Generator

A browser-based manager for **SSH keys, SSH certificates and TLS
certificates**. Everything is created and stored locally in an encrypted vault,
and nothing is ever sent to any server.

- Repository: <https://github.com/derlocke-ng/kiwi-gen>
- Live demo: <https://derlocke-ng.github.io/kiwi-gen/>
- License: MIT.

It is the natural companion to the rest of the network: the SSH keys you put in
a `fleet.yaml`, the CA you import onto your devices, the certificates your nodes
serve — all can be generated here, offline, without a key ever touching a
network.

## What it does

### Vault
- Keeps keys and certificates in one encrypted vault (AES-256-GCM, key derived
  from your master password with PBKDF2-SHA256, 600,000 iterations).
- Stored encrypted in the browser's localStorage, decrypted only in memory
  while unlocked; export it as a file to back up or move to another device.
- Import existing items, merge another vault, rename, add notes, search, and see
  what expires soon.

### SSH keys
- Ed25519, ECDSA (P-256/384/521) and RSA (3072/4096).
- Real OpenSSH format, accepted by `ssh`, `ssh-keygen` and `ssh-add`.
- Optional passphrase, encrypted the way `ssh-keygen` does (bcrypt KDF,
  aes256-ctr). SHA256 fingerprint shown for verification.

### SSH certificates
- Create an SSH CA or load an existing one; sign user or host certificates.
- Ready-made `sshd_config` and `known_hosts` lines to set up trust.

### TLS certificates
- Create a root or intermediate CA (ECDSA or RSA), or load an existing one.
- Issue server certificates (hostnames, wildcards, IPs) or client certificates;
  sign CSRs so a private key never has to come here.
- Full-chain files and `.p12` bundles. Certificates pass
  `openssl verify -x509_strict` and meet Apple's TLS server requirements.

### Inspect & convert
- Inspect certificates, CSRs, keys and SSH certificates (PEM or DER); check that
  a key matches a certificate; convert keys between PKCS#8, PKCS#1 and OpenSSH.

## Usage

Open `index.html` in a modern browser (works from disk), or serve the folder:

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git
cd kiwi-gen && python3 -m http.server 8000
```

WebCrypto only works in secure contexts, so use HTTPS, `localhost` or `file://`.
All cryptography uses the browser's [Web Crypto API](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API);
encoding lives in one dependency-free `kiwi-crypto.js`, there is no build step,
nothing loads from a CDN, and a Content-Security-Policy blocks all network
requests so keys cannot leave the page.

The vault is only as safe as your master password and your browser profile: use
a strong password and lock the vault when you are done. Ed25519 needs a current
browser (Chrome 137+, Firefox 129+, Safari 17+).
