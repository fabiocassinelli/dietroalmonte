# Dietro al Monte

Il sito su cui pubblico le mie ricerche d'archivio: <https://dietroalmonte.it>.
Costruito con [Quarto](https://quarto.org), pubblicato da GitHub Actions su
GitHub Pages.

**Il lavoro di tutti i giorni è in tre gesti:** scrivo → guardo l'anteprima
(`Ctrl+Shift+K`) → premo **Commit** nel pannello *Source Control* di VS Code.
Come si scrive è spiegato in una pagina: [GUIDA.md](GUIDA.md).

Tutto il resto succede da solo su GitHub, a ogni Commit:

| Che cosa | Come |
|---|---|
| Il sito viene ricostruito e messo online | lavoro «Costruisci il sito» + «Metti online» |
| In fondo a ogni ricerca compare la cronologia delle revisioni | letta dalla storia delle modifiche |
| Tutti i file ricevono una marca temporale OpenTimestamps | salvata nel ramo `marche-temporali` |
| Le ricerche con una nuova `versione:` diventano PDF + Release | Zenodo le archivia e assegna il DOI |

---

## Già fatto

Questi passaggi li hai completati: non vanno rifatti.

1. **Programmi installati** su Windows: Git for Windows, Quarto, Python,
   Graphviz, VS Code con l'estensione Quarto, client OpenTimestamps.
   `quarto preview` funziona.
2. **Dati personali inseriti** nei file (nome, utente GitHub, dominio, e-mail).
3. **Messa online predisposta:**
   - repository pubblico <https://github.com/fabiocassinelli/dietroalmonte>;
   - GitHub Pages con fonte **GitHub Actions** e dominio personalizzato;
   - dominio registrato su Aruba, nameserver su Cloudflare;
   - i due record DNS tolti di proposito: il sito resta irraggiungibile
     finché non decidi tu (vedi il punto 9).

---

## Da fare, in quest'ordine

### 1. Sostituisci la vecchia cartella con questa

1. Fai una copia della cartella attuale del progetto (copia e incolla sul
   Desktop): è la tua rete di sicurezza.
2. Nella cartella del progetto, in Esplora file attiva
   *Visualizza → Mostra → Elementi nascosti*. Cancella **tutto tranne la
   cartella `.git`** (è lei che contiene la storia e il collegamento a GitHub).
3. Estrai lì dentro il contenuto dello zip, in modo che `README.md` e
   `_quarto.yml` stiano direttamente nella cartella del progetto.
4. Aggiorna Quarto: scarica l'installer da <https://quarto.org/docs/download/>
   (versione 1.11 o successiva) e installalo sopra la versione che hai.
   È la stessa versione usata da GitHub per costruire il sito.
5. Apri la cartella in VS Code (*File → Apri cartella*). Apri `index.qmd` e
   premi `Ctrl+Shift+K`: deve comparire l'anteprima con la nuova home.

Nel pannello *Source Control* vedrai molti file modificati: è giusto così.
Non premere ancora Commit: prima i punti 2 e 3.

### 2. Metti il tuo ORCID

In VS Code premi `Ctrl+Shift+H` (*Cerca e sostituisci nei file*):
cerca `0009-0009-4455-0112`, sostituisci con il tuo ORCID iD, premi
*Sostituisci tutto*. Compare in sei file (piè di pagina, Chi sono, Metodo,
dati per Zenodo).

### 3. Attiva la firma delle modifiche

Doppio clic su **`Configura firma.bat`**. Crea una chiave dedicata, dice a
Git di firmare ogni modifica di questo progetto (anche quelle fatte da
VS Code) e apre la pagina di GitHub dove incollarla. Lì:

- *Title*: `Dietro al Monte - firma`
- *Key type*: **Signing Key** (non «Authentication Key»)
- *Key*: incolla con `Ctrl+V` (la chiave è già negli appunti) → *Add SSH key*.

La chiave non ha password, altrimenti VS Code non potrebbe firmare da
solo: la protegge l'accesso al tuo utente di Windows. Copia i due file
indicati dallo script su una chiavetta.

### 4. Prima pubblicazione di prova

1. In VS Code apri *Source Control* (`Ctrl+Shift+G`), scrivi un messaggio
   (per esempio «Nuovo impianto del sito») e premi **Commit**. In questo
   progetto Commit invia anche subito a GitHub (Commit e Sync insieme).
2. Su GitHub apri la scheda **Actions**: il lavoro *Pubblica il sito* deve
   finire con quattro spunte verdi (Costruisci il sito, Metti online,
   Marca temporale, Versioni citabili). Dura due o tre minuti.
3. Nella pagina del repository, accanto al messaggio dell'ultima modifica,
   deve comparire l'etichetta **Verified**; nel menu dei rami deve esserci
   il nuovo ramo `marche-temporali`.

Il sito resta irraggiungibile (i record DNS non ci sono), ma tutta la
catena ha già girato una volta. Se un lavoro è rosso, vedi «Se qualcosa
non va» in fondo.

### 5. Collega Zotero

Le citazioni archivistiche prendono i dati da due file che Zotero tiene
aggiornati da solo.

1. Installa [Zotero](https://www.zotero.org/download/) e il componente
   [Better BibTeX](https://retorque.re/zotero-better-bibtex/installation/).
2. Crea due collezioni: *Fonti d'archivio* e *Bibliografia*.
3. Clic destro su *Fonti d'archivio* → *Esporta collezione* → formato
   **Better CSL JSON** → spunta **Keep updated** → salva sopra
   `fonti/fonti.json`.
4. Clic destro su *Bibliografia* → *Esporta collezione* → formato
   **Better BibLaTeX** → spunta **Keep updated** → salva sopra
   `fonti/bibliografia.bib`.

**Una voce per unità archivistica** (filza, registro, busta), non per
documento: il documento si indica nella citazione. Tipo di elemento
*Manoscritto*, compilato così:

| Campo in Zotero | Contenuto | Esempio (inventato) |
|---|---|---|
| Titolo | fondo o serie | `Notai Antichi` |
| Tipo | tipologia | `Registro notarile` |
| Archivio | **sigla** dell'istituto | `ASGe` |
| Segnatura | unità | `1123` |
| Collocazione nell'archivio | intitolazione dell'unità | `notaio X` |
| Data | anno iniziale | `1428` |
| Extra | `publisher: Archivio di Stato di Genova` e, a capo, `note: Estremi 1428-1441.` | |

Chiave di citazione parlante (campo *Citation key*): `ASGe_NA_1123`.
Dettagli sullo stile: `assets/csl/LEGGIMI.md`.

### 6. Collega Zenodo (prima di creare la prima versione citabile)

1. Vai su <https://zenodo.org> → *Log in* → **GitHub**.
2. Menu del profilo (in alto a destra) → **GitHub** → **Sync now**.
3. Trova `fabiocassinelli/dietroalmonte` e attiva l'interruttore.
4. Menu del profilo → *Linked accounts*: collega il tuo **ORCID**.

Da quel momento ogni Release creata da GitHub viene archiviata da Zenodo
con un DOI. Va fatto **prima** della prima Release: quelle precedenti
Zenodo non le vede.

### 7. Completa le pagine fisse

Doppio clic su **`Controlla prima di pubblicare.bat`**: elenca tutti i
riquadri «DA COMPLETARE». Sono promemoria con l'esempio esatto di che cosa
scrivere; si vedono solo nell'anteprima e **sul sito pubblico vengono tolti
da soli**, quindi non c'è fretta. I più importanti prima di andare online:

- `metodo.qmd`: conferma i criteri di edizione;
- `fonti/index.qmd`: sigle, schede dei fondi, paragrafo sulle riproduzioni;
- `luoghi/` e `famiglie/`: le schede.

### 8. Pubblica la prima ricerca: «Il delitto di Chilinella»

1. Scrivi il testo (in Word o nel `.qmd`: vedi [GUIDA.md](GUIDA.md)) e
   sostituisci ogni riquadro DA COMPLETARE con il tuo materiale.
2. Quando non ne resta nessuno, nella scheda in alto cancella la riga
   `draft: true` → Commit. La ricerca è pubblicata.
3. Quando la consideri citabile, nella scheda togli il `#` davanti a
   `versione: "1.0"` → Commit. GitHub crea da solo il PDF, la Release
   e il deposito su Zenodo.
4. Dopo qualche minuto apri Zenodo → menu del profilo → *GitHub*: accanto
   al repository c'è il DOI. Copialo nella scheda (`doi: "10.5281/zenodo.NNNNNNN"`)
   → Commit. Ora compare nel riquadro *Citazione*.

Per una versione riveduta: correggi, cambia in `versione: "1.1"`, Commit.

### 9. Riattiva il dominio

Quando il sito è pronto per essere visto:

1. **Cloudflare** → <https://dash.cloudflare.com> → `dietroalmonte.it` →
   **DNS → Records → Add record**, due volte:

   | Type | Name | Target | Proxy status |
   |---|---|---|---|
   | CNAME | `@` | `fabiocassinelli.github.io` | **DNS only** (nuvola grigia) |
   | CNAME | `www` | `fabiocassinelli.github.io` | **DNS only** (nuvola grigia) |

   La nuvola deve restare grigia: con quella arancione GitHub non riesce a
   rilasciare il certificato HTTPS.
2. **GitHub** → repository → **Settings → Pages**. In *Custom domain* deve
   esserci `dietroalmonte.it` (se il campo è vuoto scrivilo e premi *Save*).
   Aspetta la scritta *DNS check successful*: di solito pochi minuti.
3. Nella stessa pagina spunta **Enforce HTTPS**. Se la casella non è ancora
   attiva, GitHub sta preparando il certificato: può servire fino a un giorno.
4. Apri <https://dietroalmonte.it>.

**Per rimetterlo offline:** cancella di nuovo i due record su Cloudflare.
Il file `CNAME` del progetto non c'entra: con la fonte «GitHub Actions»
GitHub lo ignora, e il dominio vale solo se è scritto in *Settings → Pages*.
Ricostruire il sito, quindi, non lo rimette online né lo toglie.

Ricorda che il repository è pubblico: i testi, bozze comprese, sono
leggibili su GitHub anche quando il sito è offline. Fa parte della prova di
paternità (la storia delle modifiche è visibile a tutti).

### 10. Facoltativi

- **Marca temporale qualificata (eIDAS).** Per una ricerca a cui tieni:
  scarica il PDF dalla Release su GitHub e applicagli una marca temporale
  qualificata comprata da un prestatore italiano (per esempio Aruba o
  InfoCert, a pacchetti). Conserva il file marcato e scrivilo in fondo
  alla ricerca. È l'unico strato che la legge presume esatto fino a prova
  contraria; gli altri si verificano tecnicamente.
- **Software Heritage.** Su <https://archive.softwareheritage.org/save/>
  incolla l'indirizzo del repository: ne conserva una copia indipendente
  da GitHub.

---

## Dove sta che cosa

```
dietroalmonte/
├─ README.md, GUIDA.md           istruzioni
├─ Converti bozza Word.bat       ┐
├─ Nuova ricerca.bat             │ doppio clic
├─ Controlla prima di pubblicare.bat
├─ Configura firma.bat           ┘
├─ index.qmd, metodo.qmd, chi-sono.qmd
├─ ricerche/
│  └─ 2026-09-delitto-chilinella-1577/
│     ├─ index.qmd               la ricerca (scheda in alto + testo)
│     ├─ bozza.docx              la bozza di Word, se la usi
│     ├─ immagini/  dati/
│     └─ _revisioni.md           vuoto, ma deve esistere: lo riempie GitHub
├─ luoghi/  famiglie/  fonti/    schede e fonti (fonti.json, bibliografia.bib)
├─ _modelli/                     modelli ed esempio dei Rossi: mai pubblicati
├─ assets/                       grafica, caratteri, stile delle citazioni
├─ scripts/                      i programmi usati dai .bat e da GitHub
├─ .vscode/                      impostazioni e attività di VS Code
└─ .github/workflows/            che cosa fa GitHub a ogni Commit
```

## Se qualcosa non va

**Il lavoro «Costruisci il sito» è rosso.** Aprilo dalla scheda *Actions*:
il passo *Controlla i testi* dice in italiano che cosa non va. I casi
sono tre: una pagina non più bozza che contiene ancora segnaposto o la
scritta DA COMPLETARE fuori da un riquadro; una citazione `[@chiave]` che
non esiste in Zotero; una `versione:` scritta male. Correggi e rifai Commit.

**`could not find file _revisioni.md`.** Ogni cartella in `ricerche/` deve
contenere un file `_revisioni.md`, anche vuoto. «Nuova ricerca» e
«Controlla prima di pubblicare» lo creano da soli.

**L'etichetta Verified non compare.** L'e-mail delle modifiche deve essere
una delle e-mail verificate del tuo account GitHub, e la chiave va caricata
come *Signing Key*. Rilancia `Configura firma.bat` per rivedere i dati.

**Commit dà un errore di firma.** Lo script non ha trovato o non ha potuto
usare la chiave. Rilancia `Configura firma.bat`. Per togliere la firma in
attesa di capire, incolla nel terminale di VS Code
`git config --local commit.gpgsign false` (dice a Git di non firmare in
questo progetto).

**Il lavoro «Marca temporale» è rosso.** I server di OpenTimestamps non
hanno risposto. Il sito è stato pubblicato lo stesso. *Actions → Pubblica
il sito → Run workflow* riprova.

**La Release c'è ma Zenodo non mostra il DOI.** Controlla che
l'interruttore del punto 6 fosse attivo prima della Release. Su Zenodo,
menu del profilo → *GitHub* → nome del repository: lì ci sono gli eventuali
errori.

**Una citazione compare come `[@chiave]` o `?chiave`.** La chiave non
esiste in `fonti/fonti.json` né in `fonti/bibliografia.bib`: controlla in
Zotero la *Citation key* e che l'esportazione automatica sia attiva.

**Le attività o i `.bat` dicono che non trovano Python.** Reinstalla Python
da <https://www.python.org/downloads/windows/> spuntando *Add python.exe
to PATH*, poi chiudi e riapri VS Code.

**Voglio fare Commit senza pubblicare subito.** In `.vscode/settings.json`
cancella la riga `"git.postCommitCommand": "sync"`: Commit tornerà a
registrare soltanto, e per inviare premerai *Sync Changes*.
