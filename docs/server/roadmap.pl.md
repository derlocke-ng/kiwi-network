# Dokąd zmierza projekt

Ta strona opisuje, czym kiwi-server ma się stać w przyszłości i które części
tego planu już istnieją.

!!! info "Zaprojektowane, jeszcze niezrealizowane"
    Ta strona streszcza
    [projekt warstwy sterowania](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/design/control-plane.md)
    narzędzia kiwi-server, uzgodniony w październiku 2026. Nic z tego, co tu
    opisano, jeszcze nie istnieje, chyba że przy danym punkcie jest napisane
    *zrealizowane*. Kolejność prac wyznacza
    [roadmapa](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/ROADMAP.md).

Dziś kiwi-server to narzędzie, które uruchamiasz na swoim komputerze. Plik fleet, sekrety
i CA (urząd certyfikacji twojej sieci) są przechowywane na komputerze
administratora. Plan zakłada, że kiwi-server stanie się **usługą**, która
może działać na nodzie. Sieć będzie można wtedy tworzyć i nią zarządzać bez
linuksowego pulpitu, z telefonu, i to w kilka osób. Maszyny nadal będzie można
odtworzyć z pliku fleet. Warstwa sterowania (control plane) to ta część, która
przechowuje ten plik i uruchamia program generujący, czyli program, który
zamienia plik fleet w konfigurację każdej maszyny.

## Warstwy { #the-layers }

Projekt dzieli oprogramowanie na pięć warstw.

1. **kiwi-modules** zawiera moduły i kontrakt generowania, który określa, jak
   powstaje konfiguracja jednej maszyny. *Zrealizowane.*
2. **kiwi-stack** to część działająca na maszynie. Zaczyna się od
   `kiwi-stack apply`, które umieszcza wygenerowaną konfigurację na maszynie.
   *Zrealizowane.*
3. **Rdzeń kiwi-server** obsługuje plik fleet, hosty, systemy docelowe, obrazy
   ISO, CA, dodawanie urządzeń i `apply`. Tak jak dziś działa bez interfejsu
   graficznego (headless). *Zrealizowane.*
4. **Moduł sterujący** to rdzeń zapakowany w kontener, z API i interfejsem
   WWW. Działa na nodzie jak każdy inny moduł.
5. **Programy klienckie** to te, za pomocą których pracujesz z modułem sterującym.
   Najpierw powstanie interfejs WWW. Aplikacja GTK zostaje i komunikuje się
   albo z lokalnym CLI, albo przez sieć mesh, czyli prywatną sieć WireGuard,
   z kontrolerem (działającym modułem sterującym). CLI też zostaje. Cała
   logika pozostaje w rdzeniu, więc żaden klient nie ma własnej logiki.

## Node sterujący { #the-control-node }

Kontroler działa na nodzie w domu, nazywanym *node’em sterującym*. Dostęp do
niego mają tylko administratorzy i tylko z sieci mesh, a jego dysk jest
zaszyfrowany. Przechowuje seed, klucz CA, plik fleet i całą konfigurację.

Wynajęty **master staje się wymiennym pośrednikiem**. Przekazuje dalej ruch
sieci i przechowuje tylko to, czego potrzebuje do działania: swoje klucze
i peery WireGuard, własne hasła i swój certyfikat. Jeśli stracisz mastera,
stosujesz go ponownie z node’a sterującego. Jeśli stracisz node’a sterującego,
przywracasz kopię zapasową plików sieci.

## Użytkownicy { #users }

Blok `users:` definiuje użytkowników z jedną z dwóch ról. **Administrator
sieci** (fleet admin) może wszystko. **Administrator node’a** (node admin)
jest przypisany do własnych hostów. Widzi ich stan, logi, działające na nich
usługi i kopie zapasowe, a urządzenia może dodawać do tych grup, na które
pozwoli administrator sieci. Nie widzi niczego z mastera, CA ani pozostałych
node’ów. Do zalogowania się użytkownik potrzebuje hasła oraz albo certyfikatu
klienta wystawionego przez CA sieci, albo WebAuthn. Każda zmiana trafia do
dziennika audytu.

