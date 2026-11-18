#!/usr/bin/env python3
"""Apre il cantiere di una nuova ricerca.

Crea la cartella  ricerche/AAAA-MM-nome-breve/  con:
  index.qmd       la ricerca, già con la scheda in alto (segnata come bozza)
  bozza.docx      la bozza di Word con gli stili giusti
  _revisioni.md   file vuoto che deve esistere (lo riempie GitHub)
  immagini/ dati/

Uso: doppio clic su «Nuova ricerca.bat», oppure in VS Code
Terminale → Esegui attività → «Nuova ricerca».
"""

from __future__ import annotations

import datetime as dt
import json
import re
import shutil
import sys
import unicodedata

from comune import (MODELLI, RADICE, RICERCHE, attendi_invio, console_utf8, dividi_qmd, esci,
                    impronta, leggi, normalizza, scrivi)


def nome_breve(titolo: str) -> str:
    semplice = unicodedata.normalize("NFKD", titolo).encode("ascii", "ignore").decode()
    semplice = re.sub(r"[^a-zA-Z0-9]+", "-", semplice).strip("-").lower()
    parole = [p for p in semplice.split("-") if p not in
              ("il", "lo", "la", "i", "gli", "le", "un", "una", "di", "del", "della",
               "dei", "degli", "delle", "a", "da", "in", "e", "per", "con", "su")]
    return "-".join(parole)[:48].strip("-")


def main() -> None:
    console_utf8()
    argomenti = [a for a in sys.argv[1:] if not a.startswith("--")]
    try:
        titolo = " ".join(argomenti).strip()
        if not titolo:
            titolo = input("Titolo della nuova ricerca (lo potrai cambiare): ").strip()
        if not titolo:
            esci("serve un titolo, anche provvisorio.")
        breve = nome_breve(titolo)
        if not breve:
            esci("dal titolo non riesco a ricavare un nome di cartella: usa lettere o numeri.")
        oggi = dt.date.today()
        cartella = RICERCHE / f"{oggi:%Y-%m}-{breve}"
        if cartella.exists():
            esci(f"esiste già la cartella {cartella.relative_to(RADICE).as_posix()}")

        (cartella / "immagini").mkdir(parents=True)
        (cartella / "dati").mkdir()
        (cartella / "immagini" / ".gitkeep").write_text("", encoding="utf-8")
        (cartella / "dati" / ".gitkeep").write_text("", encoding="utf-8")
        (cartella / "_revisioni.md").write_text("", encoding="utf-8")

        testo = leggi(MODELLI / "nuova-ricerca.qmd")
        titolo_yaml = titolo.replace("\\", "\\\\").replace('"', '\\"')
        testo = testo.replace('title: "TITOLO"', f'title: "{titolo_yaml}"', 1)
        testo = testo.replace("date: DATA", f"date: {oggi.isoformat()}", 1)
        testo = testo.replace("CARTELLA", cartella.name)
        scrivi(cartella / "index.qmd", testo)
        # Segno che il testo attuale è solo il modello: la prima conversione
        # da Word potrà sostituirlo senza chiedere conferma.
        _, corpo, _ = dividi_qmd(testo)
        scrivi(cartella / ".bozza.json", json.dumps(
            {"nota": "File scritto dalla conversione da Word: non modificarlo a mano.",
             "corpo_sha256": impronta(normalizza(corpo))}, indent=2, ensure_ascii=False) + "\n")

        modello = MODELLI / "bozza-modello.docx"
        if modello.exists():
            shutil.copyfile(modello, cartella / "bozza.docx")

        relativa = cartella.relative_to(RADICE).as_posix()
        print(f"\nCantiere aperto: {relativa}/")
        print("  index.qmd   compila la scheda in alto (sottotitolo, categorie, abstract)")
        print("  bozza.docx  se preferisci scrivere in Word, scrivi qui e poi converti")
        print("\nLa ricerca è segnata come bozza (draft: true): finché non togli quella")
        print("riga non compare sul sito, nemmeno dopo Commit e Sync.")
    finally:
        attendi_invio()


if __name__ == "__main__":
    main()
