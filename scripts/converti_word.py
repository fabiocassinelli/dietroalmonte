#!/usr/bin/env python3
"""Converte la bozza Word di una ricerca (bozza.docx) nel suo index.qmd.

Che cosa fa:
  - legge `bozza.docx` nella cartella della ricerca;
  - sostituisce SOLO il testo di `index.qmd`: la scheda in alto fra i `---`
    e la coda (da `<!-- CODA` in giù) restano come sono;
  - Titolo 1 / Titolo 2 di Word diventano sezioni e sottosezioni;
  - le note a piè di pagina restano note; le immagini inserite nel testo
    vengono salvate in `immagini/` con il nome `bozza-01.png`, ...;
  - prima di scrivere salva sempre una copia in `_copie-di-sicurezza/`;
    se `index.qmd` è stato corretto a mano dopo l'ultima conversione,
    si ferma e chiede conferma.

Uso (di norma non serve digitarlo: c'è il file «Converti bozza Word.bat»
e l'attività di VS Code «Word → converti la bozza»):

    python scripts/converti_word.py                 cerca da solo le bozze
    python scripts/converti_word.py CARTELLA        una ricerca precisa
    python scripts/converti_word.py --si            non chiede conferme
"""

from __future__ import annotations

import datetime as dt
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

from comune import (CODA_STANDARD, MODELLI, RADICE, SEGNO_CODA, attendi_invio,
                    cartelle_ricerche, console_utf8, dividi_qmd, esci, esegui,
                    impronta, impronta_file, leggi, normalizza, scrivi, trova_quarto)

NOME_BOZZA = "bozza.docx"
NOME_STATO = ".bozza.json"
FORMATO_USCITA = ("markdown-smart-simple_tables-multiline_tables-grid_tables"
                  "+pipe_tables-raw_attribute")
IMMAGINI_WEB = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
PESO_MASSIMO_MB = 1.5


# ── scelta della ricerca ────────────────────────────────────────────

