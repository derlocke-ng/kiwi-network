# Dokąd to zmierza

!!! info "Zaprojektowane, nie zbudowane"
    Ta strona streszcza
    [projekt płaszczyzny sterowania](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/design/control-plane.md)
    kiwi-server, uzgodniony w październiku 2026. O ile linia nie mówi
    *zbudowane*, nic z tego jeszcze nie istnieje.
    [Roadmapa](https://github.com/derlocke-ng/kiwi-server/blob/main/docs/ROADMAP.md)
    śledzi kolejność.

Dziś kiwi-server to narzędzie desktopowe: plik fleet, sekrety i CA leżą na
maszynie operatora. Plan jest taki, żeby stał się **usługą**, która może
działać na nodzie, dzięki czemu sieć da się tworzyć i nią zarządzać bez
desktopa z Linuksem, z telefonu i przez więcej niż jedną osobę. Maszyny nadal
dają się odtworzyć z pliku fleet. Płaszczyzna sterowania to po prostu to, co
trzyma ten plik i uruchamia renderer.

## Warstwy { #the-layers }

1. **kiwi-modules**: moduły i kontrakt renderowania dla jednej maszyny. *Zbudowane.*
2. **kiwi-stack**: strona maszyny, od `kiwi-stack apply`. *Zbudowane.*
3. **Rdzeń kiwi-server**: flota, hosty, targety, obrazy ISO, CA, rejestracja i
   apply, bez interfejsu graficznego, jak dziś. *Zbudowane.*
4. **Moduł sterujący**: rdzeń jako kontener, z API i interfejsem WWW,
   działający jako moduł na nodzie jak każdy inny.
5. **Klienci**: najpierw interfejs WWW. Aplikacja GTK zostaje i rozmawia z
   lokalnym CLI albo z kontrolerem przez sieć mesh; CLI też zostaje. Żaden
   frontend nie dostaje własnej logiki.

## Node sterujący { #the-control-node }

Kontroler działa na nodzie w domu (*node sterujący*), osiągalnym z sieci mesh
tylko dla administratorów, na zaszyfrowanym dysku. Trzyma seed, klucz CA, plik
fleet i każdą konfigurację.

Wynajmowany **master staje się wymienialną infrastrukturą przekaźnikową**.
Trzyma tylko to, czego potrzebuje do działania: swoje klucze i peerów
WireGuard, własne hasła i swój certyfikat. Jego utrata kosztuje ponowne apply
z node'a sterującego. Utrata node'a sterującego kosztuje odtworzenie kopii
zapasowej floty.

## Użytkownicy { #users }

Blok `users:` z dwiema rolami: **administrator floty**, który może wszystko, i
**administratorzy node'ów** przypisani do własnych hostów. Administrator
node'a widzi stan, logi, obciążenia i kopie zapasowe tych hostów oraz
rejestruje urządzenia w grupach, na które pozwala administrator floty, ale nie
widzi niczego z mastera, CA ani innych node'ów. Logowanie to hasło plus
certyfikat klienta z CA floty lub WebAuthn, a każda zmiana trafia do dziennika
audytu.

## Dołączanie maszyny { #joining-a-machine }

Obie ścieżki zostają:

- **Obraz ISO dla konkretnego hosta** z jego rolą (dzisiejsze
  `build --offline`), do instalacji offline.
- **Ogólny obraz ISO bootstrap** dla każdego targetu, budowany raz przez CI i
  bez żadnych sekretów. Przy pierwszym rozruchu pobiera swoją rolę z
  kontrolera za pomocą jednorazowego **tokenu dołączenia**. Ręcznie
  zainstalowana maszyna lub VPS dołącza jedną linią:
  `curl https://control.<host>.<tld>/join/<token> | sudo bash`.

Każda maszyna z linii CoreOS ma uruchamiać **jeden obraz bootc**, a rola ma
przychodzić przy pierwszym rozruchu.

## Federacja i multi-hop { #federation-and-multi-hop }

Sieci, które ufają nawzajem swoim CA i delegują sobie nazwy, stają się
nawzajem swoimi klientami. Z trzecim trybem wyjścia master jednej sieci może
wychodzić do Internetu przez mastera innej: **multi-hop**, w którym drugi
master widzi tylko pierwszego. Kilka masterów prowadzonych przez jednego
operatora daje wtedy własną usługę VPN: mastery wejściowe w jednym kraju,
mastery wyjściowe w innych, Tor w środku.

## Sad { #the-orchard }

Sad (orchard) jest dla ludzi, którzy prowadzą wiele masterów dla innych. To
osobna aplikacja lub wtyczka kiwi-server, która tworzy VPS-y przez API
dostawców, przekazuje każdemu masterowi jego instalację i token rejestracji,
zbiera heartbeat od każdego mastera (wersja, stan, dysk, ostatnia
aktualizacja) i wdraża aktualizacje, przesuwając tagi obrazów dla każdego
kanału.

Nie może zalogować się na mastera, odczytać floty ani dotknąć node'a. Node
sterujący każdego najemcy, u niego w domu, przechowuje jego sieć. Dostawca
hostujący mastera nie może jej odczytać i uruchamia jedną maszynę wirtualną na
najemcę. Obsługa netcup w kiwi-server (`kiwi-server
vps`, *zbudowane*) to pierwszy element jego sterownika dostawców.

## Również na liście { #also-on-the-list }

Zapasowy master, podman bez roota, IPv6 od końca do końca, płytki ARM, zakresy
portów i moduł do gier oraz odtwarzanie danych node'a przy pierwszym
rozruchu.
