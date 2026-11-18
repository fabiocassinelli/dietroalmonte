# Come scrivere e pubblicare una ricerca

**Per cominciare:** doppio clic su `Nuova ricerca.bat`, scrivi il titolo. Nasce la cartella `ricerche/AAAA-MM-nome/` con `index.qmd` (la ricerca) e `bozza.docx` (la bozza di Word). In cima a `index.qmd`, fra i due `---`, c'è la **scheda**: titolo, sottotitolo, data, categorie, abstract. Si compila sempre lì, mai in Word.

## Strada A — scrivo in Word

1. Scrivi in `bozza.docx`, nella cartella della ricerca, usando gli stili:

   | In Word | Sul sito |
   |---|---|
   | stile **Titolo 1** / **Titolo 2** | sezione / sottosezione |
   | *Riferimenti → Inserisci nota a piè di pagina* | nota |
   | *Inserisci → Immagini*, su una riga a sé | immagine, salvata in `immagini/` |
   | stile **Didascalia**, sotto l'immagine | didascalia |
   | stile **Regesto** (il primo paragrafo fa da titolo) | riquadro richiudibile |
   | stile **Nota a margine** | nota a margine |

2. Salva (`Ctrl+S`) e fai doppio clic su **`Converti bozza Word.bat`** (in VS Code: *Terminale → Esegui attività → Word → converti la bozza*).
3. Il testo entra in `index.qmd`. La scheda in alto e la coda in fondo (dalla riga `<!-- CODA`) non vengono toccate.

**Protezione.** Prima di scrivere, la conversione salva sempre una copia in `_copie-di-sicurezza/`. Se hai corretto `index.qmd` a mano dopo l'ultima conversione, si ferma e chiede conferma. Regola pratica: finché scrivi in Word, correggi in Word; quando passi al `.qmd`, non riconvertire più.

## Strada B — scrivo direttamente in `index.qmd`

Apri il file in VS Code e scrivi sotto la scheda. Una riga vuota separa i paragrafi; `## Titolo` apre una sezione, `### Titolo` una sottosezione; `*corsivo*`, `**grassetto**`.

## La sintassi essenziale

Vale nel `.qmd`. Le citazioni fra parentesi quadre funzionano anche scritte in Word.

**Citazione archivistica** — diventa da sola una nota nella forma «ASGe, *Notai Antichi*, 1123, notaio X, doc. 47 (1432 aprile 12)»; alla seconda citazione si accorcia, alla ripetizione diventa «Ibid.». La chiave è quella di Zotero; dopo la virgola, il documento:

```markdown
Il pascolo va al primogenito.[@ASGe_NA_1123, doc. 47 (1432 aprile 12)]
```

**Nota scritta a mano:**

```markdown
Il pascolo va al primogenito.[^1]

[^1]: Il testo della nota, che può contenere una citazione [@ASGe_NA_1123, c. 12r].
```

**Immagine** (il file va in `immagini/`; la segnatura va nella didascalia):

```markdown
![ASGe, Notai Antichi, 1123, c. 88v. Fotografia dell'autore.](immagini/c088v.jpg)
```

**Regesto e trascrizione** (riquadro chiuso, si apre con un clic):

```markdown
::: {.callout-note collapse="true" appearance="simple" class="trascrizione"}
## Regesto e trascrizione — ASGe, NA 1123, doc. 47

**1432 aprile 12, Varese.** *Regesto.* ...

> In nomine Domini amen...
:::
```

**Nota a margine:**

```markdown
::: {.column-margin}
Testo che compare a fianco, nel margine.
:::
```

**Promemoria per me** (si vede solo in anteprima, sul sito viene tolto):

```markdown
::: {.da-completare}
## DA COMPLETARE — che cosa manca
:::
```

## Controllare e pubblicare, da VS Code

1. **Anteprima:** con `index.qmd` aperto premi `Ctrl+Shift+K`.
2. **Pubblicare:** pannello *Source Control* (`Ctrl+Shift+G`) → scrivi che cosa hai fatto → **Commit**. Il resto lo fa GitHub in due o tre minuti: sito, cronologia delle revisioni, marca temporale.
3. **Bozza o pubblica?** Finché nella scheda c'è `draft: true` la ricerca non compare sul sito, anche se fai Commit. Cancella la riga quando è pronta.
4. **Versione citabile:** nella scheda scrivi `versione: "1.0"` → Commit. GitHub crea PDF e Release, Zenodo assegna il DOI: copialo nella riga `doi:` → Commit. Per una revisione: `versione: "1.1"`.

Dubbi su che cosa manca? Doppio clic su `Controlla prima di pubblicare.bat`.
