# kiwi-gen: Kiwi Key Generator

kiwi-gen to strona internetowa, która tworzy **klucze SSH, certyfikaty SSH
i certyfikaty TLS** w twojej przeglądarce i nimi zarządza. Wszystko powstaje
na twoim własnym komputerze i jest tam przechowywane w zaszyfrowanym sejfie,
a nic nie jest wysyłane na żaden serwer.

- Repozytorium: [derlocke-ng/kiwi-gen](https://github.com/derlocke-ng/kiwi-gen), MIT
- Działa pod adresem: [derlocke-ng.github.io/kiwi-gen](https://derlocke-ng.github.io/kiwi-gen/)
- To statyczna strona internetowa, a nie aplikacja instalowana przez
  kiwi-updater. Nie ma tagów wydań.

Możesz w niej utworzyć klucze SSH do pliku fleet (pliku, który opisuje każdą
maszynę twojej sieci Kiwi Network), urząd certyfikacji (CA) dla własnych
usług albo certyfikaty klienckie. Wszystko to powstaje w przeglądarce, bez
połączenia z internetem.

## Funkcje { #features }

**Sejf.** Klucze i certyfikaty są przechowywane w jednym zaszyfrowanym sejfie.
Jest on szyfrowany algorytmem AES-256-GCM, a klucz szyfrowania jest
wyprowadzany z twojego hasła głównego funkcją PBKDF2-SHA256 przy 600 000
iteracji. Sejf jest zapisany w postaci zaszyfrowanej w localStorage
przeglądarki. Odszyfrowuje się go tylko w pamięci i tylko wtedy, gdy jest
odblokowany. Żeby zrobić kopię zapasową sejfu albo go przenieść, wyeksportuj go
do pliku. Możesz importować istniejące klucze i certyfikaty, a certyfikat
razem z kluczem i łańcuchem zapisuje się jako jedna pozycja. Możesz też
scalić z twoim sejfem inny sejf, dodawać notatki, wyszukiwać i sprawdzać, co
wkrótce wygasa.

**Klucze SSH.** kiwi-gen tworzy klucze Ed25519, ECDSA (P-256/384/521) i RSA
(3072/4096). Zapisuje je w prawdziwym formacie OpenSSH, który przyjmują `ssh`,
`ssh-keygen` i `ssh-add`. Fraza dostępu jest opcjonalna. Jeśli ją ustawisz,
klucz jest szyfrowany tak samo, jak robi to `ssh-keygen` (bcrypt KDF,
aes256-ctr). Wyświetlany jest odcisk klucza SHA256.

**Certyfikaty SSH.** Możesz utworzyć urząd certyfikacji SSH albo wczytać
istniejący, a potem podpisywać nim certyfikaty użytkowników i hostów. kiwi-gen
podaje gotowe do użycia wiersze dla `sshd_config` i `known_hosts`.

**Certyfikaty TLS.** Możesz utworzyć główny albo pośredni urząd certyfikacji
(ECDSA lub RSA) albo wczytać istniejący. Za pomocą CA wystawiasz certyfikaty
serwerów dla nazw hostów, symboli wieloznacznych i adresów IP albo certyfikaty
klienckie. Możesz też podpisać żądanie podpisania certyfikatu (CSR) utworzone
gdzie indziej, dzięki czemu klucz prywatny w ogóle nie musi trafiać do
kiwi-gen. kiwi-gen tworzy pliki z pełnym łańcuchem i paczki `.p12`. Certyfikaty
przechodzą `openssl verify -x509_strict` i spełniają wymagania Apple dla
certyfikatów serwerów TLS.

**Podgląd i konwersja.** kiwi-gen odczytuje certyfikaty, żądania CSR, klucze
i certyfikaty SSH w formacie PEM lub DER. Potrafi sprawdzić, czy klucz pasuje
do certyfikatu. Konwertuje klucze prywatne między formatami PKCS#8, PKCS#1
i OpenSSH, a przy okazji może dodać albo usunąć frazę dostępu. Konwertuje też
klucze publiczne między formatami SSH i PEM.

## Uruchamianie { #running-it }

Otwórz `index.html` w nowoczesnej przeglądarce. Działa to bezpośrednio
z dysku, bez serwera WWW. Możesz też serwować cały folder:

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git && cd kiwi-gen
python3 -m http.server 8000      # potem http://localhost:8000
```

Funkcje WebCrypto przeglądarki działają tylko w bezpiecznym kontekście, czyli
na stronie wczytanej przez HTTPS, z `localhost` albo z `file://`. Jeśli
otworzysz stronę przez zwykłe HTTP z innej maszyny, nie zadziała.

## Jak to działa { #how-it-works }

Wszystkie operacje kryptograficzne wykonuje
[Web Crypto API](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API)
przeglądarki. Kod, który koduje formaty OpenSSH, X.509, PKCS#8, PKCS#10
i PKCS#12, mieści się w jednym pliku, `kiwi-crypto.js`, bez żadnych
zależności. Nie ma etapu budowania, a strona niczego nie wczytuje z CDN.
Content-Security-Policy blokuje wszystkie żądania sieciowe, więc klucze nie
mogą wydostać się poza stronę.

Strona internetowa nie może działać jako agent SSH. Żeby korzystać
z utworzonych kluczy, wczytaj je do swojego zwykłego `ssh-agent` poleceniem
`ssh-add`. Sejf jest tak bezpieczny, jak twoje hasło główne i twój profil
przeglądarki. Ed25519 wymaga aktualnej przeglądarki (Chrome 137+, Firefox
129+, Safari 17+).