## Dołączanie maszyny { #joining-a-machine }

Maszyna może dołączyć do sieci na dwa sposoby i oba zostają:

- **ISO dla konkretnego hosta**, zawierający rolę maszyny, czyli dzisiejsze
  `build --offline`. Służy do instalacji offline.
- **Ogólny obraz startowy ISO** dla każdego systemu docelowego, budowany raz
  przez CI, bez żadnych sekretów. Przy pierwszym uruchomieniu maszyna pobiera
  swoją rolę z kontrolera za pomocą jednorazowego **tokenu dołączenia** (join
  token). Maszyna zainstalowana ręcznie albo VPS dołącza jedną linią:
  `curl https://control.<host>.<tld>/join/<token> | sudo bash`.

Każda maszyna z rodziny CoreOS ma działać na **jednym obrazie bootc**, czyli
jednym startowym obrazie kontenera, takim samym dla wszystkich. Rolę maszyna
dostaje przy pierwszym uruchomieniu.

## Federacja i multi-hop { #federation-and-multi-hop }

Federacja łączy osobne Kiwi Networks. Sieci, które ufają nawzajem swoim CA
i delegują sobie nazwy, stają się nawzajem swoimi klientami. Master ma trzy
tryby wyjścia, które decydują, którędy jego ruch trafia do internetu. W trzecim
z nich master jednej sieci wysyła swój ruch do internetu przez mastera innej
sieci. Nazywa się to **multi-hop**, a drugi master widzi tylko pierwszego.
Administrator, który w ten sposób prowadzi kilka masterów, ma własną usługę
VPN: mastery wejściowe w jednym kraju, mastery wyjściowe w innych krajach i Tor
wewnątrz sieci.

## Orchard { #the-orchard }

Orchard (po angielsku: sad) to planowana usługa dla osób, które prowadzą wiele
masterów dla innych. Ma to być osobna aplikacja albo wtyczka kiwi-server.
Tworzy VPS-y przez API dostawców hostingu i daje każdemu masterowi jego
instalację i token rejestracyjny. Od każdego mastera zbiera heartbeat, czyli
regularny raport o stanie (wersja, kondycja, dysk, ostatnia aktualizacja).
Aktualizacje wdraża, przestawiając tag obrazu w każdym kanale aktualizacji.

Orchard nie może zalogować się na mastera, odczytać pliku fleet ani zmienić
node’a. Każdy klient usługi, czyli każda osoba, dla której ktoś prowadzi
mastera, trzyma swoją sieć na własnym nodzie sterującym w domu. Plik fleet
i klucze zostają tam, więc dostawca hostingu, u którego działa maszyna
wirtualna mastera, nie może odczytać danych sieci klienta. Master każdego
klienta działa we własnej maszynie wirtualnej. Orchard potrzebuje sterownika
do API dostawców, a obsługa netcup w kiwi-server (`kiwi-server vps`,
*zrealizowane*) jest jego pierwszą częścią.

## Więcej dostawców hostingu i start przez sieć { #more-hosters-and-network-boot }

*Planowane.* Celem jest, żeby maszynę dało się zainstalować w pełni
automatycznie, niezależnie od tego, gdzie stoi.

- **Dostawcy hostingu jako wtyczki.** Obsługa netcup jest dziś wbudowana. Plan
  zakłada osobne repozytorium na API dostawców, tak żeby każdy mógł dodać AWS,
  Hetzner i innych. Wtyczka działałaby tak jak obecna obsługa netcup: tworzy
  albo czyści serwer, umieszcza na nim instalację i go uruchamia.
- **Wake-on-LAN i start przez PXE** są planowane dla maszyn w domu.
  Wake-on-LAN włącza maszynę przez sieć, a PXE pozwala jej wystartować z sieci.
  Node budzi się wtedy i instaluje przez sieć, bez pendrive’a.

## Co jeszcze jest na liście { #also-on-the-list }

Na roadmapie są też zapasowy master, rootless podman, IPv6 na całej trasie,
płytki ARM, zakresy portów, moduł do gier oraz przywracanie danych node’a przy
pierwszym uruchomieniu.
