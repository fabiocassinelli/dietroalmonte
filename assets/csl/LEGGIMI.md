# Stile citazionale

`appennino-archivistico.csl` è lo stile in uso, scritto su misura per
questo sito. È già nel repository: non serve scaricare nulla.

## Che cosa fa

Note a piè di pagina nella forma archivistica italiana, istituto per primo:

    ASGe, Notai Antichi, 1123, notaio Antonio da Cogorno, doc. 47 (1432 aprile 12).

Alla seconda citazione della stessa unità la forma si accorcia:

    ASGe, Notai Antichi, 1123, docc. 51 e 63.

Alla ripetizione immediata: `Ibid.`

Nell'elenco delle fonti, in fondo alla pagina, l'istituto compare per
esteso con tipologia ed estremi:

    Archivio di Stato di Genova, Notai Antichi, 1123, notaio Antonio da
    Cogorno. Registro notarile, 1428. Estremi 1428-1441. Danni da umidità
    sui margini esterni.

Per le opere a stampa usa la forma italiana corrente: autore, titolo,
luogo, editore, anno; alla seconda citazione autore, titolo breve, *cit.*

## Mappatura dei campi

| Campo CSL | Contenuto | Esempio | Campo in Zotero |
|---|---|---|---|
| `archive` | sigla dell'istituto | ASGe | Archivio |
| `publisher` | nome per esteso | Archivio di Stato di Genova | Extra: `publisher: ...` |
| `title` | fondo o serie | Notai Antichi | Titolo |
| `call-number` | unità (filza, registro, busta) | 1123 | Segnatura |
| `archive_location` | intitolazione dell'unità | notaio Antonio da Cogorno | Collocazione nell'archivio |
| `genre` | tipologia | Registro notarile | Tipo |
| `issued` | anno iniziale | 1428 | Data |
| `note` | estremi, lacune, stato | Estremi 1428-1441 | Note (campo Extra) |

Il singolo documento **non** è una voce bibliografica: si indica nel
suffisso della citazione.

    [@ASGe_NA_1123, doc. 47 (1432 aprile 12)]
    [@ASGe_NA_1123, cc. 88v-89r]

## Modificarlo

È un file XML leggibile. Le macro `archivio-nota`,
`archivio-nota-breve` e `archivio-bibliografia` controllano l'ordine e
la punteggiatura delle citazioni d'archivio: cambia l'ordine dei
`<text variable="..."/>` dentro il `<group>` e hai una forma diversa.

## Alternative

Se preferisci uno stile internazionale già pronto:

    make csl        # scarica chicago-notes-bibliography.csl

poi cambia la chiave `csl:` in `_quarto.yml`. Perderai la forma
archivistica italiana: Chicago mette il titolo per primo e l'archivio
in coda.
