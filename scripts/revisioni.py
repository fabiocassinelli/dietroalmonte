#!/usr/bin/env python3
"""Scrive la cronologia delle revisioni di ogni ricerca leggendo la storia di Git.

Lo esegue GitHub Actions prima di costruire il sito: per ogni cartella in
ricerche/ riempie il file `_revisioni.md`, che la ricerca include in fondo
con la riga   {{< include _revisioni.md >}}

Sul tuo computer NON va eseguito: nel repository i file `_revisioni.md`
restano vuoti (devono però esistere, altrimenti Quarto si ferma).
Per una prova locale:  python scripts/revisioni.py --scrivi
(poi annulla le modifiche ai file _revisioni.md prima del commit).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

from comune import cartelle_ricerche, console_utf8, leggi, dividi_qmd, valore_scheda, RADICE

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
        "agosto", "settembre", "ottobre", "novembre", "dicembre"]
REPO = os.environ.get("GITHUB_REPOSITORY", "fabiocassinelli/dietroalmonte")
MAX_RIGHE = 40


def git(*argomenti: str) -> str:
    try:
        return subprocess.run(["git", *argomenti], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", check=True,
                              cwd=RADICE).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def data_estesa(iso: str) -> str:
    try:
        anno, mese, giorno = iso.split("-")
        return f"{int(giorno)} {MESI[int(mese) - 1]} {anno}"
    except (ValueError, IndexError):
        return iso


def nome_breve(cartella) -> str:
    """2026-09-delitto-chilinella-1577 -> delitto-chilinella-1577"""
    return re.sub(r"^\d{4}-\d{2}-", "", cartella.name)


def versioni(cartella) -> list[tuple[str, str]]:
    righe = git("tag", "--list", f"v*-{nome_breve(cartella)}",
                "--format=%(refname:short)%09%(creatordate:short)")
    trovate = []
    for riga in righe.splitlines():
        if "\t" in riga:
            tag, data = riga.split("\t", 1)
            versione = tag[1:].split("-", 1)[0]
            trovate.append((versione, data.strip()))
    return sorted(trovate, key=lambda v: v[1], reverse=True)


def modifiche(cartella) -> list[tuple[str, str, str, str]]:
    percorso = cartella.relative_to(RADICE).as_posix()
    righe = git("log", "--date=short", "--format=%H%x09%ad%x09%G?%x09%s", "--", percorso)
    trovate = []
    for riga in righe.splitlines():
        parti = riga.split("\t", 3)
        if len(parti) == 4:
            trovate.append(tuple(p.strip() for p in parti))
    return trovate


def testo_cronologia(cartella) -> str:
    elenco = modifiche(cartella)
    if not elenco:
        return ""
    scheda, _, _ = dividi_qmd(leggi(cartella / "index.qmd"))
    righe = ["", "## Cronologia delle revisioni {.appendix}", ""]

    corrente = valore_scheda(scheda, "versione")
    depositate = versioni(cartella)
    if depositate:
        for versione, data in depositate:
            righe.append(f"**Versione {versione}** — depositata il {data_estesa(data)}  ")
        righe.append("")
    elif corrente:
        righe += [f"**Versione {corrente}**", ""]

    prima, ultima = elenco[-1], elenco[0]
    quante = "1 modifica registrata" if len(elenco) == 1 else f"{len(elenco)} modifiche registrate"
    righe += [f"Prima stesura registrata il {data_estesa(prima[1])}. "
              f"Ultima modifica il {data_estesa(ultima[1])}. {quante}.", ""]

    righe += ['::: {.callout-note collapse="true" appearance="simple"}',
              "## Tutte le modifiche", "",
              "| Data | Modifica | Firmata | Registrazione |", "|---|---|:-:|---|"]
    for sha, data, firma, messaggio in elenco[:MAX_RIGHE]:
        firmata = "—" if firma in ("N", "") else "sì"
        messaggio = messaggio.replace("|", "\\|").replace("[", "\\[").replace("@", "\\@")
        righe.append(f"| {data_estesa(data)} | {messaggio} | {firmata} | "
                     f"[`{sha[:7]}`](https://github.com/{REPO}/commit/{sha}) |")
    righe.append("")
    if len(elenco) > MAX_RIGHE:
        percorso = cartella.relative_to(RADICE).as_posix()
        righe += [f"Sono mostrate le ultime {MAX_RIGHE}. "
                  f"[Cronologia completa](https://github.com/{REPO}/commits/main/{percorso}).", ""]
    righe += ["Come verificare firme e marche temporali: "
              "vedi il [metodo](../../metodo.qmd).", ":::", ""]
    return "\n".join(righe)


def main() -> None:
    console_utf8()
    scrivere = "--scrivi" in sys.argv or os.environ.get("GITHUB_ACTIONS") == "true"
    for cartella in cartelle_ricerche():
        if not (cartella / "index.qmd").exists():
            continue
        destinazione = cartella / "_revisioni.md"
        if not scrivere:
            if not destinazione.exists():
                destinazione.write_text("", encoding="utf-8")
                print(f"creato il file vuoto mancante: {destinazione.relative_to(RADICE)}")
            continue
        with open(destinazione, "w", encoding="utf-8", newline="\n") as f:
            f.write(testo_cronologia(cartella))
        print(f"cronologia scritta: {cartella.name}")
    if not scrivere:
        print("Niente da fare sul computer: la cronologia la scrive GitHub Actions.")


if __name__ == "__main__":
    main()