def stato_di(cartella: Path) -> dict:
    try:
        return json.loads((cartella / NOME_STATO).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def bozza_cambiata(cartella: Path) -> bool:
    return stato_di(cartella).get("bozza_sha256") != impronta_file(cartella / NOME_BOZZA)


def cartella_da_argomento(argomento: str) -> Path:
    p = Path(argomento).expanduser()
    if not p.is_absolute():
        p = (Path.cwd() / p)
    p = p.resolve()
    if p.is_file():
        p = p.parent
    if not (p / NOME_BOZZA).is_file():
        esci(f"nella cartella\n  {p}\nnon c'è il file {NOME_BOZZA}. "
             f"Salva lì la bozza di Word con questo nome esatto.")
    return p


def scegli_cartelle(argomenti: list[str], senza_domande: bool) -> list[Path]:
    if argomenti:
        return [cartella_da_argomento(a) for a in argomenti]
    con_bozza = [c for c in cartelle_ricerche() if (c / NOME_BOZZA).is_file()]
    if not con_bozza:
        esci(f"non trovo nessun file {NOME_BOZZA} dentro le cartelle di ricerche/.\n"
             f"Salva la bozza di Word con questo nome nella cartella della ricerca, "
             f"accanto a index.qmd.")
    cambiate = [c for c in con_bozza if bozza_cambiata(c)]
    if len(cambiate) == 1:
        return cambiate
    if not cambiate:
        if len(con_bozza) == 1:
            print(f"La bozza di {con_bozza[0].name} non è cambiata dall'ultima "
                  f"conversione: la riconverto comunque.")
            return con_bozza
        print("Nessuna bozza è cambiata dall'ultima conversione.")
        candidate = con_bozza
    else:
        candidate = cambiate
    if senza_domande or not sys.stdin.isatty():
        return candidate
    print("\nQuale bozza vuoi convertire?")
    for n, c in enumerate(candidate, 1):
        print(f"  {n}. {c.name}")
    print("  0. tutte")
    risposta = input("Scrivi il numero e premi Invio: ").strip()
    if risposta == "0":
        return candidate
    try:
        return [candidate[int(risposta) - 1]]
    except (ValueError, IndexError):
        esci("numero non valido: non ho convertito nulla.")
    return []


# ── conversione ─────────────────────────────────────────────────────

def pandoc_docx(bozza: Path, lavoro: Path) -> str:
    quarto = trova_quarto()
    comando = [quarto, "pandoc", str(bozza),
               "--from=docx+styles",
               f"--to={FORMATO_USCITA}",
               "--wrap=none",
               "--markdown-headings=atx",
               "--reference-location=block",
               "--shift-heading-level-by=1",
               "--extract-media=.",
               f"--lua-filter={RADICE / 'scripts' / 'word.lua'}"]
    esito = esegui(comando, cwd=lavoro)
    if esito.returncode != 0:
        esci("la conversione del file Word non è riuscita.\n"
             "Controlla che il file sia chiuso in Word e che sia un vero .docx.\n\n"
             + (esito.stderr or esito.stdout).strip())
    return esito.stdout.replace("\r\n", "\n")


def numero_naturale(nome: str) -> list:
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", nome)]


def immagini_estratte(lavoro: Path) -> list[tuple[Path, str]]:
    """Le immagini che Pandoc ha tolto dal file Word, con il nuovo nome."""
    media = lavoro / "media"
    if not media.is_dir():
        return []
    estratte = sorted((p for p in media.rglob("*") if p.is_file()),
                      key=lambda p: numero_naturale(p.name))
    return [(p, f"bozza-{n:02d}{p.suffix.lower()}") for n, p in enumerate(estratte, 1)]


def correggi_percorsi(testo: str, lavoro: Path, estratte: list[tuple[Path, str]]) -> str:
    for origine, nuovo in estratte:
        relativo = origine.relative_to(lavoro).as_posix()
        for vecchio in (f"./{relativo}", relativo):
            testo = testo.replace(f"]({vecchio})", f"](immagini/{nuovo})")
            testo = testo.replace(f'src="{vecchio}"', f'src="immagini/{nuovo}"')
    return testo


def copia_immagini(estratte: list[tuple[Path, str]], cartella: Path) -> list[str]:
    """Mette le immagini in immagini/ (sostituendo quelle della conversione
    precedente, che si chiamano bozza-NN) e restituisce gli avvisi."""
    avvisi: list[str] = []
    destinazione = cartella / "immagini"
    destinazione.mkdir(exist_ok=True)
    for vecchia in destinazione.glob("bozza-[0-9][0-9]*"):
        if vecchia.is_file():
            vecchia.unlink()
    for origine, nuovo in estratte:
        shutil.copyfile(origine, destinazione / nuovo)
        estensione = origine.suffix.lower()
        if estensione not in IMMAGINI_WEB:
            avvisi.append(f"immagini/{nuovo}: il formato {estensione} non si vede nei "
                          f"browser. In Word sostituisci l'immagine con un JPG o PNG.")
        peso = origine.stat().st_size / 1e6
        if peso > PESO_MASSIMO_MB:
            avvisi.append(f"immagini/{nuovo} pesa {peso:.1f} MB: rallenta la pagina. "
                          f"Riducila (1600 px sul lato lungo bastano) e reinseriscila in Word.")
    return avvisi


def ripristina_citazioni(testo: str) -> str:
    """Le citazioni scritte a mano in Word, tipo [@chiave, doc. 47],
    tornano citazioni vere (Pandoc le aveva protette con le barre)."""
    def pulisci(m: re.Match) -> str:
        interno = m.group(1)
        interno = re.sub(r"\\([\[\]@_*.\-()])", r"\1", interno)
        return "[" + interno + "]"
    return re.sub(r"\\\[((?:-?\\?@|[^\]\n]*?;\s*-?\\?@|[^\]\n@]*?\\?@)[^\n]*?)\\\]",
                  pulisci, testo)


def conta(testo: str) -> dict:
    return {
        "sezioni": len(re.findall(r"^##\s", testo, re.M)) - len(re.findall(r"^:::+\s*\{\.callout-note", testo, re.M)),
        "sottosezioni": len(re.findall(r"^###\s", testo, re.M)),
        "note": len(re.findall(r"^\[\^\d+\]:", testo, re.M)),
        "immagini": len(re.findall(r"!\[", testo)),
        "citazioni": len(re.findall(r"\[-?@|;\s*-?@", testo)),
        "riquadri": len(re.findall(r"^:::+\s*\{\.callout-note", testo, re.M)),
    }


def converti(cartella: Path, senza_domande: bool) -> bool:
    bozza = cartella / NOME_BOZZA
    qmd = cartella / "index.qmd"
    relativa = cartella.relative_to(RADICE).as_posix() if RADICE in cartella.parents else str(cartella)
    print(f"\n── {relativa} " + "─" * max(3, 60 - len(relativa)))

    if (cartella / ("~$" + NOME_BOZZA)).exists():
        print("ATTENZIONE: la bozza sembra aperta in Word. Salvala (Ctrl+S) prima di "
              "convertire, altrimenti leggo la versione precedente.")

    # 1. il file di arrivo: la scheda e la coda non si toccano
    if qmd.exists():
        originale = leggi(qmd)
    else:
        originale = leggi(MODELLI / "nuova-ricerca.qmd")
        oggi = dt.date.today().isoformat()
        originale = originale.replace("DATA", oggi, 1).replace("CARTELLA", cartella.name)
        print("index.qmd non esisteva: lo creo dal modello. Ricorda di compilare la scheda in alto.")
    scheda, corpo_vecchio, coda = dividi_qmd(originale)
    if not scheda:
        esci(f"{relativa}/index.qmd non comincia con la scheda fra i '---'. "
             f"Rimettila (copiala da _modelli/nuova-ricerca.qmd) e riprova.")
    if not coda:
        coda = CODA_STANDARD
    if "_revisioni.md" not in coda:
        coda = coda.rstrip("\n") + "\n\n{{< include _revisioni.md >}}\n"

    # 2. conversione in una cartella di lavoro temporanea
    with tempfile.TemporaryDirectory(prefix="dam-word-") as tmp:
        lavoro = Path(tmp)
        corpo = pandoc_docx(bozza, lavoro)
        estratte = immagini_estratte(lavoro)
        corpo = correggi_percorsi(corpo, lavoro, estratte)
        corpo = ripristina_citazioni(corpo)
        corpo = re.sub(r"^(\[\^\d+\]:) +", r"\1 ", corpo, flags=re.M)
        if SEGNO_CODA in corpo:
            esci("nel testo di Word compare la scritta '<!-- CODA': toglila dalla bozza.")
        nuovo_corpo = "\n" + corpo.strip("\n") + "\n\n"
        nuovo = scheda + nuovo_corpo + coda

        # 3. protezione del lavoro fatto a mano
        stato = stato_di(cartella)
        vecchio_norm = normalizza(corpo_vecchio)
        mai_convertita = "corpo_sha256" not in stato
        modificato_a_mano = (not mai_convertita
                             and stato.get("corpo_sha256") != impronta(vecchio_norm))
        da_proteggere = bool(vecchio_norm) and qmd.exists() and (mai_convertita or modificato_a_mano)

        if qmd.exists() and nuovo == originale:
            print("Il testo convertito è identico a quello già presente: nessuna modifica.")
            copia_immagini(estratte, cartella)
            salva_stato(cartella, bozza, nuovo_corpo)
            return True

        if da_proteggere:
            print()
            if modificato_a_mano:
                print("ATTENZIONE: index.qmd è stato corretto a mano dopo l'ultima conversione.")
                print("Se continuo, quelle correzioni vengono sostituite dal testo di Word.")
            else:
                print("ATTENZIONE: index.qmd contiene già del testo che non viene da Word.")
                print("Se continuo, quel testo viene sostituito dal testo di Word.")
            print("(La scheda in alto fra i --- e la coda in fondo restano comunque intatte,")
            print(" e salvo in ogni caso una copia di sicurezza.)")
            if not senza_domande:
                if not sys.stdin.isatty():
                    print("\nNon posso chiedere conferma da qui: non ho modificato nulla.")
                    return False
                risposta = input("\nScrivi SI e premi Invio per continuare, "
                                 "oppure solo Invio per lasciare tutto com'è: ")
                if risposta.strip().lower() not in ("si", "sì", "s"):
                    print("Va bene: non ho modificato nulla.")
                    return False

        # 4. copia di sicurezza, poi scrittura
        if qmd.exists():
            copie = cartella / "_copie-di-sicurezza"
            copie.mkdir(exist_ok=True)
            adesso = dt.datetime.now().strftime("%Y-%m-%d-%H%M%S")
            copia = copie / f"index-{adesso}.qmd"
            shutil.copyfile(qmd, copia)
            print(f"Copia di sicurezza: {copia.relative_to(cartella).as_posix()}")

        avvisi = copia_immagini(estratte, cartella)
        immagini = [nuovo_nome for _, nuovo_nome in estratte]
        scrivi(qmd, nuovo)

    revisioni = cartella / "_revisioni.md"
    if not revisioni.exists():
        revisioni.write_text("", encoding="utf-8")
    salva_stato(cartella, bozza, nuovo_corpo)

    c = conta(nuovo_corpo)
    print(f"Fatto: index.qmd aggiornato "
          f"({c['sezioni']} sezioni, {c['sottosezioni']} sottosezioni, {c['note']} note, "
          f"{c['immagini']} immagini, {c['citazioni']} citazioni, {c['riquadri']} riquadri).")
    if immagini:
        print(f"Immagini salvate in immagini/: {', '.join(immagini)}")
    for avviso in avvisi:
        print("AVVISO: " + avviso)
    return True


def salva_stato(cartella: Path, bozza: Path, corpo: str) -> None:
    stato = {
        "nota": "File scritto dalla conversione da Word: non modificarlo a mano.",
        "bozza_sha256": impronta_file(bozza),
        "corpo_sha256": impronta(normalizza(corpo)),
        "convertita_il": dt.datetime.now().isoformat(timespec="seconds"),
    }
    scrivi(cartella / NOME_STATO, json.dumps(stato, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    console_utf8()
    argomenti = [a for a in sys.argv[1:] if not a.startswith("--")]
    senza_domande = "--si" in sys.argv
    try:
        cartelle = scegli_cartelle(argomenti, senza_domande)
        riuscite = [converti(c, senza_domande) for c in cartelle]
        if any(riuscite):
            print("\nOra apri index.qmd in VS Code e guarda l'anteprima (Ctrl+Shift+K).")
    finally:
        attendi_invio()


if __name__ == "__main__":
    main()
