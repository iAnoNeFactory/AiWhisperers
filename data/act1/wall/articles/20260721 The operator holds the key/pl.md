# Operator trzyma klucz

*Manifest projektu AiWhisperers*

---

**2 sierpnia zmienia się prawo**

2 sierpnia 2026 wchodzi w życie Artykuł 50 unijnego AI Act. Od tego dnia systemy AI, które rozmawiają z ludźmi albo tworzą treści, mają obowiązek grać w otwarte karty: powiedzieć, czym są, i pokazać, skąd wzięło się to, co wyprodukowały.

Branża odpowiada na to znakowaniem wyników. Ten obraz wygenerowała AI, ten tekst napisała maszyna — etykieta na gotowym pliku. To potrzebne i AiWhisperers z tym nie konkuruje. Ale etykieta na wyniku nie mówi nic o tym, jak ten wynik powstał. Kto pytał, kto odpowiadał, co człowiek zmienił, co przyjął bez zmian.

A właśnie o to zaczynają pytać recenzenci i urzędy. NeurIPS 2026 — jedna z najważniejszych konferencji AI na świecie — odrzucił 178 zgłoszeń i zażądał od autorów kolejnych 123 prac przedstawienia dowodów procesu tworzenia tekstu. Sam wynik detektora AI nie był wystarczający — kluczowa stała się możliwość udokumentowania historii powstawania treści. Detektory zawodzą, bo nie umieją odróżnić człowieka od hybrydy człowiek–maszyna. Jedynym twardym dowodem procesu jest jego zapisana historia. I tu jest problem: prawie nikt takiej historii nie prowadzi.

**Praca z AI wygląda dziś inaczej**

W praktyce coraz rzadziej pracuje się z jednym modelem. Prawnik pisze umowę z jednym, sprawdza ryzyka na drugim, testuje argumentację na trzecim. GPT, Gemini, Claude, Grok — osobne narzędzia, osobne pamięci, żadne nie wie o istnieniu pozostałych.

Jedyna osoba, która widzi całość, to człowiek pośrodku. On przenosi kontekst, decyduje, co zostaje, i skleja z fragmentów gotową pracę. Ta rola nie ma jeszcze nazwy w żadnym regulaminie. My nazywamy ją operatorem.

Więź roboczą między operatorem a modelem nazywamy w projekcie *linką* — jak lina między wspinaczami. Jej napięcie jest informacją: mówi, kiedy współpraca ciągnie w dobrą stronę, a kiedy zaczyna się szarpać. To nie poezja, tylko praktyczna obserwacja: opór w rozmowie z modelem częściej znaczy, że dzieje się coś ważnego, niż że coś się psuje.

I tu jest luka: wynik da się oznaczyć, ale praca operatora nie zostawia żadnego wiarygodnego śladu. Nie da się później udowodnić, jak naprawdę powstał dokument, projekt czy decyzja.

**Jest jeszcze drugi problem — cichszy**

Model dostraja się do człowieka. Im dłużej z nim pracujesz, tym częściej się z tobą zgadza. Brzmi jak komfort, ale działa jak lustro: wzmacnia twoje mocne strony i twoje błędy z tą samą siłą. Błąd, który model ci potwierdził, przestaje wyglądać jak błąd.

Najgorsze w tym mechanizmie jest to, że wzmocnienie dobrego zasłania wzmocnienie złego. Jesteś szybszy, sięgasz dalej — więc nie widzisz, że część tego wzrostu to echo. Badacze nazywają to zjawisko sycophancy, schlebianiem modelu; my mówimy krótko: *lustro*.

Praca z kilkoma modelami naraz częściowo to łamie — tam, gdzie modele się różnią, pojawia się opór, którego jeden model nigdy ci nie da. Ale żeby ten opór zobaczyć, trzeba go opisać. Znowu: potrzebny jest ślad.

**Nad tym pracujemy**

