# kiwi-gen: Kiwi Key Generator

Działający w przeglądarce menedżer **kluczy SSH, certyfikatów SSH i
certyfikatów TLS**. Wszystko jest tworzone i przechowywane lokalnie w
zaszyfrowanym sejfie i nic nie jest wysyłane na żaden serwer.

- Repozytorium: [derlocke-ng/kiwi-gen](https://github.com/derlocke-ng/kiwi-gen), MIT
- Na żywo: [derlocke-ng.github.io/kiwi-gen](https://derlocke-ng.github.io/kiwi-gen/)
- To statyczna strona WWW, a nie aplikacja kiwi-updater. Nie ma tagów wydań.

Używaj go do kluczy SSH w twoim pliku fleet, CA dla twoich własnych usług lub
certyfikatów klienta, wszystko generowane offline w przeglądarce.

## Funkcje { #features }

**Sejf.** Klucze i certyfikaty są trzymane w jednym zaszyfrowanym sejfie:
AES-256-GCM, z kluczem wyprowadzanym z twojego hasła głównego przez
PBKDF2-SHA256 przy 600 000 iteracji. Sejf jest przechowywany zaszyfrowany w
localStorage przeglądarki i odszyfrowywany tylko w pamięci, gdy jest
odblokowany. Wyeksportuj go jako plik, żeby zrobić kopię zapasową lub go
przenieść. Możesz importować istniejące klucze i certyfikaty (certyfikat z
kluczem i łańcuchem staje się jednym elementem), scalić inny sejf, dodawać
notatki, wyszukiwać i sprawdzać, co wkrótce wygasa.

**Klucze SSH.** Ed25519, ECDSA (P-256/384/521) i RSA (3072/4096), w
prawdziwym formacie OpenSSH akceptowanym przez `ssh`, `ssh-keygen` i
`ssh-add`. Opcjonalne frazy dostępu są szyfrowane tak, jak robi to
`ssh-keygen` (bcrypt KDF, aes256-ctr), a odcisk SHA256 jest wyświetlany.

**Certyfikaty SSH.** Utwórz CA SSH lub wczytaj istniejący, potem podpisuj
certyfikaty użytkowników lub hostów. Dostajesz gotowe linie `sshd_config` i
`known_hosts`.

**Certyfikaty TLS.** Utwórz główny lub pośredni CA (ECDSA lub RSA) albo
wczytaj istniejący. Wystawiaj certyfikaty serwerów (nazwy hostów, wildcardy,
adresy IP) lub klientów i podpisuj CSR-y z innych miejsc, żeby klucz prywatny
nigdy nie musiał tu trafić. Tworzy pliki z pełnym łańcuchem i paczki `.p12`.
Certyfikaty przechodzą `openssl verify -x509_strict` i spełniają wymagania
Apple dla certyfikatów serwerów TLS.

**Inspekcja i konwersja.** Odczytuj certyfikaty, CSR-y, klucze i certyfikaty
SSH (PEM lub DER), sprawdzaj, czy klucz pasuje do certyfikatu, konwertuj
klucze prywatne między PKCS#8, PKCS#1 i OpenSSH (dodając lub usuwając frazę
dostępu) oraz klucze publiczne między SSH i PEM.

## Uruchamianie { #running-it }

Otwórz `index.html` w nowoczesnej przeglądarce (działa prosto z dysku) albo
serwuj folder:

```bash
git clone https://github.com/derlocke-ng/kiwi-gen.git && cd kiwi-gen
python3 -m http.server 8000      # potem http://localhost:8000
```

WebCrypto działa tylko w bezpiecznych kontekstach: HTTPS, `localhost` lub
`file://`. Zwykłe HTTP z innej maszyny nie zadziała.

## Jak to działa { #how-it-works }

Cała kryptografia korzysta z
[Web Crypto API](https://developer.mozilla.org/docs/Web/API/Web_Crypto_API)
przeglądarki. Kodowanie OpenSSH, X.509, PKCS#8, PKCS#10 i PKCS#12 jest w
jednym pliku bez zależności, `kiwi-crypto.js`. Nie ma kroku budowania i nic nie
jest ładowane z CDN. Content-Security-Policy blokuje wszystkie żądania
sieciowe, więc klucze nie mogą opuścić strony.

Strona WWW nie może działać jako agent SSH. Wczytaj utworzone klucze do
swojego zwykłego `ssh-agent` przez `ssh-add`. Sejf jest tylko tak bezpieczny
jak twoje hasło główne i twój profil przeglądarki. Ed25519 wymaga aktualnej
przeglądarki (Chrome 137+, Firefox 129+, Safari 17+).
