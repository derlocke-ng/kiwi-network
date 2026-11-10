# kiwi-gen: Kiwi Key Generator

kiwi-gen is a web page that creates and manages **SSH keys, SSH certificates
and TLS certificates** in your browser. Everything is created on your own
computer and stored there in an encrypted vault, and nothing is sent to any
server.

- Repository: [derlocke-ng/kiwi-gen](https://github.com/derlocke-ng/kiwi-gen), MIT
- Live: [derlocke-ng.github.io/kiwi-gen](https://derlocke-ng.github.io/kiwi-gen/)
- It is a static web page, not a kiwi-updater app. There are no release tags.

You can use it to create the SSH keys for your fleet file (the file that
describes every machine of your Kiwi Network), a certificate authority (CA)
for your own services, or client certificates. All of them are generated
offline in the browser.

## Features

**Vault.** Keys and certificates are kept in one encrypted vault. It is
encrypted with AES-256-GCM, and the encryption key is derived from your master
password with PBKDF2-SHA256 at 600,000 iterations. The vault is stored in
encrypted form in the browser's localStorage. It is decrypted only in memory,
and only while it is unlocked. To back the vault up or move it, export it as a
file. You can import existing keys and certificates, and a certificate that
comes with its key and chain is stored as one item. You can also merge another
vault into yours, add notes, search, and see what expires soon.

**SSH keys.** kiwi-gen creates Ed25519, ECDSA (P-256/384/521) and RSA
(3072/4096) keys. They are written in the real OpenSSH format, which `ssh`,
`ssh-keygen` and `ssh-add` accept. A passphrase is optional. If you set one,
the key is encrypted in the same way `ssh-keygen` does it (bcrypt KDF,
aes256-ctr). The SHA256 fingerprint of the key is shown.

**SSH certificates.** You can create an SSH CA or load an existing one, and
then sign user certificates or host certificates with it. kiwi-gen gives you
the matching lines for `sshd_config` and `known_hosts`, ready to use.

**TLS certificates.** You can create a root CA or an intermediate CA (ECDSA or
RSA), or load an existing one. With the CA you issue server certificates for
hostnames, wildcards and IP addresses, or client certificates. You can also
sign a certificate signing request (CSR) that was created elsewhere, so the
private key never has to be brought into kiwi-gen. kiwi-gen produces
full-chain files and `.p12` bundles. The certificates pass
`openssl verify -x509_strict` and meet Apple's requirements for TLS server
certificates.

**Inspect & convert.** kiwi-gen reads certificates, CSRs, keys and SSH
certificates in PEM or DER format. It can check that a key matches a
certificate. It converts private keys between PKCS#8, PKCS#1 and OpenSSH
format and can add or remove a passphrase while doing so. It also converts
public keys between the SSH and PEM formats.

## Running it

Open `index.html` in a modern browser. This works directly from the disk,
without a web server. You can also serve the folder:

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git && cd kiwi-gen
python3 -m http.server 8000      # then http://localhost:8000
```

The browser's WebCrypto functions only work in a secure context. That is a
page loaded over HTTPS, from `localhost` or from `file://`. If you open the
page over plain HTTP from another machine, it will not work.

## How it works

All cryptographic operations are done by the browser's
[Web Crypto API](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API). The
code that encodes the OpenSSH, X.509, PKCS#8, PKCS#10 and PKCS#12 formats is in
one file, `kiwi-crypto.js`, which has no dependencies. There is no build step,
and the page loads nothing from a CDN. A Content-Security-Policy blocks all
network requests, so keys cannot leave the page.

A web page cannot act as an SSH agent. To use the keys you create, load them
into your usual `ssh-agent` with `ssh-add`. The vault is only as safe as your
master password and your browser profile. Ed25519 needs a current browser
(Chrome 137+, Firefox 129+, Safari 17+).