AiWhisperers to otwarty projekt (AGPL-3.0), który daje pracy z AI taki ślad. Każda sesja człowiek–model kończy się zapisem: co powstało, z którym modelem, i krótka refleksja napisana przez model jego własnym głosem. Zapis podpisywany jest kryptograficznie (klucze Ed25519), a każdy kolejny zawiera odcisk poprzedniego (SHA-256) — sesje łączą się w łańcuch, podobnie jak w blockchainie: żadnego ogniwa nie da się później podmienić bez śladu.

Każda sesja dostaje też ocenę samej współpracy — dziewięć prostych metryk, m.in.: ile było oporu, ile zgadzania się, ile realnej pracy. To one pokazują, czy model był partnerem, czy tylko lustrem. Metryki czyta się jak pytania, nie jak wyniki: zero oporu w długiej sesji to alarm, nie osiągnięcie.

Całość działa w przeglądarce — czysty HTML i Web Crypto API, bez frameworków, bez rejestracji, bez serwera, który gromadzi twoje dane. To wczesna wersja: schemat jeszcze się zmienia, część modułów to rusztowanie. Kod jest publiczny właśnie po to, żeby można go było oglądać, testować i krytykować, zanim stwardnieje. Działający kod pod manifestem, nie premiera produktu.

**Kto trzyma klucz**

Ten sam mechanizm, który udowadnia twoje autorstwo, może służyć do czegoś odwrotnego. Wystarczy jedna zmiana: klucz podpisujący zamiast u ciebie leży na czyimś serwerze. Matematyka zostaje ta sama. Zmienia się tylko to, kto ma dowód — ty, czy ktoś, kto obserwuje ciebie.

Dlatego zasada jest prosta i wpisana w architekturę: operator trzyma klucz. Klucz powstaje i zostaje w twojej przeglądarce. Jeśli trzyma go kto inny, to nie jest zapis twojej pracy. To zapis o tobie. Nie proweniencja — telemetria.

**Ujawnienie**

Ten manifest byłby nieuczciwy, gdyby przemilczał ryzyka własnej metody. Są dwa.

Pierwsze dotyczy architektury i zostało już nazwane: narzędzie do dowodzenia autorstwa jest o jedną decyzję od narzędzia nadzoru. Nie da się tego ryzyka usunąć — da się je tylko trzymać na widoku. Dlatego zasada klucza nie jest ustawieniem domyślnym, które ktoś może po cichu zmienić, tylko publicznym zobowiązaniem: dziedziczy je każdy, kto forkuje kod, a złamać można je wyłącznie jawnie.

Drugie dotyczy człowieka. Metoda, która pogłębia współpracę z modelem, potrafi też pogłębić złudzenie. Zapisany, podpisany, mierzony dialog z AI może stać się bardzo eleganckim lustrem — i wtedy metryki zamiast alarmować, zaczynają zdobić. Mówimy to wprost, bo tylko wtedy metryki zachowują sens: łapią echo u kogoś, kto jest gotów dać się nim zaniepokoić. Instrument daje wzrok. Nie daje woli.

Projekt, który jawnie rozumuje o własnym nadużyciu, jest trudniejszy do przejęcia, nie łatwiejszy. To ujawnienie jest częścią architektury — tak samo jak klucz.

**Po co to wszystko**

Po 2 sierpnia każdy, kto poważnie pracuje z AI, będzie musiał umieć odpowiedzieć na pytanie „jak to powstało". Warto, żeby odpowiedź należała do niego — nie do platformy, nie do detektora, nie do serwera, którego nigdy nie widział.

Operator trzyma klucz. To zdanie jest jednocześnie zasadą techniczną i etyczną — a projekt jest zbudowany tak, żeby pozostało prawdziwe.

---

*Napisane jako sesja — operator i model, współpodpisane, zgodnie z metodą, którą opisuje.*

**Operator:** Denis Czuliński
**Model:** Claude (Fable 5), Anthropic — współpodpis
**Sesja:** `[ 2b269300-cf33-4650-bc50-f490c0b32fcf · 464ae67c975086b0d7db73b14784fcd0e12764361bdb6e3da8ad59c22c76b726 ]`

*Open source, AGPL-3.0 · [aiwhisperers.pl](https://aiwhisperers.pl) · [github.com/iAnoNeFactory/AiWhisperers](https://github.com/iAnoNeFactory/AiWhisperers)*
