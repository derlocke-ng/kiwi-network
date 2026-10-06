# kiwi-gen: Kiwi Key Generator

A browser-based manager for **SSH keys, SSH certificates and TLS
certificates**. Everything is created and stored locally in an encrypted vault,
and nothing is sent to any server.

- Repository: [derlocke-ng/kiwi-gen](https://github.com/derlocke-ng/kiwi-gen), MIT
- Live: [derlocke-ng.github.io/kiwi-gen](https://derlocke-ng.github.io/kiwi-gen/)
- It is a static web page, not a kiwi-updater app.

It fits the rest of the network: the SSH keys in your `fleet.yaml`, a CA for
your own services, client certificates, all generated offline in the browser.

## Features

**Vault.** Keys and certificates are kept in one encrypted vault: AES-256-GCM,
with the key derived from your master password by PBKDF2-SHA256 at 600,000
iterations. The vault is stored encrypted in the browser's localStorage and
decrypted only in memory while unlocked. Export it as a file to back it up or
move it. You can import existing keys and certificates (a certificate with its
key and chain becomes one item), merge another vault, add notes, search, and
see what expires soon.

**SSH keys.** Ed25519, ECDSA (P-256/384/521) and RSA (3072/4096), in real
OpenSSH format accepted by `ssh`, `ssh-keygen` and `ssh-add`. Optional
passphrases are encrypted the way `ssh-keygen` does it (bcrypt KDF,
aes256-ctr), and the SHA256 fingerprint is shown.

**SSH certificates.** Create an SSH CA or load one, then sign user or host
certificates. It gives you ready-made `sshd_config` and `known_hosts` lines.

**TLS certificates.** Create a root or intermediate CA (ECDSA or RSA), or load
an existing one. Issue server certificates (hostnames, wildcards, IPs) or client
certificates, and sign CSRs from elsewhere so the private key never has to come
here. It produces full-chain files and `.p12` bundles. Certificates pass
`openssl verify -x509_strict` and meet Apple's requirements for TLS server
certificates.

**Inspect & convert.** Read certificates, CSRs, keys and SSH certificates (PEM
or DER), check that a key matches a certificate, and convert private keys
between PKCS#8, PKCS#1 and OpenSSH.

## Running it

Open `index.html` in a modern browser (it works straight from disk), or serve
the folder:

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git && cd kiwi-gen
python3 -m http.server 8000      # then http://localhost:8000
```

WebCrypto only works in secure contexts: HTTPS, `localhost` or `file://`.

## How it works

All cryptography uses the browser's
[Web Crypto API](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API). The
OpenSSH, X.509, PKCS#8, PKCS#10 and PKCS#12 encoding is in one dependency-free
file, `kiwi-crypto.js`. There is no build step and nothing loads from a CDN. A
Content-Security-Policy blocks all network requests, so keys cannot leave the
page.

A web page cannot act as an SSH agent. Load the keys you make into your usual
`ssh-agent` with `ssh-add`. The vault is only as safe as your master password
and your browser profile. Ed25519 needs a current browser (Chrome 137+,
Firefox 129+, Safari 17+).
