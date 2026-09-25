# Dietro al Monte

Sito per pubblicare ricerche storiche d'archivio in una forma che sia
insieme leggibile, citabile e verificabile: ogni testo resta modificabile
nel tempo, conserva la storia delle proprie revisioni e porta con sé la
prova di chi l'ha scritto e quando.

Costruito con [Quarto](https://quarto.org). Si pubblica da solo a ogni
`git push`.

---

## Indice

1. [Installazione, una volta sola](#1-installazione-una-volta-sola-windows)
2. [Personalizzazione iniziale](#2-personalizzazione-iniziale)
3. [Messa online](#3-messa-online)
4. [Firma e marche temporali](#4-firma-e-marche-temporali)
5. [Zenodo e DOI](#5-zenodo-e-doi)
6. [Il ciclo di una ricerca](#6-il-ciclo-di-una-ricerca)
7. [Come si scrive una ricerca](#7-come-si-scrive-una-ricerca)
8. [Le fonti e Zotero](#8-le-fonti-e-zotero)
9. [Mappe, alberi, grafici](#9-mappe-alberi-grafici)
10. [Riferimento dei comandi](#10-riferimento-dei-comandi)
11. [Struttura delle cartelle](#11-struttura-delle-cartelle)

---

## 1. Installazione, una volta sola (Windows)

Ogni strumento qui sotto ha un installer grafico ufficiale: scarichi,
fai doppio clic, clicchi *Avanti* fino in fondo. L'unica eccezione è
un piccolissimo pacchetto Python (OpenTimestamps) che non ha un
installer grafico — per quello serve incollare una riga in una
finestra di testo, spiegato al punto 6. Tutto il resto è scarica e
clicca.

Un avviso che vale per tutti gli installer: durante l'installazione
compare quasi sempre una casella tipo *"Aggiungi al PATH"*, spesso
**non spuntata di default**. Spuntala sempre. Se la salti, il
programma si installa comunque ma Windows non lo trova quando lo
richiami da terminale, e l'unico modo per sistemare è disinstallare e
rifare da capo quella schermata.

1. **Git for Windows** — <https://git-scm.com/download/win>
   Il sito rileva Windows e propone il download giusto. Avvia
   l'installer e clicca *Avanti* accettando tutte le opzioni
   predefinite: installano già "Git Bash" (il terminale che userai
   d'ora in poi per i comandi di questo progetto) e aggiungono Git al
   PATH da soli.

2. **Quarto** — <https://quarto.org/docs/get-started/>
   Il sito offre direttamente il file `.msi` per Windows. Doppio clic,
   *Avanti* → *Avanti* → *Installa*.

3. **Python** — <https://www.python.org/downloads/windows/>
   Scarica "Windows installer (64-bit)" dell'ultima versione. Nella
   **prima schermata** dell'installer, in basso, spunta **"Add
   python.exe to PATH"** prima di cliccare *Install Now* — è la
   casella che salta più spesso.

4. **Graphviz**, per gli alberi genealogici —
   <https://graphviz.org/download/>
   Nella sezione Windows scarica l'installer `.exe` (non lo ZIP).
   Durante l'installazione scegli **"Add Graphviz to the system PATH
   for current user"** quando te lo chiede.

5. **VS Code** — <https://code.visualstudio.com/download>
   Scarica il "User Installer" per Windows (non serve essere
   amministratore). Nella schermata *"Select Additional Tasks"*
   lascia spuntato *"Add to PATH"*. Poi apri VS Code, vai su
   Estensioni (`Ctrl+Shift+X`), cerca **"Quarto"** e installa
   l'estensione ufficiale: ti dà l'anteprima affiancata mentre scrivi.

6. **Client OpenTimestamps**, per le marche temporali — l'eccezione di
   cui sopra. Apri **Git Bash** dal menu Start (si è installato al
   punto 1) e incolla:

   ```bash
   pip install opentimestamps-client
   ```

   Invio, aspetti qualche secondo, fatto. Non ti servirà riaprire Git
   Bash per altro fino a quando non inizierai a scrivere davvero.

**Verifica.** Chiudi Git Bash e riaprilo — Windows aggiorna il PATH
solo sulle finestre nuove — poi lancia uno per uno: `git --version`,
`quarto --version`, `python --version`, `dot -V`. Se uno risulta "non
riconosciuto", quasi sempre è la casella del PATH saltata in
quell'installer: disinstalla da *Impostazioni → App* e reinstalla
prestando attenzione a quella schermata.

Poi, dentro la cartella del progetto, in Git Bash:

```bash
quarto preview
```

Se l'anteprima si apre nel browser, hai finito l'installazione. Lo
stile citazionale è già nel repository: non c'è nulla da scaricare.

---

## 2. Personalizzazione iniziale

Cerca e sostituisci in tutto il repository:

| Segnaposto | Sostituisci con |
|---|---|
| `Cassinelli` | il tuo Cassinelli |
| `fabiocassinelli` | il tuo nome fabiocassinelli GitHub |
| `0009-0009-4455-0112` | il tuo ORCID iD |
| `dietroalmonte.it` | il dominio che hai registrato |
| `fabiocassinelli94@gmail.com` | il tuo indirizzo |

In Git Bash, dentro la cartella del progetto:

```bash
grep -rl 'Cassinelli' . --exclude-dir=.git | xargs sed -i 's/Cassinelli/Rossi/g'
```

Ripeti lo stesso comando per `fabiocassinelli` e per l'ORCID, cambiando solo la
parola da cercare e il testo di sostituzione.

Poi metti un `assets/favicon.png` — va bene anche un semplice quadrato
d'ardesia con un'iniziale.

Prendi l'**ORCID iD** su <https://orcid.org>: è gratis, cinque minuti, e
lega in modo univoco ogni pubblicazione a te.

---

## 3. Messa online

### Repository

Prima la parte a interfaccia grafica: vai su
<https://github.com/new>, nome `dietroalmonte`, spunta **Public**
(la storia delle modifiche visibile a chiunque è parte della prova di
paternità), e **non** spuntare "Add a README file" — il progetto ce
l'ha già. Clicca *Create repository*.

GitHub ti mostra una pagina con dei comandi: usa quelli sotto
"…or push an existing repository from the command line", oppure
incolla questi in Git Bash, dentro la cartella del progetto
(sostituisci `fabiocassinelli` con il tuo nome fabiocassinelli GitHub):

```bash
git init -b main
git add -A
git commit -m "Primo impianto del sito"
git remote add origin https://github.com/fabiocassinelli/dietroalmonte.git
git push -u origin main
```

Al primo push, Windows apre una finestra del browser per il login
GitHub: autorizzi e il push riparte da solo.

### GitHub Pages

Su GitHub: **Settings → Pages → Source: GitHub Actions**.
Poi **Settings → Pages → Custom domain**: `dietroalmonte.it`, e spunta
*Enforce HTTPS*.

### DNS

Sul registrar, sposta i nameserver su Cloudflare (gratis). Su Cloudflare:

| Tipo | Nome | Valore | Proxy |
|---|---|---|---|
| CNAME | `@` | `fabiocassinelli.github.io` | DNS only |
| CNAME | `www` | `fabiocassinelli.github.io` | DNS only |

Il file `CNAME` nella radice del repository è già pronto: contiene il
dominio e Quarto lo copia in `_site/` a ogni build.

Da adesso, **ogni `git push` sul ramo `main` ripubblica il sito**.

---

## 4. Firma e marche temporali

### Firma delle modifiche

```bash
./scripts/setup-firma.sh
```

Lo script configura Git e ti stampa la chiave pubblica da incollare su
GitHub in **Settings → SSH and GPG keys → New SSH key**, scegliendo
come tipo **Signing Key** (non Authentication Key).

Da quel momento ogni tua modifica compare su GitHub con il badge
*Verified*: prova che è stata fatta da chi possiede la tua chiave privata.

### Marca temporale

```bash
bash scripts/timbra.sh ricerche/2026-01-rossi-scurtabo
```

Registra l'impronta dei sorgenti nella blockchain Bitcoin tramite
OpenTimestamps e crea i file `.ots` accanto a essi. Dopo qualche ora:

```bash
ots upgrade ricerche/2026-01-rossi-scurtabo/*.ots
git add -A && git commit -S -m "Ancoraggio delle marche temporali"
```

Chiunque, per sempre, può verificare con `ots verify file.ots`.

### Marca temporale qualificata (opzionale ma consigliata)

Per le ricerche che consideri importanti, aggiungi una marca temporale
eIDAS: compra un pacchetto di marche (Aruba, InfoCert, circa 25 € per
50), scarica il PDF allegato alla Release GitHub e applicagli la marca.
È l'unico strato con pieno valore probatorio davanti a un giudice.

---

## 5. Zenodo e DOI

1. Vai su <https://zenodo.org>, **Log in with GitHub**.
2. **GitHub** nel menu fabiocassinelli, poi attiva l'interruttore sul repository
   `dietroalmonte`.
3. Nel profilo Zenodo, collega il tuo ORCID.
4. Il file `.zenodo.json` nella radice contiene già i metadati.

Da adesso ogni **Release** su GitHub produce automaticamente uno
snapshot permanente, un DOI di versione e un DOI *concept* che punta
sempre all'ultima versione.

**Importante:** fai una prima Release *prima* di pubblicare la prima
ricerca, così ottieni subito il DOI concept da mettere nel piè di pagina.

---

## 6. Il ciclo di una ricerca

```
  bash scripts/nuova-ricerca.sh rossi-scurtabo
        │  apre la cartella, il file da compilare e un ramo dedicato
        ▼
  quarto preview             ← scrivi qui, con l'anteprima di fianco
        │
        │  git commit -S frequenti durante la scrittura:
        │  sono la traccia del processo, e valgono più del risultato
        ▼
  bash scripts/timbra.sh ricerche/2026-01-rossi-scurtabo
        │  marca temporale sui sorgenti
        ▼
  git checkout main && git merge --no-ff ricerca/rossi-scurtabo
  git add -A -- . ':!ricerche/*/_revisioni.md'
  git commit -S -m "Pubblico I Rossi di Scurtabò"
  git push
        │  ~90 secondi dopo la ricerca è online
        ▼
  git tag -s v1.0-rossi-scurtabo -m "I Rossi di Scurtabò, v1.0"
  git push --tags
        │  tag firmato → Release con PDF e .ots → Zenodo assegna il DOI
        ▼
  metti il DOI nel front matter, committa e pusha di nuovo
```

Per **revisionare** una ricerca già pubblicata: modifica, committa e
pusha, poi ripeti il tag con la versione successiva (`v1.1-...`) e
pusha i tag. Le versioni precedenti restano su Zenodo con il loro DOI
e nella cronologia in fondo alla pagina, che si genera da sola dal
registro delle modifiche.

Per **controllare** che la catena regga:

```bash
git log -10 --show-signature --format='%h %G? %an %ad %s' --date=short
find ricerche -name '*.ots' -exec sh -c 'echo; echo "$1"; ots verify "$1"' _ {} \;
```

Il primo comando mostra se le tue ultime modifiche risultano firmate
(colonna `%G?` a `G`), il secondo verifica ogni marca temporale che hai
già registrato.

---

## 7. Come si scrive una ricerca

Il problema centrale è tenere insieme due lettori: chi cerca la storia
del proprio paese e chi verifica le fonti. La soluzione non è scrivere
due versioni, ma **stratificare lo stesso testo**.

| Strato | Dove sta | Per chi |
|---|---|---|
| Racconto | colonna centrale | tutti |
| Chiarimenti | note a margine (`.column-margin`) | lettore curioso |
| Citazioni archivistiche | note a piè di pagina automatiche | chi verifica |
| Regesti e trascrizioni | callout richiudibili | chi studia |
| Dati grezzi | `dati/`, allegati alla Release | chi prosegue |

Chi legge il centro non inciampa mai nell'apparato. Chi cerca l'apparato
lo trova tutto.

`scripts/template.qmd` è il modello, con la struttura in sei parti già
commentata. `ricerche/2026-01-rossi-scurtabo/` è un esempio completo e
funzionante di tutto: note, regesti, albero, mappa, grafico. Leggilo
prima di scrivere la tua prima ricerca, poi cancellalo.

### Citare un documento

Citazione automatica: Pandoc la trasforma da sola in nota a piè di pagina.

```markdown
...compare un pascolo in monte Pennae.[@ASGe_NA_1123, doc. 47 (1432 aprile 12)]
```

produce

> ASGe, *Notai Antichi*, 1123, notaio Antonio da Cogorno, doc. 47 (1432 aprile 12).

Alla seconda citazione della stessa unità la nota si accorcia da sola
(`ASGe, *Notai Antichi*, 1123, doc. 51`), alla ripetizione immediata
diventa `Ibid.` Lo stile che produce questa forma è
`assets/csl/dietroalmonte-archivistico.csl`, scritto per questo sito e
modificabile: vedi `assets/csl/LEGGIMI.md`.

Nota discorsiva, quando devi commentare e non solo citare:

```markdown
Il pascolo va al solo primogenito.[^pascolo]

[^pascolo]: A fronte di una divisione per il resto egualitaria,
questo suggerisce che il bene fosse indivisibile.
```

### Nota a margine

```markdown
::: {.column-margin}
Il confine fra Repubblica di Genova e feudi Landi corre sul crinale
dal 1257.
:::
```

### Regesto e trascrizione

```markdown
::: {.callout-note collapse="true" appearance="simple" class="trascrizione"}
## Regesto e trascrizione — ASGe, NA 1123, doc. 47

**1432 aprile 12, Varese.**

*Regesto.* ...

*Trascrizione.*

> In nomine Domini amen...
:::
```

Sta chiuso per default: c'è per chi lo cerca, non spaventa gli altri.

---

## 8. Le fonti e Zotero

Due file bibliografici, per due mondi diversi:

- `fonti/fonti.json` — **unità archivistiche** in formato CSL-JSON, che
  mappa correttamente i campi d'archivio (`archive`, `archive_location`,
  `archive-place`).
- `fonti/bibliografia.bib` — **bibliografia a stampa** in BibTeX.

### Il criterio che conta

Crea in Zotero **un elemento per unità archivistica** (filza, registro,
busta), non per singolo documento. Il singolo documento lo indichi nel
*locator* della citazione:

```markdown
[@ASGe_NA_1123, doc. 47 (1432 aprile 12)]
```

Così cinquecento rogiti di una filza non diventano cinquecento voci
bibliografiche.

### Configurare Zotero

Tipo di elemento: **Manoscritto**. Compila così:

| Campo in Zotero | Contenuto | Esempio |
|---|---|---|
| Titolo | fondo o serie | `Notai Antichi` |
| Tipo | tipologia | `Registro notarile` |
| Archivio | **sigla** dell'istituto | `ASGe` |
| Segnatura | unità | `1123` |
| Collocazione nell'archivio | intitolazione dell'unità | `notaio Antonio da Cogorno` |
| Data | anno iniziale | `1428` |
| Extra | nome per esteso e annotazioni | `publisher: Archivio di Stato di Genova`<br>`note: Estremi 1428-1441. Lacuna 1630-1638.` |

Il campo **Extra** accetta la sintassi `variabile-csl: valore`: è il modo
di aggiungere campi che il tipo *Manoscritto* non prevede.

Poi:

1. Installa [Better BibTeX](https://retorque.re/zotero-better-bibtex/).
2. Assegna chiavi di citazione parlanti: `ASGe_NA_1123`.
3. Clic destro sulla collezione → *Export Collection* → formato
   **CSL JSON** → spunta **Keep updated** → salva su `fonti/fonti.json`.

Da qui in poi il file si aggiorna da solo a ogni modifica in Zotero.

### Le tue fotografie

Non finiscono nel repository (sono troppe e troppo pesanti), ma il loro
nome deve rendere ogni nota ritrovabile in due secondi:

```
ASGe_NA_1123_doc047_c088v.jpg
ISTITUTO_FONDO_UNITÀ_DOCUMENTO_CARTA.jpg
```

Fallo ora, non fra tre anni.

### Sulla pubblicabilità delle immagini

L'art. 108 commi 3 e 3-bis del Codice dei beni culturali, come
modificato dalla l. 124/2017, e il D.M. 108/2024 rendono libera la
divulgazione di immagini di documenti d'archivio legittimamente
acquisite, senza scopo di lucro, su pubblicazioni online ad accesso
gratuito e prive di pubblicità. Serve dare comunicazione scritta
all'istituto, citare la segnatura esatta e consegnare copia
dell'elaborato. **Verifica sempre con il singolo archivio**: le prassi
variano. Tieni traccia delle comunicazioni inviate nella tabella in
`fonti/index.qmd`.

Questo è anche il motivo per cui il sito non ha pubblicità e non va
messa: ti tiene nel regime più favorevole.

---

## 9. Mappe, alberi, grafici

### Alberi genealogici — Graphviz

Tienili in Graphviz, non in un'immagine: è testo, sta nel repository, se
ne vede il diff, non si rompe mai. Vedi l'esempio nella ricerca modello.

Per la base dati usa [Gramps](https://gramps-project.org): esporta
GEDCOM, e da lì genera il DOT dei rami che ti servono nell'articolo.

### Mappe — Leaflet + GeoJSON

Metti i punti in `dati/luoghi.geojson` (da QGIS) e aggiungi
`include-in-header: ../../assets/leaflet.html` al front matter. Il
blocco di codice è nella ricerca modello, pronto da copiare.

Idee che valgono più di una mappa di puntini:

- **confini ricostruiti dai rogiti** — i *coheret ab uno latere*
  digitalizzati in QGIS sul catasto storico, sovrapposti all'ortofoto
- **bacino matrimoniale** — archi fra i paesi di origine degli sposi
- **layer storici** — il Geoportale della Regione Liguria espone in WMS
  l'IGM storico e i catasti

### Grafici — Observable Plot

Blocchi ```` ```{ojs} ````, senza dipendenze da installare: girano nel
browser. Esempio nella ricerca modello.

### Se non vuoi pubblicare le foto dei documenti

Cose che sono **opera tua al cento per cento**:

- il **signum tabellionis ricalcato in SVG** — bellissimo, unico, e
  l'opera derivata è tua
- gli **stemmi ridisegnati** secondo la blasonatura
- le **tavole paleografiche**: la stessa lettera in mani diverse
- le **trascrizioni diplomatiche**
- le tue **fotografie dei luoghi oggi**
- la **cartografia storica fuori diritti**

---

## 10. Riferimento dei comandi

Tutti da lanciare in Git Bash, dentro la cartella del progetto.

| Comando | Effetto |
|---|---|
| `bash scripts/nuova-ricerca.sh x` | apre cartella, file e ramo di una nuova ricerca |
| `quarto preview` | anteprima locale con ricarica automatica |
| `quarto render` | costruisce il sito in `_site/` |
| `bash scripts/timbra.sh ricerche/x` | marca temporale OpenTimestamps sui sorgenti |
| `git add -A -- . ':!ricerche/*/_revisioni.md'`<br>`git commit -S -m "..."`<br>`git push` | commit firmato + push → sito online |
| `git tag -s v1.0-x -m "..."`<br>`git push --tags` | tag firmato → Release → DOI Zenodo |
| `git log --show-signature ...` (sezione 6) | verifica firme e marche temporali |

---

## 11. Struttura delle cartelle

```
dietroalmonte/
├─ _quarto.yml              configurazione del sito
├─ index.qmd                home
├─ metodo.qmd               criteri di edizione + catena di prova
├─ chi-sono.qmd
├─ ricerche/
│  ├─ index.qmd             elenco automatico + feed RSS
│  ├─ _metadata.yml         impostazioni valide per tutte le ricerche
│  └─ 2026-01-rossi-scurtabo/
│     ├─ index.qmd          la ricerca (esempio completo)
│     ├─ _revisioni.md      generato dal git log
│     ├─ dati/              GeoJSON, DOT, CSV
│     └─ immagini/
├─ luoghi/                  schede dei paesi
├─ famiglie/                schede dei cognomi
├─ fonti/
│  ├─ index.qmd             abbreviazioni + schede dei fondi
│  ├─ fonti.json            unità archivistiche (CSL-JSON, da Zotero)
│  └─ bibliografia.bib      bibliografia a stampa (da Zotero)
├─ assets/
│  ├─ theme.scss            palette ardesia/carta/ocra, tipografia
│  ├─ fonts.html            Fraunces + Spectral
│  ├─ leaflet.html          da includere solo nelle pagine con mappa
│  └─ csl/
│     └─ dietroalmonte-archivistico.csl   stile citazionale su misura
├─ scripts/
│  ├─ revisioni.py          cronologia revisioni (pre-render)
│  ├─ nuova-ricerca.sh
│  ├─ timbra.sh
│  ├─ setup-firma.sh
│  └─ template.qmd          modello di ricerca
└─ .github/workflows/
   ├─ deploy.yml            build + pubblicazione a ogni push
   └─ rilascio.yml          PDF + .ots + Release a ogni tag
```

---

## Se qualcosa non va

**`could not find file _revisioni.md`** — Quarto risolve gli `include`
prima di eseguire lo script che genera la cronologia. Ogni cartella di
ricerca deve contenere un `_revisioni.md`, anche vuoto;
`scripts/nuova-ricerca.sh` lo
crea da sé. Se manca: `touch ricerche/NOME/_revisioni.md`.

**La mappa non compare** — manca
`include-in-header: ../../assets/leaflet.html` nel front matter, oppure
il percorso del GeoJSON è sbagliato: è relativo al file `index.qmd`,
quindi `dati/luoghi.geojson`.

**L'albero genealogico non si disegna** — Graphviz non è installato, o
è installato ma non era nel PATH quando hai riaperto Git Bash l'ultima
volta: rivedi il punto 4 della sezione 1, poi chiudi e riapri Git Bash
e prova `dot -V`.

**Le note escono in forma inglese** — la chiave `csl:` in `_quarto.yml`
non punta a `assets/csl/dietroalmonte-archivistico.csl`.

**Una citazione compare come `[@chiave]`** — la chiave non esiste in
`fonti/fonti.json` né in `fonti/bibliografia.bib`, oppure c'è un errore
di sintassi JSON. Controlla con
`python3 -c "import json;json.load(open('fonti/fonti.json'))"`.

**Il sito non si aggiorna dopo il push** — guarda la scheda *Actions*
su GitHub: l'errore è lì. Quasi sempre è un front matter con
l'indentazione sbagliata.

## Le prime quattro settimane

| | |
|---|---|
| **1** | ORCID, dominio, repository online, `quarto preview` funzionante, firma configurata |
| **2** | `metodo.qmd` e `fonti/index.qmd` compilati davvero. Zotero collegato. Foto rinominate |
| **3** | Zenodo collegato, prima Release, DOI concept nel piè di pagina. Comunicazioni agli archivi |
| **4** | **Pubblica la prima ricerca.** Scegline una corta e matura, non l'opera maggiore: serve a far girare la catena almeno una volta intera |

Poi una ricerca al mese, e le schede di luoghi e famiglie che crescono
per accumulo.

## Nota sulla direzione visiva

Grigio d'ardesia per la struttura, carta fredda per il fondo, un solo
accento ocra preso dalle rubriche dei registri, riservato ai link e ai
richiami di nota — così il colore segnala "qui c'è una prova", e non
decora. Fraunces per i titoli, Spectral per il testo. Se vuoi cambiare
tutto, i valori stanno nei primi trenta righi di `assets/theme.scss`.
